# Volume test

Thousands of synthetic screenings through the production engine, storage, scheduler and API (`scripts/volume_test.py`). The language models are replaced by a scripted reader and the fixed templates, so this measures **our own code at volume, at $0**; model latency and cost are in the other evals (understanding ≈ 1.6 s, writing ≈ 1.3 s per turn). One process, SQLite, a laptop.

| | 1,000 screenings | 10,000 screenings |
|---|---|---|
| Candidate messages processed | 7,646 in 14.2 s (539.0/s, 8 threads) | 77,094 in 150.5 s (512.3/s, 8 threads) |
| Engine time per message, without the models: p50 / p95 | 1.8 / 49.1 ms | 1.9 / 48.9 ms |
| Follow-up scheduler, one pass over every conversation | 134 ms (72 reminders or abandonments) | 1,911 ms (743 reminders or abandonments) |
| Database | 19.9 MB · 16,832 messages · 11,865 events | 196.1 MB · 165,867 messages · 116,065 events |
| GET /api/candidates (the pipeline) | 56 ms p50 · 720.1 KB | 818 ms p50 · 7,235.3 KB |
| GET /api/analytics | 95 ms p50 · 1.1 KB | 1,621 ms p50 · 1.2 KB |
| GET /api/candidates/{id} (one candidate) | 2 ms p50 · 17.2 KB | 2 ms p50 · 6.2 KB |
| Outcomes | qualified 474, awaiting_reply 230, disqualified 184, needs_review 63, withdrawn 49 | qualified 5016, awaiting_reply 2251, disqualified 1738, withdrawn 501, needs_review 492, in_progress 2 |
| Interviews | booked 414, handed_off 47, offered 13 | handed_off 3777, booked 986, offered 253 |
