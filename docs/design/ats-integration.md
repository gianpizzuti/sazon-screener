# Design: ATS integration

**Status:** design, not built. The API it builds on exists today; what is missing is marked **(to build)**.

Grupo Sazón's recruiters already work in an applicant tracking system (ATS). The screener should feel like part of it: an application in the ATS starts a screening within seconds, and the result comes back into the ATS without anyone copying data by hand.

## 1. Principles

| Decision | Why | Rejected alternative |
|---|---|---|
| **The ATS owns the application; the screener owns the conversation.** The ATS is the system of record for the candidate's lifecycle (applied → interviewed → hired). The screener is the system of record for the conversation, the screening data and its audit trail | Recruiters keep one place to work, and each system stays authoritative for what it is good at | Making the screener the recruiter's main tool (one more tool to adopt) |
| **One adapter per ATS behind one internal contract** | Every ATS models candidates, stages and custom fields differently; the engine must not know which one is on the other side | Integration code inside the engine (every new client would touch the core) |
| **Events out, never synchronous calls from the conversation** | The candidate must never wait for, or be broken by, the ATS | Calling the ATS at the end of a turn (an ATS outage would break screenings) |
| **A knock-out reaches the ATS as "screened out", and a person confirms the rejection** (the client can opt in to automatic rejection) | AI in recruitment is high-risk under the EU AI Act, and GDPR art. 22 limits purely automated decisions; a batch confirmation costs recruiters seconds, not a call | Rejecting automatically in the ATS by default |

## 2. The flow

```
 ATS                          Screener                                Candidate
  │ application created          │                                        │
  ├── webhook (or poll) ────────►│ POST /api/conversations                │
  │   ats_application_id,        │   idempotent on (client, ats_id)       │
  │   phone, country, location   ├── first message, within seconds ──────►│
  │                              │◄─────────────── answers ───────────────┤
  │                              │ screening runs (no ATS involved)       │
  │◄── outcome event ────────────┤ completed: outcome, data, summary      │
  │    stage + fields + note     │                                        │
  │                              │                                        │
  │ recruiter moves the stage    │                                        │
  ├── webhook ──────────────────►│ PUT /api/candidates/{id}/review        │
  │  (interview, hired, rejected)│   override logged if it contradicts    │
  │ candidate withdrawn / erased │                                        │
  ├── webhook ──────────────────►│ stop the conversation / DELETE         │
```

## 3. Inbound: from the ATS to the screener

| Item | Today | To build |
|---|---|---|
| Start a screening | `POST /api/conversations` with `channel`, `language`, `country` | **(to build)** `external_ref` (ATS application id), phone, restaurant/location id; **idempotent** on `(client, external_ref)`, so a webhook delivered twice never starts two conversations |
| Spain or Mexico Spanish from message one | `country` already sets the variant (D157) | Derive it from the location the candidate applied to |
| Start from the right place | – | **(to build)** pre-fill what the application already knows (name, city) as *known data*, so Sofía doesn't ask it again. The candidate still confirms it at the recap |
| Recruiter decisions made in the ATS | `PUT /api/candidates/{id}/review` (new, contacted, interview, hired, rejected) with audited override | **(to build)** map ATS stages to these statuses in the adapter |
| Withdrawal or erasure in the ATS | `DELETE /api/candidates/{id}` erases everything | **(to build)** inbound webhook that stops the conversation (withdrawal) or erases it (GDPR request) |

**Duplicates.** The same person often applies to two restaurants. The adapter looks up open conversations by phone number. If one is in progress, the new application is linked to it rather than starting a second screening. If one finished recently, its result is reused and the recruiter is told. A rule for the client to confirm: "recently" defaults to 30 days.

## 4. Outbound: from the screener to the ATS

**When.** On `completed`: qualified, needs review, disqualified or withdrawn. Optionally also on `abandoned`, and on `human_requested` so a recruiter can call.

**What, and how it maps.** The screening data is already structured (`ScreeningData`, `CandidateDetail`), so the mapping is configuration per client:

| Screener | Typical ATS target |
|---|---|
| Outcome (qualified / needs review / screened out / withdrawn) | Application stage |
| Knock-out reason (`no_license`, `license_in_progress`, `out_of_area`) | Rejection reason (after human confirmation, see §1) |
| Licence and type, city and zone, availability, shift, experience and platforms, start date | Custom fields, or structured tags if the ATS has no custom fields |
| Recruiter summary (Opus) | Note on the application |
| Flags (asked for a person, late start, unclear answer) and open questions | Tags plus a note |
| Talent-pool consent | Consent field or tag; it decides whether the profile can be kept after rejection |
| Link to the transcript in the screener | URL field. The transcript stays in the screener (data minimisation) |

**Delivery: transactional outbox (to build).**
1. The event is written to an `outbox` table **in the same transaction** as the turn that produced it. The engine already saves the state, the messages and the events in one transaction, so this is one more row.
2. A worker delivers outbox rows to the ATS adapter.
   - Retries with exponential backoff.
   - An idempotency key (`conversation_id` + event id), so a retry never creates two notes.
   - A dead-letter state plus an alert after N failures.
3. A nightly reconciliation compares the outcomes in both systems and re-sends what is missing.

*Why an outbox:* sending to the ATS right after committing can lose events (crash between the two steps), and sending before committing can report outcomes that never happened. The outbox makes delivery at-least-once, and the idempotency key makes it effectively once.

## 5. Security and privacy

- **Authentication (to build).** The API has no authentication today: it is a local demo. To add:
  - one key per client for the ATS adapter, stored in a secret manager;
  - signed inbound webhooks, verified with HMAC and a timestamp to stop replays;
  - SSO for recruiters in the web app.
- **Least data.** Only screening fields and the summary go to the ATS; the transcript stays in the screener behind a link. No sensitive categories are collected in the first place.
- **Erasure in both directions.** An erasure in either system propagates to the other, and the propagation is logged.
- **Data processing agreements.** One with the client, and one with the language-model provider, covering EU processing and retention.

## 6. Levels of integration (offer the client the cheapest one that works)

| Level | What | Effort | When |
|---|---|---|---|
| 0 | Recruiters use the screener's web app; nightly CSV/JSON export to the ATS | Days | Pilot, or an ATS without an API |
| 1 | Inbound webhook starts screenings; outbound outcome, fields and note via the ATS API | 2–3 weeks per ATS | Production |
| 2 | Two-way stage sync, duplicate linking, erasure propagation, reconciliation | +2 weeks | Several cities, recruiters working only in the ATS |

## 7. Questions for Grupo Sazón

1. **ATS and access.** Which ATS, and does its API offer webhooks, custom fields and notes?
2. **Who acts on screened-out candidates.** Do recruiters want to confirm each one, or accept automatic rejection for the objective knock-outs?
3. **Where recruiters work.** Only in the ATS, or also in the screener's app (transcripts, analytics)?
4. **Duplicates.** How long is a screening result valid for a second application?

## Revisit when

- **The ATS has no webhooks:** poll for new applications every minute. The idempotent start makes polling safe.
- **Several clients share one ATS vendor:** the adapter becomes a reusable connector, and the client's own mapping stays in its config folder.
