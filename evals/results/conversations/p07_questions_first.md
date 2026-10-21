# p07_questions_first

> Carmen, careful and curious. Before her first answer she asks how much the job pays. Later, when asked where she lives, she first asks whether she needs her own motorbike. Before giving her shift she asks whether there is parking for the motorbike at the restaurant. She answers everything else.

**Expected:** qualified · **Got:** qualified · **Checks:** all passed

| | Message | |
|---|---|---|
| **Sofía** | ¡Hola! 👋 Soy Sofía, la asistente virtual (IA) de Grupo Sazón. Te escribo por tu solicitud como repartidor/a: son 7 preguntas rápidas, unos 3 minutos. Tus datos solo se usan para este proceso de selección. ¿Empezamos? | `template` |
| *Candidate* | Hola Sofía, buenas tardes. Sí, empecemos. Antes de nada, ¿cuánto se paga por el puesto? Me gustaría saberlo para decidir si me compensa. | affirm,question,smalltalk |
| **Sofía** | Claro, es normal querer saberlo. Es un contrato laboral con Grupo Sazón (no como autónomo), con el salario del convenio de hostelería de tu provincia, más propinas. El importe exacto según horas te lo confirma el equipo en la entrevista. ¿Cómo te llamas? Nombre y apellido, por favor. | `llm` |
| *Candidate* | Gracias por la aclaración. Me llamo Carmen Vidal. | provide_info · full_name=Carmen Vidal |
| **Sofía** | Encantada, Carmen. Seguimos con la siguiente: ¿tienes licencia de conducir en vigor (auto o moto)? | `llm` |
| *Candidate* | Sí, tengo el carnet de moto en vigor. | provide_info,affirm · drivers_license=yes |
| **Sofía** | Perfecto, gracias. ¿En qué ciudad y zona te gustaría repartir? | `llm` |
| *Candidate* | Vivo en Sevilla, en Triana. Antes de contestar lo de la zona, quería saber: ¿necesito tener mi propia moto para este puesto? | provide_info,question · location_text=Sevilla, en Triana, location_city_id=sevilla, location_zone=Triana, location_outside_service_area=False |
| **Sofía** | Anotado, Sevilla y Triana. Puedes repartir con tu propia moto o coche y te compensamos el combustible por kilómetro. En algunos restaurantes también hay motos de la empresa, y el equipo te lo confirma según tu zona. ¿Qué disponibilidad tienes: jornada completa, media jornada o fines de semana? | `llm` |
| *Candidate* | Media jornada, por favor. Preferiría turnos de mañanas. | provide_info · availability=['part_time'], schedule=['morning'] |
| **Sofía** | Perfecto, media jornada en turno de mañanas, lo dejo anotado. ¿Tienes experiencia como repartidor/a? Si es así, ¿cuánto tiempo y en qué plataformas? | `llm` |
| *Candidate* | No, ninguna. Nunca he trabajado como repartidora. | provide_info,deny · experience_months=0 |
| **Sofía** | Vale, sin problema, gracias por decírmelo. ¿Cuándo podrías empezar? | `llm` |
| *Candidate* | Podría empezar dentro de dos semanas. | provide_info · start_date={'kind': 'in_weeks', 'amount': 2, 'weekday': None, 'exact_date': None} |
| **Sofía** | Antes de terminar, revisa tus datos:<br>• Nombre: Carmen Vidal<br>• Carnet de conducir: Sí<br>• Zona: Sevilla (Triana)<br>• Disponibilidad: media jornada<br>• Turno: mañana<br>• Experiencia: Sin experiencia previa<br>• Inicio: martes 03/11<br><br>¿Está todo correcto? | `template` |
| *Candidate* | Casi todo está bien, pero hay un par de cosas que quiero dejar claras. Lo del carnet: tengo el de moto, no el de coche, así que si el puesto requiere carnet B, lo tendrás que revisar. Y lo del inicio: yo dije "dentro de dos semanas", es decir, sobre el 3 de noviembre, así que la fecha me vale. Antes de confirmar, ¿podéis indicarme si en el restaurante donde trabajaría hay aparcamiento para la moto? | correction,provide_info,question · drivers_license=yes, start_date={'kind': 'in_weeks', 'amount': 2, 'weekday': None, 'exact_date': None} |
| **Sofía** | Gracias por precisarlo: tienes el carnet de moto en vigor y puedes empezar sobre el martes 3/11, dentro de dos semanas, y así queda reflejado. Lo del aparcamiento para la moto en el restaurante no lo sé, el equipo de selección te lo confirmará. | `llm` |
| **Sofía** | Antes de terminar, revisa tus datos:<br>• Nombre: Carmen Vidal<br>• Carnet de conducir: Sí<br>• Zona: Sevilla (Triana)<br>• Disponibilidad: media jornada<br>• Turno: mañana<br>• Experiencia: Sin experiencia previa<br>• Inicio: martes 03/11<br><br>¿Está todo correcto? | `template` |
| *Candidate* | Sí, todo correcto. Solo una cosa más: como tengo carnet de moto y no de coche, quiero confirmar que el puesto acepta repartir en moto. Si es así, de acuerdo; si no, prefiero saberlo ahora. Gracias, Sofía. | affirm,question,provide_info · drivers_license=yes |
| **Sofía** | Sí, se puede repartir en moto: puedes usar tu propia moto y te compensamos el combustible por kilómetro. En algunos restaurantes también hay motos de la empresa, y el equipo te lo confirma según tu zona. Tu carnet de moto en vigor consta como carnet válido, y la fecha 3/11 corresponde a «dentro de dos semanas», como me dijiste. | `llm` |
| **Sofía** | Antes de terminar, revisa tus datos:<br>• Nombre: Carmen Vidal<br>• Carnet de conducir: Sí<br>• Zona: Sevilla (Triana)<br>• Disponibilidad: media jornada<br>• Turno: mañana<br>• Experiencia: Sin experiencia previa<br>• Inicio: martes 03/11<br><br>¿Está todo correcto? | `template` |
| *Candidate* | Sí, todo correcto. Gracias, Sofía. Quedo a la espera de que el equipo me confirme lo del aparcamiento para la moto en el restaurante. | affirm,smalltalk,other |
| **Sofía** | Genial, Carmen, gracias por tu tiempo y por tus respuestas. Cumples los requisitos para pasar a la entrevista. Un/a recruiter de Grupo Sazón te escribirá en menos de 48 horas para concertar una breve entrevista en el restaurante más cercano. Lo del aparcamiento para la moto se lo comentamos al equipo para que te lo confirme. | `llm` |

