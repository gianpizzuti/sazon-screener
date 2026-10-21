# p04_no_licence

> Marta, 19, in Valencia. She does not have a driving licence and has never had one. If offered to be kept for future openings, she accepts.

**Expected:** disqualified · **Got:** disqualified (no_license) · **Checks:** all passed

| | Message | |
|---|---|---|
| **Sofía** | ¡Hola! 👋 Soy Sofía, la asistente virtual (IA) de Grupo Sazón. Te escribo por tu solicitud como repartidor/a: son 7 preguntas rápidas, unos 3 minutos. Tus datos solo se usan para este proceso de selección. ¿Empezamos? | `template` |
| *Candidate* | ¡Hola! Sí, empecemos 😊 | smalltalk,affirm |
| **Sofía** | ¡Genial, empezamos! ¿Cómo te llamas? Nombre y apellido, por favor. | `llm` |
| *Candidate* | Marta Gil | provide_info · full_name=Marta Gil |
| **Sofía** | Encantada, Marta. ¿Tienes carnet de conducir en vigor, ya sea de coche o de moto? | `llm` |
| *Candidate* | No, no tengo carnet de conducir. Nunca lo he tenido. | provide_info,deny · drivers_license=no |
| **Sofía** | Gracias por tu sinceridad, Marta. Para este puesto de repartidor/a es imprescindible tener carnet de conducir en vigor, así que no podemos continuar con tu solicitud por ahora. ¿Quieres que guardemos tus datos para avisarte si surgen otras vacantes en el futuro? | `llm` |
| *Candidate* | Sí, por favor, guárdenlos. Gracias por avisarme. | affirm,smalltalk |
| **Sofía** | Hecho, Marta: tus datos quedan guardados y te avisaremos si surge otra vacante. Gracias por tu tiempo y mucha suerte 🙂 | `llm` |

**Screening data:** `{"full_name": "Marta Gil", "has_drivers_license": false, "license_status": "no"}`

**Recruiter summary:** Descartada en el cribado por no tener carnet de conducir (nunca lo ha tenido), requisito imprescindible para el puesto. La conversación terminó tras la segunda pregunta, por lo que no hay datos de zona, disponibilidad, experiencia ni fecha de inicio. Ha pedido que se guarden sus datos para futuras vacantes.

**Judge:** warmth 5/5 · clarity 5/5 · brevity 5/5 · language 5/5 · honesty 5/5 · handling 5/5 · summary_faithful 5/5
