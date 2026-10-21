# p04_no_licence

> Marta, 19, in Valencia. She does not have a driving licence and has never had one. If offered to be kept for future openings, she accepts.

**Expected:** disqualified · **Got:** disqualified (no_license) · **Checks:** all passed

| | Message | |
|---|---|---|
| **Sofía** | ¡Hola! 👋 Soy Sofía, la asistente virtual (IA) de Grupo Sazón. Te escribo por tu solicitud como repartidor/a: son 7 preguntas rápidas, unos 3 minutos. Tus datos solo se usan para este proceso de selección. ¿Empezamos? | `template` |
| *Candidate* | Hola! Sí, empecemos 😊 | smalltalk,affirm |
| **Sofía** | ¡Genial, vamos allá! ¿Cómo te llamas? Nombre y apellido, por favor. | `llm` |
| *Candidate* | Marta Gil | provide_info · full_name=Marta Gil |
| **Sofía** | Gracias, Marta. Ahora una pregunta clave para el puesto: ¿tienes licencia de conducir en vigor (auto o moto)? | `llm` |
| *Candidate* | No, no tengo carnet de conducir. Nunca lo he sacado. | provide_info,deny · drivers_license=no |
| **Sofía** | Gracias por contármelo, Marta. Para el puesto de repartidor/a es imprescindible tener carnet de conducir en vigor, así que por ahora no podemos continuar con tu solicitud. ¿Quieres que guardemos tus datos para avisarte si surge alguna oportunidad en el futuro? | `llm` |
| *Candidate* | Vale, entiendo. Sí, guardadlos por favor, que si surge algo más adelante me interesa. | affirm,provide_info |
| **Sofía** | Hecho, Marta: guardamos tus datos y te avisaremos si surge alguna oportunidad en el futuro. Gracias por tu tiempo y por tu interés en Grupo Sazón. ¡Que te vaya muy bien! | `llm` |

**Screening data:** `{"full_name": "Marta Gil", "has_drivers_license": false, "license_status": "no"}`

**Recruiter summary:** Descalificación por no tener licencia de conducir (indica que nunca la ha obtenido). La entrevista terminó en la segunda pregunta, por lo que no se recogieron ubicación, disponibilidad, horario, experiencia ni fecha de inicio. Ha pedido que se guarden sus datos para futuras oportunidades.

**Judge:** warmth 5/5 · clarity 5/5 · brevity 5/5 · language 3/5 · honesty 4/5 · handling 5/5 · summary_faithful 5/5
- Message 5 uses Mexican terms "licencia de conducir" and "auto" instead of Spain's "carnet de conducir" and "coche" with a Valencia candidate.
- "te avisaremos si surge alguna oportunidad en el futuro" reads as a mild promise of future contact.
