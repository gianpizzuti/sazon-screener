# p06_licence_in_progress

> Sergio, in Sevilla. He is studying for his licence and has the exam in December. Would like to be contacted later.

**Expected:** disqualified · **Got:** disqualified (license_in_progress) · **Checks:** all passed

| | Message | |
|---|---|---|
| **Sofía** | ¡Hola! 👋 Soy Sofía, la asistente virtual (IA) de Grupo Sazón. Te escribo por tu solicitud como repartidor/a: son 7 preguntas rápidas, unos 3 minutos. Tus datos solo se usan para este proceso de selección. ¿Empezamos? | `template` |
| *Candidate* | Hola Sofía! Sí, vale, empezamos | smalltalk,affirm |
| **Sofía** | ¡Genial, empezamos entonces! ¿Cómo te llamas? Nombre y apellido, por favor. | `llm` |
| *Candidate* | Sergio Blanco | provide_info · full_name=Sergio Blanco |
| **Sofía** | Encantada, Sergio. Vamos con la primera pregunta: ¿tienes carnet de conducir en vigor, ya sea de coche o de moto? | `llm` |
| *Candidate* | No, todavía no lo tengo. Estoy estudiando para sacarlo, el examen es en diciembre | provide_info,deny · drivers_license=in_progress |
| **Sofía** | Gracias por contármelo, Sergio, y mucho ánimo con el examen de diciembre. Para este puesto hace falta tener ya el carnet en vigor, así que de momento no podemos seguir con el proceso. ¿Quieres que guardemos tus datos para contactarte cuando lo tengas? | `llm` |
| *Candidate* | Sí, por favor. Guárdalos y cuando tenga el carnet me escriben de nuevo. Gracias Sofía | affirm,provide_info,smalltalk |
| **Sofía** | Hecho, Sergio: lo anotamos para que el equipo de selección se ponga en contacto contigo cuando tengas el carnet. Gracias por tu tiempo y mucha suerte en diciembre. 🚗 | `llm` |

**Screening data:** `{"full_name": "Sergio Blanco", "has_drivers_license": false, "license_status": "in_progress"}`

**Recruiter summary:** Descartado/a en la primera pregunta: no tiene carnet de conducir en vigor (lo está sacando, examen previsto en diciembre). No se recogieron más datos. Pidió que se guarden sus datos para recontactar cuando tenga el carnet.

**Judge:** warmth 5/5 · clarity 5/5 · brevity 5/5 · language 5/5 · honesty 4/5 · handling 4/5 · summary_faithful 5/5
- Message 9 "lo anotamos para que el equipo de selección se ponga en contacto contigo cuando tengas el carnet" implies the company will know when he gets the licence; this is a soft overpromise.
- Message 5 says "Vamos con la primera pregunta" after the name question was already asked, a minor inconsistency with the "7 preguntas" framing.
