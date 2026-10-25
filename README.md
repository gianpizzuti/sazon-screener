# Sazón Screener

A conversational agent that screens delivery-driver applicants for **Grupo Sazón** (45 restaurants in Spain and Mexico, ~1000 applications/week), and a recruiter tool to act on the results.

The client has two different problems, and the design addresses each one separately:

| Problem | Mechanism |
|---|---|
| 60% of candidates don't answer recruiter calls | Asynchronous chat, first message seconds after applying, candidate answers when it suits them |
| 80% of recruiter time goes to unqualified candidates | Knock-out questions first; recruiters only receive qualified (or flagged) candidates with a summary |

📄 **[Process design](docs/process-design.md)** (Phase 1, two pages, with an [appendix](docs/process-design-appendix.md)) · 🧭 **[Decision log](docs/decisions/decision-log.md)** (every choice and its trade-off) · **[ADRs](docs/decisions/README.md)** (deep-dives) · 🔬 **[Live testing log](docs/live-testing-log.md)** (what real conversations broke, and the fixes) · 📊 **[Evals](evals/README.md)** (what the models get right, measured, and what that changed) · 💬 **[Sample conversations](samples/README.md)**

🏗️ Design (not built yet): **[ATS integration](docs/design/ats-integration.md)** with its **[API spec](docs/design/ats-api.yaml)** (OpenAPI 3.1) · **[Deployment and scaling](docs/design/deployment-and-scaling.md)** (from one process to 10,000 applications/week) · **[Licences issued abroad](docs/design/foreign-licences.md)** (research behind the rules, with sources)

---

## Quick start

Requirements: Python 3.11+, Node 18+ (for the web app), an Anthropic API key.

```bash
make install                 # Python package + builds the web app
cp .env.example .env         # then set ANTHROPIC_API_KEY in .env
make run                     # recruiter web app + API on http://localhost:8000 (API docs at /docs)
                             # the first start downloads the embedding model (≈ 240 MB, once) into data/models
make test                    # offline, no API key: 222 tests of the product + 254 checks of the eval datasets
```

Optional:

```bash
make seed                    # fill the app with 15 demo candidates (real models, ~1.5 USD in total)
make chat                    # talk to the agent in the terminal (/data shows what was collected)
make samples                 # export finished conversations to samples/*.md
make reset-demo              # wipe the local database and re-seed (deletes your local test conversations)
make web-dev                 # web app with hot reload on :5173 (with `make run` for the API)
make eval-extraction         # extraction eval on the production model (real API, ~0.03 USD)
make eval-conversations      # 13 simulated candidates + LLM judge (real API, ~1 USD)
make eval-retrieval          # knowledge-base retrieval: local models ($0) + Haiku's choice (real API, ~0.32 USD)
```

## What's inside

