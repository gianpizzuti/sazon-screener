# Sazón Screener

A conversational agent that screens delivery-driver applicants for **Grupo Sazón** (45 restaurants in Spain and Mexico, ~1000 applications/week), and a recruiter tool to act on the results.

The client has two different problems, and the design addresses each one separately:

| Problem | Mechanism |
|---|---|
| 60% of candidates don't answer recruiter calls | Asynchronous chat, first message seconds after applying, candidate answers when it suits them |
| 80% of recruiter time goes to unqualified candidates | Knock-out questions first; recruiters only receive qualified (or flagged) candidates with a summary |

📄 **[Process design](docs/process-design.md)** (Phase 1) · 🧭 **[Decision log](docs/decisions/decision-log.md)** (every choice and its trade-off) · **[ADRs](docs/decisions/README.md)** (deep-dives) · 🔬 **[Live testing log](docs/live-testing-log.md)** (what real conversations broke, and the fixes) · 💬 **[Sample conversations](samples/README.md)**

---

## Quick start

Requirements: Python 3.11+, an Anthropic API key.

```bash
make install                 # creates .venv and installs the package
cp .env.example .env         # then set ANTHROPIC_API_KEY in .env
make run                     # API (localhost:8000/docs) + recruiter dashboard (localhost:8501)
make test                    # 106 tests, offline, no API key needed
```

Optional:

```bash
make seed                    # fill the dashboard with 15 demo candidates (real models, ~1.5 USD in total)
make chat                    # talk to the agent in the terminal (/data shows what was collected)
make samples                 # export finished conversations to samples/*.md
```

## What's inside

| | |
|---|---|
| **The agent (Sofía)** | Screens in Spanish (Spain or Mexico vocabulary) or English, switches when the candidate does, accepts several answers in one message, answers questions from the client's FAQ, handles corrections, ambiguity, frustration, opt-outs and manipulation attempts |
| **Recruiter dashboard** | **Pipeline** (queue ordered by what to do first) · **Candidate** (AI summary, extracted data with the candidate's own words, full transcript with the *why* of every message, recruiter decision and override, JSON export, GDPR erasure) · **Analytics** (completion, funnel, knock-out reasons, drop-off, frustration by question, FAQ gaps, AI health) · **Try the agent** (play the candidate in the web chat) |
| **API** | `/conversations` for channels (web, WhatsApp, voice), `/candidates` + `/analytics` for recruiters and an ATS. OpenAPI docs at `/docs` |

## How it works

```
candidate message
      │
      ▼
 1. UNDERSTAND   Claude Haiku 5.5, structured output → TurnAnalysis
                 values + verbatim evidence, intents, language, sentiment, FAQ match
      │
      ▼
 2. DECIDE       ScreeningPolicy, pure Python (no LLM)
                 grounding check → validation → knock-outs → next question → audit events
      │
      ▼
 3. SPEAK        Claude Sonnet 5.5 writes ONE message from the policy's Directive
      │          (greeting and recap are fixed templates)
      ▼
 4. GUARD        length / markdown / leaked-instruction checks → retry once → template fallback
      │
      ▼
 5. PERSIST      state + transcript + events in one transaction (SQLite)

 after the conversation: recruiter summary with Claude Opus 5.5 (off the hot path)
```

**The LLM never decides eligibility.** It reads and it writes. Knock-outs, validation, question order and loop prevention are deterministic code with unit tests ([ADR 0001](docs/decisions/0001-code-decides-llm-understands.md)).

```
 candidate (web chat · WhatsApp · voice)          recruiter (dashboard · ATS)
                 │                                         │
         /conversations                     /candidates · /analytics
                 └──────────────► FastAPI ◄─────────────────┘
                                     │
                      ScreeningEngine (pipeline above)
                                     │
             SQLite: conversations · messages · events · reviews
```

The recruiter dashboard only talks to the API, like any other client ([ADR 0008](docs/decisions/0008-api-first-recruiter-tool.md)). What the bot decided and what a recruiter decided are stored separately; every override is audited.

### Repository layout

```
config/clients/grupo_sazon/   everything client-specific: service areas, FAQ, copy, models, thresholds
src/screener/
  domain/      models (ScreeningData, ConversationState), validators, location matching, grounding
  engine/      policy (the rules), engine (the turn pipeline), directive (policy → writer contract), recap
  llm/         provider-agnostic interfaces, Claude implementations, prompts, template responder
  storage/     SQLAlchemy repository: conversations, messages, events, reviews
  api/         FastAPI app: channel and recruiter endpoints
  views.py     read models for recruiters (queue row, candidate detail)
  analytics.py funnel, drop-off, knock-outs, frustration, FAQ gaps, AI health
  channels/    terminal chat
dashboard/     Streamlit recruiter tool (an API client)
scripts/       run (API + dashboard), seed demo data, export samples
samples/       real conversations with highlights, transcript, data and summary
tests/         policy, engine, API, validators, locations (offline, deterministic)
docs/          process design, decision log, ADRs, live testing log
```

## Key design decisions

| Decision | Why (short) | ADR |
|---|---|---|
| Code decides, LLM understands and speaks | Auditable, injection-proof, testable; required for high-risk AI in recruitment | [0001](docs/decisions/0001-code-decides-llm-understands.md) |
| One model per task | Hot path optimised for latency, off-path for quality; cost is not the deciding factor at this volume | [0002](docs/decisions/0002-llm-per-task.md) |
| Client = configuration | New zones, FAQ or wording without a deploy; next client = new folder | [0003](docs/decisions/0003-config-driven-client.md) |
| SQLite + event log | Zero setup for evaluators, real queries, an audit trail; Postgres is one URL away | [0004](docs/decisions/0004-sqlite-sqlalchemy.md) |
| Grounded extraction | Structured output guarantees shape, not truth: every value must quote the candidate | [0005](docs/decisions/0005-grounding-and-layered-validation.md) |
| Templates for recap and fallback | Data shown back to the candidate is never paraphrased; the conversation never breaks | [0006](docs/decisions/0006-templates-where-precision-matters.md) |
| FAQ without a vector DB | 13 entries don't need retrieval infrastructure; the writer only sees the one approved answer | [0007](docs/decisions/0007-faq-without-vector-db.md) |
| API-first, Streamlit as a client | Logic in one place, ready for WhatsApp/voice/ATS; the UI can be replaced without touching the core | [0008](docs/decisions/0008-api-first-recruiter-tool.md) |

## Structured output

Every conversation produces a `ScreeningData` record (plus per-field status, flags and the full audit trail):

```json
{
  "full_name": "Ana López",
  "has_drivers_license": true,
  "license_status": "yes",
  "city_id": "madrid",
  "city": "Madrid",
  "country": "ES",
  "zone": "Chamberí",
  "in_service_area": true,
  "availability": ["part_time", "weekends"],
  "preferred_schedule": ["evening"],
  "experience_years": 2.0,
  "experience_months": 24,
  "experience_platforms": ["Glovo", "Uber Eats"],
  "start_date": "2026-10-26",
  "start_date_raw": "el lunes"
}
```
