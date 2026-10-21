# ADR 0006: Templates where precision beats naturalness, and as the degraded mode

**Status:** accepted

## Context
Some messages must be exact: the opening message (legal disclosure, and on WhatsApp business-initiated messages must be pre-approved templates anyway), and the recap where the candidate checks their data. Separately, the LLM API can fail, and a candidate should never see a broken conversation.

## Decision
- The **greeting** and the **recap** always come from `copy.yaml`, rendered from state. The model never paraphrases a candidate's data back to them.
- All other messages come from the Speak model, but every directive also has a **template rendering** (`TemplateResponder`). It is used when:
  - the Speak call fails (API error, timeout, refusal), or
  - the draft fails the output guard twice.
- If **Understand** fails, the agent apologises and asks again. That attempt is not counted against the candidate.
- Every message records its `source` (`llm` / `template`), and failures are logged as events. The fallback rate is a metric to monitor.

## Trade-offs accepted
- The template mode is stiffer, and a Spanish FAQ answer may reach an English speaker in degraded mode. Acceptable for a failure path.
- Copy has to be maintained per locale. It is also useful as reference wording for the model.

## Revisit when
The fallback rate is persistently non-trivial. That points to a prompt or guard problem, not something to paper over.