| | |
|---|---|
| **The agent (Sofía)** | Screens in Spanish (Spain or Mexico vocabulary) or English, switches when the candidate does, accepts several answers in one message, answers questions from the client's FAQ, handles corrections, ambiguity, frustration, opt-outs and manipulation attempts. A licence issued abroad is judged by the law of the country they'd work in (EU: valid; 33 countries with an exchange agreement: qualified with a note; others: a person decides), and Sofía never asks where it is from. **Qualified candidates book their interview in the chat**: three free times as buttons, no double booking, moved by writing again |
| **Knowledge base (RAG)** | Candidates' questions are answered from the client's knowledge base ([`faq.yaml`](config/clients/grupo_sazon/faq.yaml)): 30 topics such as pay, tips, payday, contract, fuel, parking, shifts, insurance, work permit or a foreign licence, plus **zones** and **interview times built live from the configuration**. **Retrieve**: a multilingual embedding model, run locally, finds the 5 closest topics (98% recall@5 on held-out questions, 4 ms, $0). **Augment**: the understanding model picks the topic whose approved answer answers the question, or none, and code inserts that single answer. **Generate**: Sofía phrases only that, or says "the team will confirm"; unanswered questions are logged for recruiters. Measured: 0 wrong topics in 254 runs; hybrid keyword search was tried and measured worse ([ADR 0010](docs/decisions/0010-knowledge-base-retrieval.md)). No knowledge base came with the assignment, so this one is illustrative, to validate with the client |
| **Voice agent** | "Try the agent" → **Voice**: talk to Sofía hands-free, through the same API and engine as the chat. The browser transcribes the candidate; Sofía speaks with **ElevenLabs** voices chosen per country (Spain, Mexico, English), writes spoken-style sentences, and dates, times and options are read naturally. Without an ElevenLabs key the browser's own voice is used. [ADR 0011](docs/decisions/0011-voice-channel.md) |
| **Re-engagement** | Silent candidates get up to 3 reminders (+2 h, +24 h, +72 h), never at night in *their* timezone, as fixed templates (WhatsApp's 24-hour rule) that repeat the pending question. Any reply resumes the screening. The **recovery rate** shows whether it works. In the web app, the **demo clock** (top bar) moves time forward to show it live |
| **Recruiter web app** (React) | **Pipeline**: queue ordered by what to do first, status filters, live counters. **Candidate**: AI summary, extracted data with the candidate's own words, chat transcript with the *why* behind every message, recruiter decision and audited override, audit timeline, JSON export, GDPR erasure. **Analytics**: funnel and charts that grow as you scroll, recovery-rate meter, FAQ gaps, AI health, table view. **Try the agent**: play the candidate and watch the screening checklist fill in live. **How it works**: the screening flow as an interactive flowchart (click a step for the exact question and rules, or trace a candidate's path) plus the workspace's live configuration. Light and dark theme, reduced-motion aware |
| **Evals** | **Extraction**: 126 hand-labelled messages scored field by field, Haiku vs Sonnet vs Opus (Haiku: 124/126 messages and 158/158 values right, 1 invented value, location 22/22 after the rules, ≈ $0.25 per 1,000 messages). **Conversations**: 13 simulated candidates screened end to end, deterministic checks plus an Opus judge calibrated on hand-written controls (data right 13/13, judge 4.2–4.8/5, $0.043 per screening). **Retrieval**: 127 held-out questions, keyword vs meaning vs hybrid and two embedding models, then the topic Haiku picks in four setups. **Volume**: 1,000 and 10,000 synthetic screenings through the real engine and API at $0: 2 ms of our code per message, the pipeline in 56 ms at today's volume, and interview capacity, not software, as the limit at 10× ([results](docs/design/deployment-and-scaling.md#1b-measured-the-system-at-1000-and-10000-screenings-a-week)). Results are committed, with what each finding changed: two paths to a false knock-out and a recap loop were found and closed |
| **API** | `/api/conversations` for channels (web, WhatsApp, voice), `/api/candidates` + `/api/analytics` for recruiters and an ATS, `/api/config` for the read-only workspace rules. OpenAPI docs at `/docs` |

## How it works

```
candidate message
      │
      ▼
 0. RETRIEVE     local multilingual embeddings → the 5 closest FAQ topics, with their answers
      │
      ▼
 1. UNDERSTAND   Claude Haiku 5.5, structured output → TurnAnalysis
                 values + verbatim evidence, intents, language, sentiment, FAQ topic (or none)
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
 candidate (web chat · WhatsApp · voice)          recruiter (web app · ATS)
                 │                                         │
       /api/conversations             /api/candidates · /api/analytics
                 └──────────────► FastAPI ◄─────────────────┘
                                     │
                      ScreeningEngine (pipeline above)
                                     │
             SQLite: conversations · messages · events · reviews
```

The recruiter web app only talks to the API, like any other client ([ADR 0008](docs/decisions/0008-api-first-recruiter-tool.md), [ADR 0009](docs/decisions/0009-react-web-app.md)); FastAPI also serves it, so production is one process. What the bot decided and what a recruiter decided are stored separately; every override is audited.

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
web/           React + TypeScript recruiter web app (an API client, built into web/dist)
scripts/       run, seed demo data, export samples
samples/       real conversations with highlights, transcript, data and summary
tests/         policy, engine, API, validators, locations, eval datasets (offline, deterministic)
evals/         extraction and conversation evals against the real models, with committed results
docs/          process design, decision log, ADRs, live testing log, design docs (ATS, deployment)
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
| RAG: local embeddings, the model chooses, code inserts | Embeddings find the closest topics (meaning beat hybrid search when measured); the model picks by the approved answer, or none; the writer phrases only that answer. No vector database at 205 vectors, pgvector when it grows | [0010](docs/decisions/0010-knowledge-base-retrieval.md) (was [0007](docs/decisions/0007-faq-without-vector-db.md)) |
| API-first, the UI is a client | Logic in one place, ready for WhatsApp/voice/ATS; the UI was replaced (Streamlit → React) without touching the core | [0008](docs/decisions/0008-api-first-recruiter-tool.md) |
| React web app with a design system | Orbio's visual language with the client as workspace; motion that explains, accessible charts, light/dark tokens checked for contrast; one process in production | [0009](docs/decisions/0009-react-web-app.md) |