**Screening data:** `{"full_name": "Carmen Vidal", "has_drivers_license": true, "license_status": "yes", "location_raw": "Sevilla, en Triana", "city_id": "sevilla", "city": "Sevilla", "country": "ES", "zone": "Triana", "in_service_area": true, "availability": ["part_time"], "preferred_schedule": ["morning"], "experience_years": 0.0, "experience_months": 0, "start_date": "2026-11-03", "start_date_raw": "dentro de dos semanas"}`

**Recruiter summary:** Perfil apto: carnet de moto en vigor, zona Triana dentro del área de servicio, disponible a media jornada en turno de mañana y con inicio en unas dos semanas (03/11). Sin experiencia previa en reparto. Respuestas claras; precisó por iniciativa propia que solo tiene carnet de moto, no de coche.

**Judge:** warmth 4/5 · clarity 4/5 · brevity 4/5 · language 3/5 · honesty 4/5 · handling 4/5 · summary_faithful 5/5
- Message 5: "licencia de conducir en vigor (auto o moto)" uses Mexican wording with a candidate in Sevilla.
- The recap template was shown three times (messages 15, 18, 21), creating a repetitive loop.
- Message 17 says the moto licence "queda reflejado", but the recap still shows only "Carnet de conducir: Sí".
- Message 20 repeats nearly verbatim the fuel and company-moto text from message 9.
