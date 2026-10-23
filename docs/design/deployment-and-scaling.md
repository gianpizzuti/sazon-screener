# Design: deployment and scaling

**Status:** design, not built. Today the system runs as one process: FastAPI serves the API, the web app and an in-process follow-up loop, on SQLite. That is right for a demo and a small pilot. This document is the path to production at Grupo Sazón's volume (1,000 applications/week) and to ten times that.

## 1. The numbers that size everything

From the conversation eval: median **8 candidate messages** per screening, **$0.043** of model cost per complete screening, about **3 s** per turn (understanding ≈ 1.5 s + writing ≈ 1.3 s).

| | Today's volume | 10× |
|---|---|---|
| Applications / week | 1,000 | 10,000 |
| Turns / day (≈ 10 per screening) | ≈ 1,400 | ≈ 14,000 |
| Turns / second, average · peak hour (assumed 5× average) | 0.02 · 0.1 | 0.17 · ≈ 1 |
| Model calls / day (2 per turn + 1 summary per screening) | ≈ 3,000 | ≈ 30,000 |
| Model cost / week, if every screening completes | ≤ $45 | ≤ $430 |

**What this means.** Compute is not the problem: one small container handles the peak. The real constraints are three:
1. **The model provider's rate limits.** At 10×, the peak is around 120 requests per minute and a few hundred thousand input tokens per minute, mostly cached. The account tier has to cover that.
2. **Correctness with several workers**: ordering, no double sends, no lost events.
3. **WhatsApp's rules**: approved templates, the 24-hour window, and quality ratings that drop if people block the number.

## 2. Target architecture

```
WhatsApp Cloud API ──webhook──► Ingress (stateless)
                                  · verify signature · dedupe by message id · answer 200 at once
                                  │ enqueue, ordering key = conversation
                                  ▼
                                Queue ──► Workers: ScreeningEngine ──► Claude (Anthropic API, or an EU cloud region)
                                              │                  └──► WhatsApp send API
                                              ▼
                     PostgreSQL: conversations · messages · events · reviews · outbox
                                              ▲
Scheduler (every minute) ──► follow-up job ───┘      Outbox worker ──► ATS adapter (docs/design/ats-integration.md)

Recruiter web app (static files, CDN) ──► Recruiter API (SSO)
```

| Decision | Why | Rejected alternative |
|---|---|---|
| **Answer the webhook at once and process from a queue** | WhatsApp retries if the reply is slow, and a turn takes about 3 s. A queue also absorbs bursts and outages of the model provider | Processing inside the webhook request (timeouts, then duplicate deliveries) |
| **Ordering per conversation**: the queue's ordering key (SQS FIFO message group, Pub/Sub ordering key) plus a Postgres advisory lock on the conversation | A candidate's messages must be handled one at a time and in order. Today's per-conversation lock is in-process (`threading.Lock`), so it protects one process only | One global worker (no parallelism) or no ordering (two answers read out of order) |
| **Idempotency everywhere it can repeat**: inbound by WhatsApp message id, follow-ups by a unique `(conversation, attempt)`, outbound by event id | Queues and webhooks deliver at least once; idempotency makes "at least once" behave like "exactly once" | Trusting single delivery |
| **Coalesce bursts**: wait about 3 s after a message before processing, and treat the messages that arrive in that window as one turn | People send "hola" / "soy Ana" / "de Madrid" as three messages; one turn reads them together and answers once (process design appendix §5) | One turn per message (three replies, some to half-sentences) |
| **Follow-ups as a scheduled job** that claims due conversations with `SELECT … FOR UPDATE SKIP LOCKED` | Several workers can run it with no double sends; the in-process loop is the pilot version (comment in `api/app.py`) | The loop inside every API process |
| **PostgreSQL**, with Alembic migrations | Concurrent writers, row locks, JSONB for state and events. The code already goes through SQLAlchemy, so the switch is the connection URL plus migrations | Staying on SQLite (one writer at a time) |
| **The knowledge-base embedding model inside the worker image** (≈ 240 MB, baked in at build time, loaded once per process in ≈ 1 s); vectors in memory, rebuilt when the configuration changes. **pgvector** in the same Postgres once the index passes ≈ 10,000 passages (client documents) or must change without a restart | 4 ms per message on CPU, $0, candidates' messages never leave the platform (ADR 0010). At 30 topics (205 vectors, 315 KB) a database would add a moving part for nothing | An embeddings API (a second AI vendor and its data terms on the hot path); a dedicated vector database such as Qdrant (another service to run, when Postgres already does it) |
| **Containers on a managed platform**: Cloud Run or ECS Fargate, managed Postgres, a managed queue, a managed scheduler | Nothing to operate; scales on queue depth; both clouds have regions in Spain and Mexico | Kubernetes (operational weight not justified at this size) |

The platform choice should follow what Orbio and the client already run. The design only needs containers, Postgres, a queue with per-key ordering and a scheduler.

