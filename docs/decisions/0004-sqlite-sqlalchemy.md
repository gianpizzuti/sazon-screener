# ADR 0004: SQLite through SQLAlchemy, with an append-only event log

**Status:** accepted

## Context
The brief allows JSON files or a database. The recruiter tool needs to filter and sort candidates, and analytics (completion rate, drop-off by stage) need queries across conversations. Whoever evaluates the project must be able to run it in minutes.

## Decision
- **SQLite** via **SQLAlchemy 2.0**, with three tables:
  - `conversations`: current state as JSON, plus denormalised columns to filter on (stage, city, needs_review…)
  - `messages`: the transcript. Each message keeps its *why* (the analysis or the directive).
  - `events`: an append-only audit trail (`field_valid`, `knockout`, `language_switched`, `llm_error`…). Analytics are computed from it.
- A whole turn (state + messages + events) is saved in **one transaction**.
- Conversations are serialised per conversation with an in-process lock, so two quick messages can't race.

## Alternatives considered
| Option | Why not |
|---|---|
| JSON files | Zero dependencies, but no queries for the dashboard, no atomic multi-file writes, no concurrency. |
| Postgres now | The production choice, but it forces evaluators to set up a server. SQLAlchemy makes the switch a connection-string change. |
| Event sourcing only (rebuild state from events) | Elegant and fully auditable, but over-engineered here. We keep events for audit/analytics *and* a state snapshot for simplicity. |

## Trade-offs accepted
- SQLite allows a single writer, and the per-conversation lock only works within one process. Both are fine for a pilot and both break with several workers.

## Revisit when
Running more than one worker process. Then: Postgres, row-level locking (`SELECT … FOR UPDATE`) or a per-candidate queue partition, and migrations with Alembic.
