# Decision log

Every decision taken while building the agent, large or small (108 so far), with the reason and the alternative that was rejected. The big ones have a full ADR (linked). This is a living document, updated with every decision.

## Product and conversation design

| # | Decision | Why | Rejected alternative / trade-off | Where |
|---|---|---|---|---|
| D01 | Messaging-first, asynchronous screening | The 60% no-answer rate is a channel/timing problem: candidates answer chats when it suits them | Automated outbound calls: same timing problem as recruiters' calls | [process design §1](../process-design.md) |
| D02 | Knock-outs (licence, area) right after the name | Ineligible candidates find out in 1 minute; recruiters never see them | Knock-outs at the end: kinder flow, wastes everyone's time. Trade-off: can feel like an interrogation, so tone compensates | process design §2 |
| D03 | Stop at a knock-out, offer talent-pool opt-in | Respects the candidate's time; data minimisation (GDPR) | Collect everything anyway: more data for future openings, but without consent | `policy._finish` |
| D04 | Slot filling: any answer, any order | Real messages contain several answers ("soy Ana, tengo carnet, vivo en Getafe") | Strict one-question form: robotic, more turns, lower completion | `policy._apply_extraction` |
| D05 | One recap checkpoint where everything can be corrected | One confirmation instead of seven; corrections re-run knock-outs | Confirm each answer: doubles the message count | `policy.decide` (CONFIRMING) |
| D06 | "Zone" = where the candidate would deliver | What matters operationally is reaching a restaurant | Where they live. **Open question for the client** | process design §8 |
| D07 | Zone is optional and asked at most once | The city is the knock-out; the zone only helps pick the nearest restaurant | Required zone: an extra hurdle for little value | `policy._account_attempt` |
| D08 | Max 2 failed attempts per field, then "unclear" + flag | No loops; a human decides ambiguous cases | Keep asking (frustrating) or disqualify (unfair) | `client.yaml: max_failed_attempts` |
| D09 | A question or small talk is not a failed attempt | Asking about pay is engagement, not a wrong answer | Counting every reply: penalises curious candidates | `NON_ATTEMPT_INTENTS` |
| D10 | Knock-out field unclear → `needs_review`, not qualified nor disqualified | Neither outcome can be justified without a human | Defaulting to either side | `policy._complete` |
| D11 | Start date > 90 days: accepted and flagged | It's a recruiter judgement, not a rule | Rejecting: the client didn't ask for it | `client.yaml: late_start_days` |
| D12 | A withdrawn candidate can come back by writing again | Changing your mind is normal; it costs nothing to accept | Final withdrawal | `policy.decide` |
| D13 | Abuse: one calm warning, then the conversation closes | Protects the brand and the bot without over-reacting to one message | Close immediately, or ignore | `policy.decide` |
| D14 | Asking for a human: flag + keep screening | Answering the rest speeds up the human follow-up | Stop and hand off immediately: the recruiter then has no data | `policy.decide` |
| D15 | AI disclosed in the first message and whenever asked | Transparency obligation (EU AI Act art. 50) and trust | A human persona: deceptive | `copy.yaml: greeting`, FAQ `is_bot` |
| D16 | Persona "Sofía": warm, direct, *tú*, ≤350 characters, one question, ≤1 emoji | Chat, not email; audience is frontline workers on their phone | Formal *usted*: distant for this audience | process design §3, §7 |
| D17 | Reply in the language of the latest message, with hysteresis | "ok", "sí", names and numbers carry no language signal and must not flip it | Fixed language, or switching on every message | `policy._update_language` |
| D18 | Spanish variant from the city's country, before that from wording hints | Country is certain; lexical hints ("carro") are a guess | Hints only | `policy._apply_location` |
| D19 | Recruiter-facing summaries in Spanish | The users are the client's recruiters | English: matches the brief, not the users | `client.yaml: recruiter_language` |

## Architecture

