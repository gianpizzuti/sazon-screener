# Decision log

Every decision taken while building the agent, large or small (76 so far), with the reason and the alternative that was rejected. The big ones have a full ADR (linked). This is a living document, updated with every decision.

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
| D69 | Gender-neutral Spanish; gender is never inferred from a name | "Lucía" → "repartidora" risks misgendering | Gendered wording from the name | `prompts.build_speak_system` |
| D70 | The writer may never claim it changed or corrected data | It once said "lo paso como 8" while the data was unchanged: only the engine changes data | n/a | `prompts.build_speak_system` |
| D71 | A language switch needs the model's "clear" signal **and** a deterministic function-word check not disagreeing | The model alone read "en la noche" and "full time y part time" as English | Model only (wrong switches), or code only (misses short English) | `text.function_word_language`, `policy._update_language` |
| D72 | Day/month dates: the model keeps the current year; code moves to next year only if > 60 days in the past, otherwise asks again | "el 1 de octubre" said on 21 Oct is a mistake, not a start date in 2027 | Model decides the year | `validators.resolve_start_date` |
| D73 | Recap shows the year when it isn't the current one; decimal comma in Spanish | "01/10" hid a 2027 date; "1.5 años" isn't Spanish | n/a | `recap.py` |
| D74 | Neutral Spanish (city unknown) uses "auto o moto" | "vehículo o moto" sounded wrong; "auto" is understood in Spain and Mexico | "coche" (Spain only), "carro" (Mexico only) | `copy.yaml`, `prompts.py` |
| D75 | FAQ entry for "can we do this in English?" | The answer is known; "the team will confirm" was unhelpful | n/a | `faq.yaml: language` |
| D76 | "Not a job offer" is a prohibition for the writer, not content | Phrased as content, it reached the candidate verbatim and sounded cold | n/a | `prompts.OUTCOME_FACTS` |
