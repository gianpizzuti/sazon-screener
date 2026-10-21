# ADR 0002: One model per task: Claude Haiku 5.5 / Sonnet 5.5 / Opus 5.5

**Status:** accepted, to be confirmed by the extraction eval

## Context
At ~1000 candidates/week, LLM cost is negligible next to 13 recruiters: a screening costs cents. So "low volume, use the biggest model" optimises the wrong variable. What matters is:
1. **Latency on the hot path.** Each turn makes two calls while the candidate waits, and that becomes critical in voice.
2. **Tone in three registers** (Spain Spanish, Mexican Spanish, English). Candidate-facing text *is* the product.
3. **Reliable structured output** for extraction.

## Decision
The rule: models where the candidate is waiting, the most capable where nobody is.

| Task | Model | Settings | Why |
|---|---|---|---|
| Understand | `claude-haiku-5-5` | structured output, effort `low` | Narrow task with strict schema and evidence. Speed dominates. Measured 1.9 s median; disabling thinking gave no gain. |
| Speak | `claude-sonnet-5-5` | thinking off (`between_tools`), effort `low`, server-side refusal fallback | Short candidate-facing text where tone matters. **Measured:** 1.3 s median with thinking off vs 6.0 s with adaptive thinking, and better instruction-following ([live testing log](../live-testing-log.md)). |
| Summary | `claude-opus-5-5` | structured output, effort `medium` | One call per conversation, after it ends. Latency is irrelevant and quality is what recruiters see. |
| Eval judge (offline) | `claude-opus-5-5` | | The judge should be more capable than what it judges. |

Models are configured per client in `client.yaml`. Changing one is a one-line change.

## Alternatives considered
| Option | Why not |
|---|---|
| Opus 5.5 everywhere | Best quality, but its thinking can't be disabled, which adds seconds to every message on the hot path. The cost argument is weak in both directions. |
| One mid-size model everywhere | Simpler to explain. It leaves latency on the table for extraction and quality on the table for summaries. |
| Other providers (GPT, Gemini) | Comparable for this task. Differences between frontier providers matter less here than the architecture and the evals. The engine depends on `Understander`/`Responder`/`Summarizer` protocols, not on an SDK, so the choice is reversible. That matters because clients often have an existing cloud/LLM contract. |
| Self-hosted open model | Maximum data control, but the operational burden isn't justified at this volume. Revisit for strict data-residency clients. |

## Trade-offs accepted
- A smaller model may need more prompt work on hard cases (code-switching, Mexican slang). The extraction eval measures exactly this, and only the task that fails gets upgraded.
- Three models means three behaviours to know. The narrow task boundaries keep that manageable.
- The Speak system prompt is ~500 tokens, around Sonnet 5.5's minimum cacheable size, so it may not be cached. At this volume it doesn't matter, and the prompt isn't padded artificially. The Understand prompt is cached: measured `cache_read_input_tokens` ≈ 5.4k (the output schema adds to the prompt, so the size is larger than its text).

## Revisit when
- The extraction eval shows Haiku below target on a field → upgrade Understand to Sonnet.
- The voice channel needs lower latency → merge Understand + Speak into one call for voice only.
- Data residency requires it → same models via a cloud provider in an EU region.