| # | Decision | Why | Rejected alternative / trade-off | Where |
|---|---|---|---|---|
| D20 | Code decides, the LLM understands and speaks | Auditable, injection-proof, testable; recruitment is high-risk AI | Agentic prompt, form bot | [ADR 0001](0001-code-decides-llm-understands.md) |
| D21 | Two LLM calls per turn (understand, speak) | Each call has one job; decisions happen in code in between | One combined call: faster, but mixes understanding and decision. Revisit for voice | ADR 0001 |
| D22 | Extract from the latest message only; the state is the memory | Old or contradicted values can't come back; fewer tokens | Re-extract from the whole transcript every turn | [ADR 0005](0005-grounding-and-layered-validation.md) |
| D23 | A `Directive` is the contract between policy and writer | The writer can only say what was decided; template and LLM writers are interchangeable | The writer reads the state and decides what to ask | `engine/directive.py` |
| D24 | Per-turn instructions sent as a mid-conversation **system** message | A channel the candidate cannot imitate; the cached prefix stays intact | Appending instructions to the user message: mixes operator and candidate text | `llm/claude.py` |
| D25 | Candidate text wrapped in `<candidate_message>` and declared as data | First line of defence against instructions hidden in messages | None: the real protection is D20 | `llm/prompts.py` |
| D26 | The policy works on a copy of the state; the turn is persisted at the end | A failed turn leaves no half-updated state | Mutating the stored state step by step | `engine._handle` |
| D27 | Interfaces by capability (`Understander`, `Responder`, `Summarizer`) | The engine depends on what it needs, not on a vendor; enables fakes in tests | A generic `LLMClient` wrapper: still leaks prompts into the engine | `llm/interfaces.py` |
| D28 | Synchronous engine | A turn is sequential by nature; simpler code; FastAPI runs it in a threadpool | Async everywhere: no gain at this volume | `engine/engine.py` |
| D29 | One lock per conversation | Two quick messages from the same person are processed in order | Nothing: race conditions on state. Single-process only (see ADR 0004) | `engine._lock_for` |

## LLM usage

| # | Decision | Why | Rejected alternative / trade-off | Where |
|---|---|---|---|---|
| D30 | Haiku 5.5 to understand, Sonnet 5.5 to speak, Opus 5.5 for summary and eval judging | Fast where the candidate waits, most capable where nobody does | Opus everywhere: slower hot path. To be confirmed by the eval | [ADR 0002](0002-llm-per-task.md) |
| D31 | Effort `low` on the hot path, `medium` for the summary | Short, well-specified tasks don't need deep thinking; latency matters | Default effort | `llm/claude.py` |
| D32 | Structured outputs with Pydantic (`messages.parse`) | Schema-valid JSON guaranteed; the same models validate in code | JSON in the prompt + parsing (fragile), or forced tool calls (rejected by Sonnet 5.5 / Opus 5.5) | `llm/schemas.py` |
| D33 | No "qualified" field in any LLM schema | The model cannot express a decision, so it cannot make one | n/a | `llm/schemas.py` |
| D34 | Server-side refusal fallback on Sonnet/Opus calls | A declined request gets a second model instead of a template | Handling refusals only client-side | `llm/claude.py` |
| D35 | Hot path: 20 s timeout + 2 SDK retries; summary: 120 s | Fail fast while the candidate waits, then fall back | Default 10-minute timeout | `make_client` |
| D36 | Summary generated after the conversation ends | Off the hot path: the candidate never waits for it | Summarising every turn | `engine.summarize` |
| D37 | System prompts contain no per-turn data | Byte-identical prompts hit the cache; dates and names go in the turn | Today's date in the system prompt: silently breaks caching | `llm/prompts.py` |

## Validation and data

