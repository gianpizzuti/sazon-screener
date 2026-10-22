# Evals

The unit tests (`tests/`: 151 on the product, offline and free) prove the rules do the right thing **given** a model's reading. These evals measure the models themselves, on real API calls, and every result is committed so it can be read without running anything.

| Eval | Question it answers | Latest results |
|---|---|---|
| **Extraction** (`extraction.py`, 118 hand-labelled messages) | Does the understanding model read each message correctly, and does it never invent a value? | [`results/extraction.md`](results/extraction.md) |
| **Conversations** (`conversations.py`, 13 simulated candidates + `judge.py`) | Does a whole screening end where it should, with the right data, in a way a candidate would find clear and respectful? | [`results/conversations.md`](results/conversations.md), [transcripts](results/conversations/) |

```bash
make eval-extraction       # Haiku (production model), ≈ $0.03
make eval-compare          # Haiku vs Sonnet vs Opus, ≈ $1.25
make eval-conversations    # 13 conversations + Opus judge, ≈ $1
python -m evals.extraction --only lic_vague sd_exact      # a few cases, printed in full
python -m evals.conversations --only p08 --no-judge       # one persona, no judge
```

## Headline numbers

**Extraction, production model (Haiku 5.5):**

| Metric | Result |
|---|---|
| Fields correct | 143/146 |
| Spurious values (said by nobody) | 1 in 118 messages ("esos días trabajo por la tarde", read as a preferred shift after qualifying, where it has no effect) |
| Interview time chosen, model reading (used only when the rules can't tell) | 5/5 |
| Values backed by a verbatim quote | 100% |
| Location after the deterministic rules | 22/22 (the model alone: 20/22) |
| Latency p50 | 1.5 s |
| Cost per 1,000 messages | ≈ $0.2 |

Opus 5.5 scores higher on its own (111/112 cases against Haiku's 107/112 on the same dataset), but it costs about 40× more and every remaining Haiku error is caught by a code layer. That is why production keeps Haiku (D146).

**Conversations (final run):**

| Metric | Result |
|---|---|
| Outcome as expected | 11/13 |
| Screening data exactly right | 13/13 |
| Template fallbacks | 0 |
| Guard rejections | 0 |
| Median length | 8 candidate messages |
| Engine cost per complete screening | $0.043 (≈ $43 per 1,000) |

The judge's mean scores (1–5):

| Warmth | Clarity | Brevity | Language | Honesty | Handling | Summary |
|---|---|---|---|---|---|---|
| 4.7 | 4.4 | 4.5 | 4.8 | 4.6 | 4.2 | 4.5 |

Both 2 "misses" in the conversation run ended in *needs review* through the recap hand-off (D154), and that hand-off is the intended behaviour. One was a simulator being pedantic about a date format. The other revealed a real gap, fixed after the run (D162–D163).

## What the evals changed

The point of an eval is the changes it causes. Each row below was found by an eval, fixed in code or prompt, and given a regression test or a held-out case.

| Found | How often | Fix | Decision |
|---|---|---|---|
| Eval cases without the context production has overstated a risk | 19/20 without context, 0/20 with it | Cases get the data already known at that point | D141 |
| A past workplace ("6 months with Deliveroo in Berlin") read as the location, a path to a **false knock-out** | (see above) | Knock-outs need an answer to the knock-out question; prompt clarified | D142, D143 |
| "más o menos" to the licence question read as *in progress*, a **false knock-out** | 18/20 | A vague answer is not a value | D143 |
| A complaint read as *postpone* / *opt-out* | 15/20, 2/20 | Prompt definitions; residual ≈ 3% accepted and monitored | D143, D147 |
| A question routed to a related FAQ ("parking?" → vehicle) | 19/20 | The writer checks that the answer fits the question | D145 |
| The recap loop: the same recap re-sent up to 5 times; 2 of 13 candidates gave up | 3/13 conversations | The recap always ends: explain, complete, or hand over after 3 rounds | D154 |
| The agent told a candidate what to say to pass a knock-out | 1/13 | Never coach an answer | D156 |
| A question in the final message was dropped | 2/13 | The final message answers it | D155 |
| Neutral Spanish scored low on "language" (3.9/5) | 7/13 | First fixed with the application's country (4.8/5). Then revised: the rubric itself asked for regional vocabulary, so the evidence was circular. Now one wording before the city | D157 → D192 |
| Recap had no licence type; a corrected recap did not say it was updated | 2/13 | Licence type recorded and shown; "he actualizado tus datos" | D162, D163 |

## Method, and why

- **Labels by hand, scored per field (D140).** A wrong value and a value nobody said (*spurious*) are counted separately, because the rules act on every value the model returns.
- **Production-like context (D141).** Each case carries the data the engine would already know at that point of the screening.
- **Held-out cases (D144).** Cases written after the fixes check that a fix generalises, instead of fitting the cases that revealed the problem.
- **Repeated sampling for risky cases (D148).** Model outputs vary, so a single pass can hide a 10% failure rate. Risky cases are re-run 20–30 times.
- **The simulator is told facts, a style and today's date (D152).** Its own mistakes are reported apart as *simulator problems*, so they are not counted against the agent.
- **The judge is checked (D153).** Two hand-written controls must land at the bottom (≤ 2) and top (≥ 4) of the scale. It caught a flaw in my own "good" control.
- **Cost from metered usage (D149).** Every run records its cost, model, prompt fingerprint and commit, so results stay comparable across prompt versions.

## Limits

- **Small datasets.** 118 messages and 13 conversations are enough to find failure modes and compare models, but not to quote precise error rates. The next step is to label a sample of real conversations from the pilot.
- **Mixed prompt versions.** The Sonnet and Opus extraction runs used the prompt before the last two clarifications; the report shows each run's prompt fingerprint.
- **An LLM judge has biases**, for example leniency and preferring longer answers. The controls bound this but do not remove it. For a client, a recruiter would also rate a sample by hand.
- **A judge scores what its rubric asks.** Its "language" criterion rewarded the regional vocabulary I had chosen, so the 3.9 → 4.8 gain was circular and the change was rolled back (D192). Rubric criteria must come from the client or from candidates, not from the design being judged.
- **Total eval spend across all rounds: about $4.5**, including the repeated sampling.
