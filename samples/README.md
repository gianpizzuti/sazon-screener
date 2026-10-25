# Sample conversations

Real conversations with the agent (real models, real policy, generated on 2026-10-25), produced by `scripts/seed_demo.py` and exported by `scripts/export_samples.py`. Each file shows the transcript, the structured data extracted and the recruiter summary.

| Sample | Outcome | What it shows |
|---|---|---|
| [Lucía Fernández](01-lucia-fernandez-qualified.md) | ✅ Qualified | books the interview in the chat |
| [Michael Torres](02-michael-torres-qualified.md) | ✅ Qualified | talks in English from the start; books the interview in the chat |
| [Juan Pérez](03-juan-perez-qualified.md) | ✅ Qualified | gives several answers in one message: those questions are skipped; books the interview in the chat; Mexican Spanish vocabulary |
| [Carla Méndez](04-carla-mendez-qualified.md) | ✅ Qualified | sends off-script messages (non-answers or attempts to steer the agent): no effect on the outcome; asks a question answered from the FAQ; gets frustrated: empathy and remaining-question count; finds no interview time that fits: a recruiter takes over |
| [Ana Torres](05-ana-torres-qualified.md) | ✅ Qualified | gives an invalid or ambiguous answer, asked again; corrects an answer; says a detail is wrong at the recap, the field is asked again; books the interview in the chat |
| [Marta Gil](06-marta-gil-disqualified.md) | ⛔ Disqualified | is knocked out (no license); answers the talent-pool opt-in |
| [Pedro Ruiz](07-pedro-ruiz-disqualified.md) | ⛔ Disqualified | is knocked out (out of area); answers the talent-pool opt-in |
| [Sergio Blanco Ruiz](08-sergio-blanco-ruiz-needs_review.md) | ⚠️ Needs review | sends off-script messages (non-answers or attempts to steer the agent): no effect on the outcome; stays unclear after two attempts: flagged, the conversation moves on |
| [Iván Morales](09-ivan-morales-qualified.md) | ✅ Qualified | names a neighbourhood without a delivery zone: the closest zones are offered; books the interview in the chat |
| [Samira El Idrissi](10-samira-el-idrissi-qualified.md) | ✅ Qualified | has a licence from a country with an exchange agreement: qualified, with a note to exchange it; asks a question answered from the FAQ; books the interview in the chat |
| [Laura Gómez](11-laura-gomez-qualified.md) | ✅ Qualified | asks for a human: flagged, screening continues; books the interview in the chat |
| [Andrés Pérez](12-andres-perez-needs_review.md) | ⚠️ Needs review | asks a question answered from the FAQ; has a licence from a country without an exchange agreement: a person decides |
| [Giulia Rossi](13-giulia-rossi-qualified.md) | ✅ Qualified | asks a question answered from the FAQ; books the interview in the chat; moves the interview to another time |
| [Diego Navarro](14-diego-navarro-qualified.md) | ✅ Qualified | books the interview in the chat; starts in more than 90 days: flagged |
| [Raúl Ortega](15-raul-ortega-withdrawn.md) | ↩️ Withdrawn | withdraws: accepted gracefully, can come back anytime |
| [Nerea Iglesias](16-nerea-iglesias-awaiting_reply.md) | 💬 Awaiting reply | stops replying at availability: reminders are scheduled (the demo clock shows them) |
| [Óscar Medina](17-oscar-medina-awaiting_reply.md) | 💬 Awaiting reply | stops replying at experience years: reminders are scheduled (the demo clock shows them); Mexican Spanish vocabulary |
| [Tom Becker](18-tom-becker-qualified.md) | ✅ Qualified | talks in English from the start; asks a question answered from the FAQ; books the interview in the chat |
| [Andrés Gil](19-andres-gil-qualified.md) | ✅ Qualified | talks by voice (transcribed speech): same engine, spoken replies; books the interview in the chat |
