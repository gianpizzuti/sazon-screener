# p06_licence_in_progress

> Sergio, in Sevilla. He is studying for his licence and has the exam in December. Would like to be contacted later.

**Expected:** disqualified · **Got:** disqualified (license_in_progress) · **Checks:** all passed

| | Message | |
|---|---|---|
| **Sofía** | ¡Hola! 👋 Soy Sofía, la asistente virtual (IA) de Grupo Sazón. Te escribo por tu solicitud como repartidor/a: son 7 preguntas rápidas, unos 3 minutos. Tus datos solo se usan para este proceso de selección. ¿Empezamos? | `template` |
| *Candidate* | Hola Sofía! Sí, vale, empezamos | smalltalk,affirm |
| **Sofía** | ¡Genial, empezamos! ¿Cómo te llamas? Nombre y apellido, por favor. | `llm` |
| *Candidate* | Sergio Blanco | provide_info · full_name=Sergio Blanco |
| **Sofía** | Encantada, Sergio. ¿Tienes carnet de conducir en vigor, ya sea de coche o de moto? | `llm` |
| *Candidate* | No todavía, estoy estudiando para sacarmelo. Tengo el examen en diciembre | provide_info,deny · drivers_license=in_progress |
| **Sofía** | Gracias por contármelo, Sergio, y mucho ánimo con el examen de diciembre. Para este puesto hace falta tener ya el carnet en vigor, así que ahora mismo no podemos seguir adelante con la solicitud. ¿Quieres que guardemos tus datos para contactarte cuando lo tengas? | `llm` |
| *Candidate* | Sí, por favor. Cuando saque el carnet en diciembre os escribo yo, o si preferís, me podéis escribir a partir de enero | affirm,provide_info,postpone |
| **Sofía** | Perfecto, Sergio, guardamos tus datos y te avisamos a partir de enero. Si prefieres escribirnos tú cuando tengas el carnet, también puedes hacerlo. ¡Gracias por tu interés en Grupo Sazón y mucha suerte con el examen! | `llm` |
| *Candidate* | Vale, muchas gracias Sofía! Ya os escribiré. Un saludo | smalltalk,postpone |
| **Sofía** | ¡Gracias a ti, y hablamos en cuanto tengas el carnet! Un saludo 😊 | `llm` |

**Screening data:** `{"full_name": "Sergio Blanco", "has_drivers_license": false, "license_status": "in_progress"}`

**Recruiter summary:** Descartado/a en la segunda pregunta por no tener aún carnet de conducir: está preparándolo y tiene el examen en diciembre. Aceptó que se guarden sus datos y pidió contacto a partir de enero (o escribirá cuando obtenga el carnet). No se recogieron zona, disponibilidad, horario, experiencia ni fecha de inicio.

**Judge:** warmth 5/5 · clarity 5/5 · brevity 5/5 · language 5/5 · honesty 4/5 · handling 4/5 · summary_faithful 5/5
- Message 9 commits to a specific follow-up window ("te avisamos a partir de enero") that may not be an official next step.