## Potential improvements

In the order I would do them with more time. Most come from what testing and the evals showed.

### Before a pilot
| Improvement | Why | Trade-off / note |
|---|---|---|
| **A real WhatsApp channel** (Cloud API) and **authentication** on the API | The channel the candidates actually use; today the API is an open local demo | Greeting and reminders are already fixed templates, as WhatsApp requires |
| **Production architecture**: Postgres, a queue ordered per conversation, scheduled follow-ups, outbox | Correctness with several workers (ordering, no double sends) | Designed in [deployment and scaling](docs/design/deployment-and-scaling.md) |
| **Answers to the open questions** (e-bikes, data retention; confirm the [foreign-licence rules](docs/design/foreign-licences.md)) | They change knock-out rules; once answered they become configuration | [Process design §8](docs/process-design.md) |
| **Pre-fill what the application already knows** (name, city) | Fewer questions; the candidate still confirms everything at the recap | Needs the ATS integration ([API spec](docs/design/ats-api.yaml)) |

### Product
| Improvement | Why | Trade-off / note |
|---|---|---|
| **The client's own documents in the knowledge base** (rider handbook, policies, per-restaurant notes), split into passages and indexed like today's examples; questions recruiters answer by hand become new examples | Today's 30 topics are illustrative. The retrieval already scales to this, and stored shortlists show what it missed | Each passage needs an owner at the client who approves it. Re-measure hybrid search then: names and codes are where keywords help (ADR 0010) |
| Confirm an opt-out that arrives with frustration | ≈ 3% of complaints are read as opt-out (D147). It is recoverable today: writing again resumes the screening | One more message for someone who really wants to stop |
| Check the licence at the interview, and measure how often candidates lie about it | Protects recruiter time without collecting ID documents in a chat (data minimisation, bias, drop-off) | A rejection reason "no licence at the interview" gives the number before adding friction |
| Voice in production (a phone line or WhatsApp voice notes) | The demo voice channel exists (ADR 0011); production needs streaming speech providers under a data-processing agreement, and interrupting Sofía mid-sentence | Latency matters more: understanding and writing may become one call for voice only |
| Recruiter app in Spanish | Grupo Sazón's recruiters work in Spanish. The app is in English for this review; the summaries are already in Spanish | Interface strings only |
| Calendar integration for interviews, a reminder the day before, and no-show tracking | Today the times come from configuration; the client's real calendar (Google/Microsoft or the ATS) is the production version | No-shows are the next leak in the funnel after "no answer" |
| Experiment with reminder timing and wording | The recovery rate is already measured, so a variant can be compared against it | Needs volume to be significant |

### Quality and evals
| Improvement | Why |
|---|---|
| Label a sample of real pilot conversations and grow the eval sets | 126 messages and 13 conversations find failure modes, but are not enough to quote error rates |
| Have recruiters rate a sample by hand | Calibrates the LLM judge on the client's own standard |
| Turn every recruiter override into an eval case | Where the system and the recruiters disagree is the most useful data there is |
| Evals in CI on prompt or model changes, plus canary rollouts | Catches regressions before they reach candidates |
| Recruiter summary on Sonnet, or through the Batch API | The Opus summary is ≈ 40% of the cost per screening. Switch only after checking `summary_faithful` with the judge |

### What I'd do differently
- **Start the evals on day one.** The most serious problems were found by the evals, late in the week: two paths to a wrong knock-out and a loop in the recap. Unit tests can't find them, because they script the model's answers.
- **Give eval cases production context from the start.** The first version had none and overstated one risk by 19/20 vs 0/20 (D141).
- **Skip the throwaway UI.** The first recruiter tool was Streamlit, later replaced by React. API-first made the switch cheap, but going straight to the final interface would have saved time.

## Structured output

Every conversation produces a `ScreeningData` record (plus per-field status, flags and the full audit trail):

```json
{
  "full_name": "Ana López",
  "has_drivers_license": true,
  "license_status": "yes",
  "license_type": "car",
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