| # | Decision | Why | Rejected alternative / trade-off | Where |
|---|---|---|---|---|
| D38 | Every value must quote the candidate (grounding) | Structured output guarantees shape, not truth | Trusting the extraction | ADR 0005 |
| D39 | The model reads the date expression; code computes the date in the candidate's timezone | Models are unreliable at date arithmetic; Spain and Mexico can be on different days | Asking the model for an ISO date | `validators.resolve_start_date`, `engine._today` |
| D40 | Locations: aliases first, the model only for unknown places and tie-breaks, and only to a configured city | Deterministic and explainable for the 95% case; world knowledge for the rest | LLM-only (unverifiable) or rules-only (brittle) | `domain/locations.py` |
| D41 | Aliases that are also real cities removed ("Salamanca", "Guadalupe") | "Vivo en Salamanca" must not become a Madrid district | Keeping them: silent wrong matches | `service_areas.yaml` |
| D42 | Fuzzy city matching at similarity ≥ 0.8, aliases ≥ 5 letters | Catches typos ("Madriz" = 0.83) without confusing configured cities | 0.85: missed common typos | `LocationMatcher` |
| D43 | Most specific zone alias wins ("centro histórico" over "centro") | Avoids false ambiguity | Treating every match equally | `LocationMatcher._zone_hits` |
| D44 | An ambiguous place followed by a city keeps the zone ("centro" → "Madrid" = Madrid Centro) | That's what the candidate means | Asking again for the zone | `_zone_from_options` |
| D45 | Partial values are kept (a first name while asking for the surname) | The agent can already use the name | Discarding until fully valid | `policy._record` |
| D46 | During screening a bad side remark never erases a valid answer; at the recap it reopens the field | Mid-flow noise vs. an explicit correction | One rule for both | `policy._record` |
| D47 | Names: capitalise lowercase words, keep particles and the candidate's own casing | "ana López" → "Ana López", "María de la Cruz", "McDonald" | `str.title()`: breaks particles and "McDonald" | `validators._title` |
| D48 | Full-time + part-time = contradiction; weekends combine with either; three shifts = flexible | Mirrors how candidates actually answer | Rejecting combinations | `validators` |
| D49 | Platform names normalised; unknown employers kept as written | "uber" → "Uber Eats"; a local pizzeria is still experience | Dropping unknown platforms | `normalize_platforms` |
| D50 | Inbound messages capped at 1000 characters | Cost and prompt-abuse bound; nobody screens in essays | No limit | `MAX_INBOUND_CHARS` |

## Messages

| # | Decision | Why | Rejected alternative / trade-off | Where |
|---|---|---|---|---|
| D51 | Greeting and recap are fixed templates | Legal disclosure and the candidate's own data must be exact; WhatsApp requires templates for business-initiated messages anyway | LLM-written: natural but unverifiable | [ADR 0006](0006-templates-where-precision-matters.md) |
| D52 | Output guard: length, markdown, leaked instructions → one retry with feedback → template | The prompt is the first defence, not the only one | Trusting the prompt | `engine._guard` |
| D53 | Outcome messages and answers may be 1.4× longer | They carry more information (next steps, FAQ answer) | One limit for everything | `engine._char_limit` |
| D54 | Quick-reply buttons for closed questions | Fewer ambiguous answers; maps to WhatsApp interactive messages | Free text only | `copy.yaml: options` |
| D55 | FAQ: the model picks the topic, code inserts the one approved answer; unknown questions logged | The writer can't embellish pay or benefits | Vector RAG, or the whole FAQ in the writer's prompt | [ADR 0007](0007-faq-without-vector-db.md) |
| D56 | Template-mode wording specific to each validation problem ("¿Y tu apellido?") | The degraded mode should still sound like a person | A generic "I didn't get that" | `copy.yaml: issue` |

## Storage, configuration and tooling

