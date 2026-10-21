# Architecture Decision Records

Every decision, small ones included, is listed in the **[decision log](decision-log.md)** (108 entries). The records below are the deep-dives on the important ones.

Each record says what was decided, the alternatives considered, the trade-offs accepted and **when the decision should be revisited**.

| # | Decision |
|---|---|
| [0001](0001-code-decides-llm-understands.md) | Code decides, the LLM understands and speaks |
| [0002](0002-llm-per-task.md) | One model per task: Haiku 5.5 / Sonnet 5.5 / Opus 5.5 |
| [0003](0003-config-driven-client.md) | Client specifics are configuration, the screening schema is code |
| [0004](0004-sqlite-sqlalchemy.md) | SQLite through SQLAlchemy, with an append-only event log |
| [0005](0005-grounding-and-layered-validation.md) | Grounded extraction and three layers of validation |
| [0006](0006-templates-where-precision-matters.md) | Templates where precision beats naturalness, and as the degraded mode |
| [0007](0007-faq-without-vector-db.md) | FAQ answering without a vector database |
| [0008](0008-api-first-recruiter-tool.md) | API-first, with a Streamlit recruiter tool as one of its clients |