## 3. Reliability

| Failure | What happens |
|---|---|
| Model provider slow or down | Retries with backoff, then the template fallback that exists today (the conversation never breaks, and the attempt is not counted). Above an error threshold a circuit breaker sends "we're having a technical problem, I'll write to you in a few minutes", and the turn is retried from the queue |
| WhatsApp send fails | Retried from the queue; the turn's state is already saved, so nothing is processed twice |
| Worker crashes mid-turn | The message is not acknowledged, so it is redelivered; the inbound idempotency key stops a double reply |
| ATS down | Outbox retries; dead-letter queue and an alert; nightly reconciliation |
| A bad prompt or model change | Caught before release by the evals (below), or rolled back: prompts and client configuration are versioned in git |

The engine depends on `Understander`, `Responder` and `Summarizer` interfaces, not on one SDK. A second model provider can therefore be a fallback, or a requirement from the client.

## 4. Quality in production

- **On every change:** unit tests in CI (offline, seconds).
- **On every prompt or model change:** the extraction eval in CI (≈ $0.03).
- **Before a release:** the conversation eval (≈ $1).
- **Canary:** a new prompt goes to a share of new conversations first, and its metrics are compared with the current one before it goes to everyone.
- **Every week:**
  - a sample of real conversations is reviewed by a person;
  - flagged and overridden candidates are read first, because they are where the system and the recruiters disagree;
  - new failure modes become eval cases.
- **Metrics:**

  | Group | What is measured |
  |---|---|
  | Funnel | completion and drop-off by stage, recovery rate after follow-ups |
  | Quality | template fallback rate, guard rejections, unanswered questions, override rate |
  | Speed | turn latency p50 / p95 by step |
  | Delivery | WhatsApp delivery and block rates |

  Most of these already exist in the Analytics page.
- **Alerts** on: fallback rate, model errors, WhatsApp send failures, outbox dead letters, and a drop in completion rate.

## 5. Security, privacy and compliance

- **Secrets** (API keys, WhatsApp token, database) in a secret manager, never in the image or the repository.
- **Data**:
  - stored in the EU for Spain;
  - Mexico's data protection law (LFPDPPP) and the client's preference decide where Mexican data lives;
  - encrypted at rest;
  - recruiters log in with SSO and see only their client's data.
- **Model provider.** The same Claude models are also available through AWS and Google Cloud in EU regions, if the client requires it.
- **Retention.** A policy per client, for example: disqualified candidates without talent-pool consent are erased after N days. It runs as a scheduled job, and the erasure path already exists (`DELETE /api/candidates/{id}`).
- **AI Act.** Recruitment is high-risk. The audit trail (events, decisions, overrides), the human review of outcomes and the documentation of the rules are part of the product, not an add-on.

## 6. Cost levers (at 10×, ≤ $430/week in model cost)

| Lever | Effect | Trade-off |
|---|---|---|
| Recruiter summary on Sonnet instead of Opus | The summary is ≈ 40% of the cost per screening | Check `summary_faithful` with the judge before switching |
| Summaries through the Message Batches API | Half price for batch requests | The summary may take up to hours instead of seconds. Recruiters read it later anyway |
| Keep Haiku for understanding | Measured: ≈ 40× cheaper than Opus for errors the code absorbs (D146) | – |
| Reuse a recent screening for a duplicate application | No second screening (ATS doc §3) | A rule to agree with the client |

Infrastructure at this size is small next to the model cost: a few containers, a small managed database and a queue. In the order of a few hundred dollars a month, to be confirmed with the chosen cloud's pricing.

## 7. Multi-client

Every row carries a client (tenant) id. Each client has its own:
- configuration folder, as today, including its knowledge base (each client's topics are indexed separately, so one client's answers can never be retrieved for another);
- WhatsApp number and approved templates;
- API keys and ATS adapter mapping;
- retention policy.

A new client is configuration, not code (ADR 0003).

## 8. Phases

| Phase | Scope | What changes |
|---|---|---|
| **Pilot** | 1–2 cities, ≈ 200 applications/week | One container (built in two stages: Node builds the web app, a slim Python image runs it), managed Postgres, WhatsApp test then production number, auth on the API. The in-process scheduler is still acceptable |
| **Production** | 45 restaurants, ≈ 1,000/week | Queue and workers, scheduled follow-up job, outbox and ATS adapter, SSO, alerts, evals in CI |
| **Scale** | 10,000/week, more clients | Workers autoscaled on queue depth, a higher rate-limit tier, batch summaries, a read replica for analytics, multi-tenant isolation |

## Revisit when

- **The voice channel is added:** latency matters more than on chat, and understanding and writing may become one call for voice only (ADR 0002).
- **Analytics queries slow down the transactional database:** move analytics to a replica or a warehouse.
- **A client requires on-premises or a specific cloud:** the containers and Postgres move as they are; only the managed queue and scheduler are swapped.