| # | Decision | Why | Rejected alternative / trade-off | Where |
|---|---|---|---|---|
| D57 | SQLite + SQLAlchemy + append-only event log | Zero setup, real queries, audit trail; Postgres is a URL change | JSON files, Postgres now | [ADR 0004](0004-sqlite-sqlalchemy.md) |
| D58 | Every stored message keeps its *why* (analysis or directive) | Explainability for recruiters and auditors; debugging | Storing text only | `engine._handle` |
| D59 | A whole turn is saved in one transaction | No transcript without state, or the reverse | Separate writes | `Repository.save_turn` |
| D60 | Client-specific data in a YAML folder; screening schema in code | Zones, FAQ, wording change without a deploy | Fully dynamic schema: premature with one client | [ADR 0003](0003-config-driven-client.md) |
| D61 | FAQ contents marked as placeholders | Pay and contract details must come from the client | Presenting invented facts as real | `faq.yaml` |
| D62 | `venv` + `pip` + `Makefile` | Works on any machine with Python; nothing extra to install for evaluators | uv / poetry: nicer, but one more prerequisite | `Makefile` |
| D63 | Tests run offline: scripted understanding + template writer | Deterministic, free and fast (< 1 s); every process rule is covered | Calling the real API in unit tests. LLM quality is measured by evals instead | `tests/` |
| D64 | Code and docs in English, the agent in Spanish/English | The deliverable is reviewed in English; candidates speak Spanish | n/a | |

## Changes after live testing (see [live testing log](../live-testing-log.md))

| # | Decision | Why | Rejected alternative / trade-off | Where |
|---|---|---|---|---|
| D65 | The writer (Sonnet 5.5) runs with thinking off (`between_tools`) | Measured 1.3 s vs 6.0 s median, and better instruction-following, for one-line messages from explicit instructions | Adaptive thinking at low effort. Model-gated: other models reject `between_tools` | `llm/claude.py: THINKING_OFF_MODELS` |
| D66 | Understanding (Haiku 5.5) keeps adaptive thinking at effort `low` | Disabling it made no measurable difference (1.9 s both); docs recommend low effort over disabling | Thinking disabled | `llm/claude.py` |
| D67 | Experience is extracted as total **months** (int); years derived by code | "8 meses" became 0.5 years and the recap said "6 meses": the model rounds, code doesn't | Years as a float from the model | `schemas.Extracted`, `validators.validate_experience_months` |
| D68 | The writer gets the name only when it was just learned and in the final message, and is told "don't use the name" otherwise | A rule in the system prompt alone didn't stop "Perfecto, Lucía" in every message | Trusting the system prompt | `policy._done`, `prompts.render_directive` |
| D69 | Gender-neutral Spanish, in candidate messages and recruiter summaries; gender is never inferred from a name | "Lucía" → "repartidora" risks misgendering | Gendered wording from the name | `prompts.build_speak_system` |
| D70 | The writer may never claim it changed or corrected data | It once said "lo paso como 8" while the data was unchanged: only the engine changes data | n/a | `prompts.build_speak_system` |
| D71 | A language switch needs the model's "clear" signal **and** a deterministic function-word check not disagreeing | The model alone read "en la noche" and "full time y part time" as English | Model only (wrong switches), or code only (misses short English) | `text.function_word_language`, `policy._update_language` |
| D72 | Day/month dates: the model keeps the current year; code moves to next year only if > 60 days in the past, otherwise asks again | "el 1 de octubre" said on 21 Oct is a mistake, not a start date in 2027 | Model decides the year | `validators.resolve_start_date` |
| D73 | Recap shows the year when it isn't the current one; decimal comma in Spanish | "01/10" hid a 2027 date; "1.5 años" isn't Spanish | n/a | `recap.py` |
| D74 | Neutral Spanish (city unknown) uses "auto o moto" | "vehículo o moto" sounded wrong; "auto" is understood in Spain and Mexico | "coche" (Spain only), "carro" (Mexico only) | `copy.yaml`, `prompts.py` |
| D75 | FAQ entry for "can we do this in English?" | The answer is known; "the team will confirm" was unhelpful | n/a | `faq.yaml: language` |
| D76 | "Not a job offer" is a prohibition for the writer, not content | Phrased as content, it reached the candidate verbatim and sounded cold | n/a | `prompts.OUTCOME_FACTS` |

## Sentiment

