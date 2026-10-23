# ADR 0007: FAQ answering without a vector database

> This is the assessment's **RAG** bonus: retrieval (the understanding model classifies the question into one of the knowledge base's topics), augmentation (code inserts that topic's single approved answer, or one built from the configuration for zones and interview times) and generation (the writer phrases only that). What changes from classic RAG is the retrieval method, chosen for the size of the knowledge base.

**Status:** accepted

## Context
Candidates ask about pay, contract, vehicle, shifts. A wrong answer about pay is the most damaging hallucination this agent could produce: it creates false expectations and possibly legal exposure.

## Decision
- The Understand model already reads every message. It also classifies the question against the list of FAQ topics (16 ids, part of its cached system prompt) and returns `faq_id`. Two answers are built from the configuration instead of written text, so they can never drift from it: the zones of the candidate's city (D198) and the interview days and hours (D207).
- Code looks up the approved answer (with per-country overrides: IMSS in Mexico, Seguridad Social in Spain).
- The Speak model receives **only that one answer**, with the instruction to rephrase it without adding facts.
- No match → the agent says the recruiting team will confirm, and the question is saved in `pending_questions` for the recruiter.
- The Speak model also checks that the approved answer fits the exact question; if not, "the team will confirm" (D145).
- Measured: FAQ routing in the extraction eval (Haiku 12/12 on the FAQ cases, including both zone questions and the questions no topic answers).

## Alternatives considered
| Option | Why not |
|---|---|
| Vector DB + embeddings retrieval | The standard RAG answer, but for ~15 entries (~1k tokens) it adds infrastructure, an embedding model and a retrieval failure mode, for no accuracy gain. |
| Put the whole FAQ in the Speak prompt | Simpler, but the writer then sees every fact and can blend or embellish them. |

## Trade-offs accepted
Classification over topic ids doesn't scale to hundreds of entries.

## Revisit when
The knowledge base grows beyond ~50–100 entries or becomes per-restaurant. Then switch to retrieval (hybrid BM25 + embeddings) behind the same `faq_id` contract.
