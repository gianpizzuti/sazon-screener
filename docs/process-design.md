# Process Design: Delivery-Driver Screening for Grupo Sazón

A conversational agent screens every applicant within seconds of applying, so that recruiters spend their time only on qualified candidates. Details and examples are in the [appendix](process-design-appendix.md); decisions and trade-offs are in the [decision log](decisions/decision-log.md).

## 1. Problems and Mechanisms

| Client problem | Root cause | Mechanism |
|---|---|---|
| 60% of candidates do not answer calls | **Channel and timing**: couriers ignore unknown numbers at work; recruiters cannot retry | Asynchronous chat with automatic reminders |
| 80% of recruiter time is spent on unqualified candidates | **Late filtering**: licence or location issues emerge minutes into a call | Knock-out questions first; recruiters receive only qualified or flagged candidates |

Pilot metrics: completion rate, time to screen, recovery rate after reminders, and drop-off by stage.

## 2. Conversation Stages and Branching

```
INTRO   AI disclosure and privacy notice
NAME → LICENCE ──no / in progress / type not accepted──► DISQUALIFIED → talent-pool opt-in
         │ yes
       CITY ──outside the service areas──► DISQUALIFIED → talent-pool opt-in
         │ inside
       ZONE (optional) → AVAILABILITY → SHIFT → EXPERIENCE (→ platforms) → START DATE
         │
       RECAP ──correction──► update, knock-outs re-evaluated, recap repeated
         │ confirmed
       QUALIFIED → interview booked in the chat (three options; a recruiter intervenes if none fits)
       NEEDS REVIEW if a knock-out answer remains unclear or a foreign licence requires verification
```

- **Knock-outs first.** An ineligible candidate learns the outcome within one minute; the tone compensates for a more direct opening.
- **Slot filling rather than a form.** "Soy Ana, tengo carnet, vivo en Getafe" answers three questions at once.
- **A single checkpoint.** The recap shows all data once; corrections re-evaluate the knock-outs.
- **Interruptions.** Questions are answered and the flow resumes; pauses are honoured; an opt-out ends the conversation; a request for a person is flagged; abuse receives one warning, then the chat closes.

## 3. Agent Personality

**Sofía**, Grupo Sazón's virtual assistant, discloses that she is an AI in her first message. She is warm, direct and efficient, like a considerate shift manager, and never promotional or robotic. She uses *tú*, replies in the candidate's language, and adopts Spanish or Mexican vocabulary once the city is known.

## 4. Data Fields and Validation

| Field | Valid when | Invalid or ambiguous answer | Knock-out |
|---|---|---|---|
| Full name | First name and surname | The surname is requested once | No |
| Driver's licence | Clear yes or no; car, motorbike or both | Asked again if vague; type asked once; foreign licences follow the hiring country's law | No, in progress, or type not accepted |
| City | A configured service area | Options if ambiguous; asked again if unknown | Outside the service areas |
| Zone | A delivery zone of that city | Unserved neighbourhood: closest zones offered | No |
| Availability | Full-time, part-time, weekends | Contradictions clarified | No |
| Shift | Morning, afternoon, evening, flexible | Asked again with the options | No |
| Experience | Duration in months and platforms | Missing duration requested | No |
| Start date | Today or later (over 90 days: flagged) | Approximate date requested if vague or past | No |

**Rules.** Every value must quote the candidate's own words, or it is discarded. The model interprets "el lunes que viene"; code computes the date and decides eligibility. After two failed answers, or three requests answered with other information, a field is flagged as *unclear* and the conversation continues.

## 5. Edge Cases

- **The candidate stops responding.** Reminders after 2, 24 and 72 hours, never between 21:00 and 09:00 in the candidate's time zone, as fixed templates (WhatsApp's 24-hour rule) that repeat the pending question. The conversation is then marked as abandoned, with the drop-off stage recorded; any later reply resumes it.
- **Invalid or ambiguous answers.** Repeated with the reason and options ("¿Centro de qué ciudad?"), never guessed. Manipulation attempts have no effect, as rules decide eligibility.
- **Language switching.** Replies follow the latest message's language, with hysteresis: "ok", "sí", names and numbers do not switch it. Before the city is known, neutral Spanish is used.
- **Candidate questions.** Answered only from the client's approved knowledge base; otherwise the team will confirm, and the question is logged.
- **Technical failures.** Retried, then replaced by a template: the conversation is never interrupted.

## 6. Outcomes

| Outcome | Candidate experience | Recruiter view |
|---|---|---|
| **Qualified** | Books the interview in the chat | Summary, data and the booked time |
| **Qualified with flag** | Same as qualified | The reason (e.g. a licence to exchange) |
| **Needs review** | Told that the team will make contact | Review queue with the reason |
| **Disqualified** | The reason, courteously, and a talent-pool opt-in | The reason; can override |
| **Withdrawn / abandoned** | A confirmation / no message | Archived / drop-off stage |

Every outcome can be reviewed by a person: recruitment AI is high-risk under the EU AI Act and subject to GDPR Article 22.

## 7. Message Tone and Length

One to three short sentences, at most 350 characters, ending with a single question after a brief acknowledgement. Plain text with at most one emoji; quick-reply buttons for closed questions; by voice, options are stated in words. The agent never promises a job, invents pay, asks about age, nationality, health or family, or pressures a candidate who leaves.

*Correct:* "Perfecto, Ana. ¿Tienes carnet de conducir en vigor?"

*Incorrect:* "¡Muchas gracias por tu respuesta, Ana! Ahora, para poder continuar con el proceso de selección, necesitaría saber si dispones de…"

## 8. Open Questions for Grupo Sazón

Each is answered by an assumption stored as configuration ([appendix](process-design-appendix.md#8-assumptions-and-open-questions-for-grupo-sazón)): the service areas (the brief gives none: 45 illustrative restaurants in nine cities); e-bikes without a licence (not accepted, as specified); accepted licence types (car and motorbike); foreign licences (the hiring country's law, to be confirmed by legal); "zone" (where the candidate would work); pay and benefits (placeholders); data retention and talent-pool consent (legal review).

**Interview capacity is the decision with the largest impact.** One interview location per city, on weekday mornings and afternoons, provides about 60 interviews a week per city. A volume test indicates that, at today's 1,000 applications a week, Mexico City, Barcelona and Madrid would need about 110, 84 and 83. The options (interviews at every restaurant, group sessions, a first interview by video) are business decisions for the client; the agent already hands unbooked candidates to a recruiter and reports how many.