| # | Decision | Why | Rejected alternative / trade-off | Where |
|---|---|---|---|---|
| D77 | Sentiment comes from the same understanding call, as 4 categories (neutral, positive, confused, frustrated) | Zero extra latency or cost; each category maps to a behaviour | A separate sentiment model, or a 0-1 score that changes nothing | `schemas.TurnAnalysis.sentiment` |
| D78 | Confused → simpler words and options; frustrated → brief empathy, shorter, "N questions left" (N computed by code) | Adjusting tone is what keeps a candidate from dropping off | One tone for everyone | `policy.TONE_BY_SENTIMENT`, `prompts.TONE_HINTS` |
| D79 | Sentiment changes the tone only, never eligibility or ordering | Fairness: a frustrated candidate must not be penalised or favoured | Using it as a screening signal. Limitation: per message, no trend over the conversation yet | `policy.decide` |

## After the screening ends

| # | Decision | Why | Rejected alternative / trade-off | Where |
|---|---|---|---|---|
| D80 | After the end: questions always answered; small talk gets at most one courtesy reply, then silence | Without it, "bye" / "ok" / "👍" got a reply each, forever (found in manual testing): annoying and a paid call per message | Replying to everything, or never replying (questions would go unanswered) | `policy._after_end` |
| D81 | New information after the end (e.g. "I just got my licence") is acknowledged and flagged for a recruiter, not re-evaluated by the bot | Reopening a closed decision is a human call; the candidate still gets a response | Automatically re-running the screening. Trade-off: the summary generated at the end becomes stale (to regenerate on this flag) | `policy._after_end`, flag `update_after_close` |

## Recruiter tool, API and data (see [ADR 0008](0008-api-first-recruiter-tool.md))

| # | Decision | Why | Rejected alternative / trade-off | Where |
|---|---|---|---|---|
| D82 | One API, two route groups: `/conversations` (channels) and `/candidates` + `/analytics` (recruiters) | Channels and recruiters are different audiences with different contracts; OpenAPI docs come for free (ATS starting point) | One flat API | `api/app.py` |
| D83 | The dashboard is a client of the API, never of the database | Logic in one place; the API is exercised by real use; it is how an ATS would integrate | Streamlit reading SQLite directly: one process fewer | `dashboard/client.py` |
| D84 | Streamlit for the recruiter UI | Built in a day, all Python, every line explainable; the evaluation focuses on the backend | React: nicer and multi-user ready, much more code. Swappable later without touching the core | ADR 0008 |
| D85 | UI in English; AI summaries in the recruiters' language (Spanish, configurable) | The take-home is reviewed in English; summaries are for the client's recruiters | Spanish UI (right for production) | `dashboard/`, `client.yaml` |
| D86 | Human decisions in a separate `reviews` table | What the bot decided and what a person decided must never be confused | A status column on the conversation | `repository.ReviewRow` |
| D87 | A recruiter can override any automated outcome; overrides are logged as `human_override` events and counted in analytics | Human oversight (EU AI Act, GDPR art. 22) made visible in the product | Bot decisions as final | `Repository.set_review` |
| D88 | Queue order: qualified and not yet handled first, then needs review, then in progress; within a group, soonest start date first | Recruiter time goes where it converts | Chronological order | `views.build_rows` |
| D89 | "Abandoned" = no reply for 2 hours, derived at read time | Until follow-ups exist, a silent candidate must not look "in progress" forever | Storing the status (would need a job to update it) | `views.ABANDON_AFTER` |
| D90 | The model's analysis is never returned to channels unless `debug=true` | Candidates must not see internal reasoning; the demo chat and dashboard opt in | Always returning it | `send_message(debug=...)` |
| D91 | Summaries are written in a background task after the reply, regenerated when new information arrives after the end, and on demand | Never on the candidate's hot path; never stale | Synchronous summary (+10 s for the last message) | `api/app.py`, dashboard button |
| D92 | Analytics computed in Python from states, messages and events | Simple and tested at pilot scale | SQL views / warehouse (the plan at 10K/week) | `analytics.py` |
| D93 | Charts: single-series bars in one validated colour, value at the tip, tooltip, table toggle; statuses always icon + label | Readable, accessible, honest; colour never carries meaning alone | Colour per category, pie charts | `dashboard/ui.py` |
| D94 | Right to erasure: one call deletes state, transcript, events and review | The FAQ promises it; GDPR requires it | Soft delete. Trade-off: no tombstone record is kept | `DELETE /candidates/{id}`, dashboard |
| D95 | Demo data generated by running scripted candidates through the real engine at simulated times; the engine uses one injectable clock | Demo data that behaves like production; abandoned candidates can be shown | Hand-written fixtures (would not prove anything) | `scripts/seed_demo.py`, `engine.clock` |
| D96 | Sample conversations exported from the database, with highlights derived from the event log | Samples are real and self-describing; no hand-written labels to drift | Copy-pasted transcripts | `scripts/export_samples.py` |
| D97 | A language switch needs the function-word check to confirm the new language, or a message of at least 4 words with no signal | "full time" alone (a common loanword in Spain) switched the agent to English (refines D71) | D71's "not contradicting" rule | `policy._update_language` |
| D98 | `make run` starts API and dashboard together | One command for evaluators | Two terminals | `scripts/run.py` |

