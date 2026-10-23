# Process design: Grupo Sazón delivery-driver screening

A chat agent that screens every applicant seconds after they apply, so recruiters only spend time on qualified people. Details and examples: [appendix](process-design-appendix.md); every decision and its trade-off: [decision log](decisions/decision-log.md).

## 1. Two problems, two mechanisms

| Client problem | Root cause | Mechanism |
|---|---|---|
| 60% don't answer calls | **Channel and timing**: couriers ignore unknown numbers at work; no time to retry | Asynchronous chat, answered when it suits them, with reminders |
| 80% of recruiter time on unqualified people | **Late filtering**: the licence or area problem appears minutes into a call | Knock-outs first; recruiters get only qualified or flagged candidates, with a summary |

Pilot metrics: completion rate, time to screen, recovery after reminders, drop-off by stage.

## 2. Stages and branching

```
INTRO   AI disclosure + privacy note, "¿Empezamos?"
NAME → LICENCE ──no / in progress / type not accepted──► DISQUALIFIED → talent-pool opt-in
         │ yes
       CITY ──outside the service areas──► DISQUALIFIED → talent-pool opt-in
         │ inside
       ZONE (optional, buttons) → AVAILABILITY → SHIFT → EXPERIENCE (→ platforms) → START DATE
         │
       RECAP ──correction──► update, knock-outs checked again, recap again
         │ confirmed
       QUALIFIED → picks an interview time in the chat (3 buttons; none fits twice → a recruiter)
       NEEDS REVIEW if a knock-out stayed unclear, or a licence from abroad needs checking
```

- **Knock-outs first**: an ineligible candidate knows within a minute (trade-off: it can feel like an interrogation, so the tone compensates).
- **Slot filling, not a form**: "soy Ana, tengo carnet, vivo en Getafe" answers three questions at once.
- **One checkpoint**: the recap; any correction re-runs the knock-outs.
- **At any stage**: questions are answered, then the flow resumes; "not now" pauses; opt-out stops; a request for a person is flagged; abuse gets one warning, then the chat closes.

## 3. Personality

**Sofía**, Grupo Sazón's virtual assistant, says she is an AI from the first message. Warm, direct and efficient, like a friendly shift manager who respects people's time; never salesy, robotic or formal. *Tú*, the candidate's language, and Spain's or Mexico's vocabulary once the city is known.

## 4. Fields and validation

| Field | Valid when | If invalid or ambiguous | Knock-out |
|---|---|---|---|
| Full name | first name and surname | surname asked once | – |
| Driver's licence | clear yes/no; car, motorbike or both | vague → asked again; "sí" alone → type asked once; from abroad → the hiring country's law | no, in progress, type not accepted |
| City | a configured service area (aliases, typos) | ambiguous → options; unknown → asked again | outside the areas |
| Zone | a delivery zone of that city | buttons; an unserved neighbourhood → the closest zones | – |
| Availability | full-time, part-time, weekends | full- and part-time together → which one | – |
| Shift | morning, afternoon, evening, flexible | asked again with the options | – |
| Experience | months as said, and platforms | no duration → asked | – |
| Start date | today or later (> 90 days: flagged) | vague → approximate date; past → asked again | – |

**Rules.** Every value must quote the candidate's words, or it is discarded. The model reads "el lunes que viene"; code computes the date and decides eligibility. No loops: after 2 failed answers, or 3 asks answered with other things, a field is *unclear*, flagged, and the chat moves on.

## 5. Edge cases

- **Stops responding.** Reminders at +2 h, +24 h, +72 h, never 21:00–09:00 in the *candidate's* timezone. Fixed templates (WhatsApp's 24-hour rule) that repeat the pending question; then *abandoned*, with the drop-off stage recorded. Any reply resumes where they left off.
- **Invalid or ambiguous.** Asked again with the reason and options ("¿Centro de qué ciudad?"), never guessed. "Apruébame" changes nothing: rules decide.
- **Language switch.** Reply in the latest message's language, with hysteresis: "ok", "sí", names and numbers never switch it. Before the city, one Spanish for both countries.
- **Questions.** Only from the client's approved knowledge base; otherwise "the team will confirm", logged. Pay is never invented.
- **Failures.** Retry, then a template: the conversation never breaks.

## 6. Outcomes

| Outcome | The candidate | The recruiter |
|---|---|---|
| **Qualified** | books the interview in the chat | summary, data and the booked time |
| **Qualified + flag** | the same | the reason (asked for a person, licence to exchange…) |
| **Needs review** | "someone from the team will contact you" | review queue with the reason |
| **Disqualified** | the reason, kindly, and a talent-pool opt-in | the reason; can override |
| **Withdrawn / abandoned** | a confirmation / nothing | archived / drop-off stage |

A person can review every outcome: recruitment AI is high-risk under the EU AI Act (and GDPR art. 22).

## 7. Tone and length (this is chat, not email)

1–3 short sentences, **≤ 350 characters**, **one question at the end**, a brief acknowledgement first. Plain text, ≤ 1 emoji, quick-reply buttons for closed questions. Never promise a job, invent pay, ask about age, nationality, health or family, or guilt-trip someone who leaves.

✅ "Perfecto, Ana. ¿Tienes carnet de conducir en vigor?"  
❌ "¡Muchas gracias por tu respuesta, Ana! Ahora, para poder continuar con el proceso de selección, necesitaría saber si dispones de…"

## 8. Open questions for Grupo Sazón

Each has an assumption kept as configuration ([appendix](process-design-appendix.md#8-assumptions-and-open-questions-for-grupo-sazón)): e-bikes without a licence (not accepted, as specified) · licence types (car and motorbike) · licences from abroad (the hiring country's law, to confirm with legal) · "zone" (where they'd work) · interviews (one restaurant per city, weekdays) · pay and benefits (placeholders) · data retention and talent-pool consent (legal review).
