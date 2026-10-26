# Sazón Screener

A conversational agent that screens delivery-driver applicants for **Grupo Sazón** (45 restaurants in Spain and Mexico, ~1,000 applications a week), and a web app for recruiters to act on the results.

| Client problem | How it is addressed |
|---|---|
| 60% of candidates don't answer recruiter calls | Asynchronous chat, first message seconds after applying, automatic reminders |
| 80% of recruiter time goes to unqualified candidates | Knock-out questions first; recruiters only receive qualified or flagged candidates, with a summary |

**Deliverables:** [Demo video](#) (_link added at submission_) · [Process design](docs/process-design.pdf) (Phase 1) · [Sample conversations](samples/README.md)

**Further reading:** [Decision log](docs/decisions/decision-log.md) · [Evals](evals/README.md) · [Deployment and scaling](docs/design/deployment-and-scaling.md) · [ATS integration](docs/design/ats-integration.md)

---

## Setup

Requirements: Python 3.11+, Node 18+, an Anthropic API key.

```bash
make install            # Python package + builds the web app
cp .env.example .env    # set ANTHROPIC_API_KEY (ELEVENLABS_API_KEY is optional, for the voice)
make run                # web app + API on http://localhost:8000 (API docs at /docs)
make test               # 478 offline tests, no API key needed
```

The first start downloads a small embedding model (≈ 240 MB, once). Optional: `make seed` fills the app with 20 demo candidates (real models, ≈ 2 USD); `make chat` talks to the agent in the terminal.

## Architecture

```
candidate message
      │
 0. RETRIEVE     local embeddings → the 5 closest topics of the client's knowledge base
 1. UNDERSTAND   Claude Haiku, structured output: values + the candidate's exact words, intents, language
 2. DECIDE       ScreeningPolicy, plain Python: validation, knock-outs, next question
 3. SPEAK        Claude Sonnet writes one short message from the policy's instructions
 4. GUARD        length and format checks → retry once → fixed template
 5. PERSIST      state, transcript and audit events in one transaction (SQLite)

 after the conversation: recruiter summary with Claude Opus
```

**The model never decides eligibility.** It reads and it writes; knock-outs, validation and question order are deterministic code with unit tests.

```
 candidate (web chat · voice · WhatsApp)        recruiter (web app · ATS)
                 │                                        │
       /api/conversations             /api/candidates · /api/analytics
                 └──────────────► FastAPI ◄───────────────┘
                                     │
                      ScreeningEngine (pipeline above)
                                     │
                    SQLite: conversations · messages · events
```

**What it does**
- **Sofía, the agent:** Spanish (Spain or Mexico) or English, switching with the candidate; answers questions from the client's approved knowledge base; handles corrections, ambiguity, opt-outs and manipulation attempts; qualified candidates book their interview in the chat.
- **Reminders:** up to three for silent candidates (2 h, 24 h, 72 h), never at night in their timezone.
- **Voice:** the same agent by voice in the browser, with ElevenLabs voices per country.
- **Recruiter web app:** pipeline, candidate detail (summary, data with the candidate's words, the reason behind every message, override), analytics, a page to try the agent, and the flow with its rules.

**Output** for every screening (plus field status, flags and an audit trail):

```json
{
  "full_name": "Ana López",
  "has_drivers_license": true,
  "license_type": "car",
  "city": "Madrid",
  "zone": "Chamberí",
  "in_service_area": true,
  "availability": ["part_time", "weekends"],
  "preferred_schedule": ["evening"],
  "experience_months": 24,
  "experience_platforms": ["Glovo", "Uber Eats"],
  "start_date": "2026-10-26"
}
```

```
config/clients/grupo_sazon/   everything client-specific: service areas, knowledge base, wording, rules
src/screener/                 domain, engine (policy + pipeline), llm, storage, api, channels
web/                          React recruiter web app (an API client)
tests/ · evals/               offline tests · evals against the real models, with results
docs/                         process design, decision log, design documents
```

## Key design decisions

| Decision | Why |
|---|---|
| **Code decides, the model understands and writes** ([ADR 0001](docs/decisions/0001-code-decides-llm-understands.md)) | Auditable, testable and immune to "approve me" messages; recruitment AI is high-risk under the EU AI Act |
| **One model per task** ([ADR 0002](docs/decisions/0002-llm-per-task.md)) | Haiku reads every message (124 of 126 labelled messages right, about 28× cheaper than Opus); Sonnet writes; Opus writes the summary, off the hot path |
| **Every value must quote the candidate** ([ADR 0005](docs/decisions/0005-grounding-and-layered-validation.md)) | Structured output guarantees the shape, not the truth: a value without the candidate's words is discarded |
| **The client is configuration** ([ADR 0003](docs/decisions/0003-config-driven-client.md)) | Zones, answers and wording change without a deploy; a new client is a new folder |
| **Answers only from the approved knowledge base** ([ADR 0010](docs/decisions/0010-knowledge-base-retrieval.md)) | Local embeddings find the closest topics (98% recall@5, $0), the model picks one or none, code inserts the approved answer: Sofía can't invent pay |
| **Templates where precision matters** ([ADR 0006](docs/decisions/0006-templates-where-precision-matters.md)) | The greeting, the recap and the fallback are fixed text: data is never paraphrased and the conversation never breaks |
| **API first** ([ADR 0008](docs/decisions/0008-api-first-recruiter-tool.md)) | Web chat, voice, WhatsApp and an ATS are all clients of the same API |
| **SQLite with an event log** ([ADR 0004](docs/decisions/0004-sqlite-sqlalchemy.md)) | No setup for reviewers, real queries and an audit trail; Postgres is one URL away |

## Potential improvements

In the order I would do them:

1. **A real WhatsApp number and authentication** on the API: the channel candidates actually use.
2. **Production setup:** Postgres, a queue ordered per conversation, scheduled reminders ([designed](docs/design/deployment-and-scaling.md)).
3. **Interview capacity:** the volume test shows Mexico City, Barcelona and Madrid already need more interviews than one location per city can hold. Group sessions, video first interviews or more locations: a decision for the client.
4. **Answers to the open questions:** e-bikes, data retention, the foreign-licence rules ([process design §8](docs/process-design.md)).
5. **The client's own documents in the knowledge base**, and questions recruiters answer by hand turned into new entries.
6. **Calendar integration** for interviews, a reminder the day before, and no-show tracking.
7. **Evals from real pilot conversations**, with every recruiter override turned into a test case.