## Re-engagement (the 60% no-answer problem)

| # | Decision | Why | Rejected alternative / trade-off | Where |
|---|---|---|---|---|
| D99 | Follow-ups at +2 h, +24 h, +72 h after the candidate's last message; abandoned 24 h after the last one | Same day, next day, and a last chance, then stop: persistent but not spammy | More reminders (annoying, WhatsApp quality rating drops) or one (gives up too early) | `client.yaml: followups` |
| D100 | Follow-ups are fixed templates that repeat the pending question | WhatsApp only allows pre-approved templates > 24 h after the candidate's last message; repeating the question makes a one-word reply enough | LLM-written reminders: not allowed on WhatsApp outside the window, and unnecessary | `copy.yaml: followup`, `followups.render` |
| D101 | Quiet hours 21:00–09:00 in the candidate's timezone | Spain and Mexico are 7–8 h apart: a "morning" message from Madrid wakes a candidate in Monterrey | Server-time quiet hours. Limitation: before the city is known the default timezone is used; production would use the city of the application | `followups.next_action` |
| D102 | At most one follow-up per run, spaced as scheduled even after downtime | A scheduler restart must not fire three reminders in a row | Sending whatever is due | `followups.due_at` |
| D103 | "Abandoned" is not terminal: any reply resumes where they stopped and resets the counters | Candidates come back days later; turning them away would waste the recovery | A terminal abandoned stage | `engine._handle` (`resumed` event) |
| D104 | Recovery rate (replied after a follow-up / received one) is the re-engagement KPI, with "which reminder brought them back" | It measures the 60% problem directly and tells which reminder is worth keeping | Counting messages sent | `analytics.py` |
| D105 | Pilot scheduler: a loop in the API every 60 s | Zero infrastructure for a pilot | Production: one scheduled job (or delayed tasks) with a unique (conversation, attempt) constraint, since several API workers would double-send | `api._followup_loop` |
| D106 | Demo clock: moves time forward for the whole system (persisted offset), hour by hour, running the scheduler at each step; only with `SCREENER_DEMO_TOOLS=1` | Shows days of follow-ups in seconds without faking data | Rewriting timestamps (history would lie) | `engine/clock.py`, `/demo/*` |
| D107 | "Awaiting reply" (silent > 2 h or follow-ups under way) is distinct from "abandoned"; completion rate = finished / (finished + abandoned) | Waiting candidates are not lost yet and must not count as failures | One "abandoned" bucket after 2 h (D89, superseded) | `views.display_status`, `analytics.py` |
| D108 | Opening "Try the agent" doesn't create a conversation; only the button does | Visiting the page was creating empty candidates that then received follow-ups | Auto-start | `dashboard/views/chat.py` |
