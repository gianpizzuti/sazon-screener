# ADR 0005: Grounded extraction and three layers of validation

**Status:** accepted

## Context
An extraction model can hallucinate ("vivo cerca" → `city: Madrid`), carry over values from earlier context, or produce schema-valid nonsense (a start date in the past). Structured outputs guarantee the *shape* of the answer, not its *truth*.

## Decision
1. **Structure:** structured outputs (`messages.parse` with Pydantic models) guarantee valid JSON with the right enums.
2. **Grounding:** every extracted value must come with a verbatim quote from the candidate's latest message. `is_grounded()` checks the quote really is there (accent/case-insensitive, tolerant of small re-spellings). Values without supporting words are discarded and logged as `ungrounded_value`.
3. **Business validation:** plain functions in `validators.py` decide what is acceptable (two-word names, coherent availability, future dates, configured service areas).
4. **Arithmetic is code's job.** The model returns *how* the date was expressed (`next_weekday: 0`), and code computes it in the candidate's timezone. Models are unreliable at date arithmetic. Code isn't.
5. **Locations: rules first, model second.** Known aliases are matched by code (including typos and ambiguity like "Centro" across four cities). The model's world knowledge is used only for places the rules don't know, and only if it names a configured city.

## Alternatives considered
| Option | Why not |
|---|---|
| Trust the structured output | Shape-valid is not truth-valid. |
| Ask the model to self-verify | A second opinion from the same kind of system. It costs a call and gives no guarantee. |
| Extract from the whole transcript every turn | Re-extraction can resurrect old or contradicted values. Extracting from the latest message only, with state as memory, is cheaper and more predictable. |

## Trade-offs accepted
Grounding can reject a correct value when the model paraphrases instead of quoting. The cost is one re-ask, and it is logged so the prompt can be tuned.

## Revisit when
Voice transcripts (ASR errors) make verbatim quotes unreliable. Then the overlap threshold should be relaxed for the voice channel.
