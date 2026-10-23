# ADR 0010: Knowledge-base retrieval with local multilingual embeddings

> The assessment's **RAG** bonus in its standard form. **Retrieval**: an embedding model finds the knowledge-base topics closest to the candidate's question. **Augmentation**: code inserts the one approved answer. **Generation**: Sofía phrases only that. This replaces the retrieval step of [ADR 0007](0007-faq-without-vector-db.md); its augmentation and generation rules stand.

**Status:** accepted

## Context
- ADR 0007 had the understanding model classify each question over the titles of all 16 topics, kept in its cached system prompt. That works at 16 topics, but the prompt grows with every topic, and the model judged a topic by its title alone.
- The knowledge base grew to 30 topics (D211). Some are close neighbours, as a real one would be:
  - money: pay, tips, payday, fuel and vehicle costs;
  - accidents: insurance cover vs what to do after an accident;
  - contract: type of contract vs trial period;
  - area: zones vs delivery distance;
  - requirements vs work permit vs foreign licence vs documents.
- A client's knowledge base will keep growing: per restaurant, then their handbook and policies. Retrieval should not need redesigning when it does.
- No knowledge base came with the assignment. The content is illustrative, and where a figure belongs to the client (amounts, distances) the answer says the team confirms it.

## Decision
1. **Index.** Each topic is indexed by its question and its example phrasings: 205 texts in Spanish (Spain and Mexico) and English.
   - They are embedded with `paraphrase-multilingual-MiniLM-L12-v2` (384 dimensions), run locally through fastembed (ONNX).
   - A topic scores as its closest phrasing.
   - A question at the end of a long message is also embedded on its own, so the rest of the message does not dilute it.
2. **Shortlist.** The 5 closest topics, each **with its approved answer**, travel in the per-message request to the understanding model. The cached system prompt no longer contains the knowledge base, so its size no longer depends on it.
3. **Choice.** The model sets `faq_id` only if a topic's *answer* directly answers the question. Otherwise it returns none. The choice needs a model: a similarity score cannot tell "related" from "answers it" (parking is close to "vehicle" but is not answered by it).
4. **Unchanged:**
   - code inserts the single approved answer, or one built from configuration (zones, interview times);
   - the writer phrases only that and checks that it fits (D145);
   - unanswered questions are logged for recruiters and become the backlog for the knowledge base.
5. **Degraded mode.** Without the embedding model (not installed, or not downloaded yet), the model sees every topic: the ADR 0007 behaviour, correct at this size.
6. **Audit.** The shortlist is stored with each candidate message and shown in the app ("Closest FAQ topics", the chosen one highlighted), so a retrieval miss can be seen.

## Measurements ([`evals/results/retrieval.md`](../../evals/results/retrieval.md))
The eval has 127 questions that are not in the index (a test checks it).
- 112 are answered by a topic and 15 by none.
- 8 were asked by the simulated candidates rather than written by me.
- 24 were written before the change they judge was run.

**Retrieval** (local, $0), on the 112 answerable questions:

| Method | Recall@1 | Recall@5 | Median latency |
|---|---|---|---|
| Keywords (BM25) | 55% | 75% | <1 ms |
| **Meaning (MiniLM embeddings)** | **84%** | **98%** | 4 ms |
| Hybrid (BM25 + embeddings, reciprocal rank fusion) | 77% | 97% | 4 ms |
| Meaning, larger model (mpnet, 1 GB) | 88% | 99% | 11 ms |

**Routing**: the topic Haiku chooses, 2 runs per question.

| Topics shown to the model | Right topic | Wrong topic | Right on the 24 new questions | Cost per 1,000 questions |
|---|---|---|---|---|
| **Shortlist of 5 with answers (production)** | **93%** | **0** | **48/48** | $0.26 |
| Shortlist of 5, titles only | 91% | 4 (+2 topics where none applies) | 42/48 | $0.21 |
| Every topic with answers | 94% | 4 | 46/48 | $0.49 |
| Every topic, titles only (ADR 0007) | 91% | 4 | 42/48 | $0.30 |

A **wrong topic** is the error that matters, because the writer receives an approved answer to another question. A **missed** topic is safe: "the team will confirm", logged. Production misses 7% of answerable questions in exchange for zero wrong topics. Two of those misses are retrieval misses ("¿necesito el número de la seguridad social?", "¿vais a pasar mi teléfono a otras empresas?"). In both cases the model said none rather than pick a wrong topic from the shortlist.

## Alternatives considered
| Option | Why not |
|---|---|
| Hybrid keyword + embedding search, the textbook RAG setup | Measured worse here. It ranks the right topic higher on 11 of the 112 questions, those with exact words ("propinas", "locales"), and lower on 21: generic words ("hace falta", "need") lift wrong topics, and "¿qué hace falta para entrar?" drops from 1st to 7th. Kept as a configuration option (`retrieval.method: hybrid`) for knowledge bases full of exact names and codes, to re-measure then. I did not tune the fusion weights on the test set. |
| An embeddings API (Voyage, OpenAI, Cohere) | A second AI vendor, with its own contract and data-processing terms for candidates' messages; network latency on the hot path; cost. Anthropic has no embeddings model. The local model takes 4 ms, costs $0 and the text never leaves the server. Trade-off: 240 MB downloaded once, about 1 s at startup. |
| A larger model (mpnet 1 GB; multilingual-e5-large 2.2 GB) | mpnet adds one question at recall@5 (99% vs 98%) for 3× the latency and 4.5× the size. Not worth it while the model chooses from 5. |
| A vector database now (pgvector, Qdrant) | 205 vectors × 384 dimensions is 315 KB in memory, and a full dot product takes under a millisecond. A database is needed for hundreds of thousands of vectors, or an index updated at runtime and shared by several processes. In production that is **pgvector** in the same Postgres ([deployment](../design/deployment-and-scaling.md)), with no new service. |
| A similarity threshold instead of a model choosing | A score cannot tell "related" from "answers it", and a threshold tuned on 127 questions would not transfer. |
| Every topic with its answer, no retrieval | The best raw accuracy (94%), but 4 wrong topics, twice the cost of the shortlist, and the prompt grows with every topic: it does not scale. |

## Trade-offs accepted
- **Partly circular evidence.** The knowledge base and most eval questions were written by the same person and share a vocabulary (the lesson of D192). Two things mitigate it: the questions asked by simulated candidates (all 5 answerable ones retrieved, and none given a topic) and the 24 questions written before the second run.
- **Precision over recall.** 7% of answerable questions get "the team will confirm" rather than risk a wrong answer about pay or contracts.
- **A local model** to ship and keep in memory: about 240 MB on disk and 1 s to load, once per process.

## Revisit when
- **The client's documents arrive** (rider handbook, policies, per-restaurant notes). Then:
  - split them into passages of about 200–400 tokens and index them like the examples;
  - re-measure the hybrid method, since names and codes are where keywords help;
  - each passage needs an owner on the client side who approves it.
- **The index passes about 10,000 passages**, or must be updated without a restart: move the vectors to pgvector.
- **There is real traffic.** The stored shortlists, together with the questions recruiters answer by hand, give a real recall figure and new example phrasings. A fresh eval set then has to be written, because the old one would be memorised.
