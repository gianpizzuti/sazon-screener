# ADR 0008: API-first, with a Streamlit recruiter tool as one of its clients

**Status:** accepted

## Context
Recruiters need to see the queue, open a candidate, understand why the agent did what it did, record their own decision and see whether the funnel works. The same data and actions will be needed by other clients: a WhatsApp webhook, a voice agent, the client's ATS. There were five days to the deadline, and the backend is what the technical evaluation focuses on.

## Decision
- **One FastAPI service with two groups of routes:**
  - `/conversations` (channel side): start a conversation, send a message.
  - `/candidates` and `/analytics` (recruiter side): queue, detail, review, erase, summary.

  OpenAPI docs are generated at `/docs`.
- **The recruiter dashboard is a Streamlit app that talks only to the API**, exactly as an ATS or a chat widget would. Business logic lives in one place.
- **What a human decides is stored apart from what the bot decided** (a `reviews` table). A recruiter can always override the automated outcome. The override is logged as a `human_override` event, which is how the EU AI Act's human oversight shows up in the product.
- **Read models (`views.py`) and analytics (`analytics.py`) are plain functions over the repository**, so they are unit-tested without a server.

## Alternatives considered
| Option | Why not |
|---|---|
| React (or similar) frontend | Better-looking and multi-user ready, but 2-3x the code to write and defend for the same functionality. Because the dashboard is only an API client, swapping it later doesn't touch the core. |
| Streamlit reading the database directly | One process instead of two, but it would bypass the API (logic duplicated, API untested by real use), and it's not how an ATS would integrate. |
| No dashboard, only exports | Doesn't meet the brief ("a tool recruiters can start using"). |

## Trade-offs accepted
- **Two processes to run.** Mitigated by `make run`, which starts both.
- **Streamlit is fine for an internal pilot, not for a multi-tenant product.** It has no authentication, roles or audit of who viewed what, and its rerun model limits interactivity.
- **The UI is in English** for the take-home audience, while recruiter-facing AI content (summaries) follows `recruiter_language` (Spanish). For Grupo Sazón's recruiters the UI would be localised.
- **Analytics are computed in Python over all rows.** Fine at pilot scale, not at 10K/week (see the revisit triggers).

## Revisit when
- More than a handful of recruiters, or recruiters from several clients → a real frontend with authentication and roles.
- Analytics take more than a second → SQL views over `events`, or a warehouse.
