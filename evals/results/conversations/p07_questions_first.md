# p07_questions_first

> Carmen, careful and curious. Before her first answer she asks how much the job pays. Later, when asked where she lives, she first asks whether she needs her own motorbike. Before giving her shift she asks whether there is parking for the motorbike at the restaurant. She answers everything else.

**Expected:** qualified · **Got:** needs_review · **Checks:** outcome failed

| | Message | |
|---|---|---|
| **Sofía** | ¡Hola! 👋 Soy Sofía, la asistente virtual (IA) de Grupo Sazón. Te escribo por tu solicitud como repartidor/a: son 7 preguntas rápidas, unos 3 minutos. Tus datos solo se usan para este proceso de selección. ¿Empezamos? | `template` |
| *Candidate* | ¡Hola, Sofía! Sí, empecemos. Antes de nada, ¿cuánto se paga por el puesto? Me gustaría saberlo antes de seguir. | affirm,question |
| **Sofía** | Es un contrato laboral con Grupo Sazón, no como autónomo, con el salario del convenio de hostelería de tu provincia más propinas. El importe exacto según horas te lo confirma el equipo en la entrevista. ¿Cómo te llamas? Nombre y apellido, por favor. | `llm` |
| *Candidate* | Vale, gracias por la aclaración. Me llamo Carmen Vidal. | provide_info,smalltalk · full_name=Carmen Vidal |
| **Sofía** | Encantada, Carmen. Siguiente pregunta: ¿tienes carnet de conducir en vigor, ya sea de coche o de moto? | `llm` |
| *Candidate* | Sí, tengo el carnet de moto en vigor. | provide_info,affirm · drivers_license=yes |
| **Sofía** | Perfecto, gracias. ¿En qué ciudad y zona te gustaría repartir? | `llm` |
| *Candidate* | Estoy en Sevilla, en Triana. Pero antes de decidir, ¿necesito tener moto propia para este puesto? | provide_info,question · location_text=Sevilla, en Triana, location_city_id=sevilla, location_zone=Triana, location_outside_service_area=False |
| **Sofía** | Anotado: Sevilla, zona Triana. No es obligatorio tener moto propia: puedes repartir con la tuya y te compensamos el combustible por kilómetro, y en algunos restaurantes hay motos de la empresa; el equipo te lo confirma según tu zona. ¿Qué disponibilidad tienes: jornada completa, media jornada o fines de semana? | `llm` |
| *Candidate* | Gracias por aclararlo. Yo tengo moto propia, así que me viene bien. Mi disponibilidad es media jornada. | provide_info,other · availability=['part_time'] |
| **Sofía** | Genial, media jornada entonces. ¿Qué turno prefieres: mañana, tarde, noche o flexible? | `llm` |
| *Candidate* | Mañanas, por favor. Pero antes de confirmar el turno, ¿hay sitio para aparcar la moto en el restaurante? | provide_info,question · schedule=['morning'] |
| **Sofía** | Anotado, turno de mañanas. Sobre el aparcamiento en el restaurante no tengo ese dato, así que el equipo de selección te lo confirmará según tu zona. ¿Tienes experiencia como repartidor/a? Si es así, ¿cuánto tiempo y en qué plataformas? | `llm` |
| *Candidate* | No, nunca he trabajado como repartidora. Es mi primera vez. | provide_info,deny · experience_months=0 |
| **Sofía** | No pasa nada, todos empezamos por algo. ¿Cuándo podrías empezar? | `llm` |
| *Candidate* | Podría empezar dentro de dos semanas. | provide_info · start_date={'kind': 'in_weeks', 'amount': 2, 'weekday': None, 'exact_date': None} |
| **Sofía** | Antes de terminar, revisa tus datos:<br>• Nombre: Carmen Vidal<br>• Carnet de conducir: Sí<br>• Zona: Sevilla (Triana)<br>• Disponibilidad: media jornada<br>• Turno: mañana<br>• Experiencia: Sin experiencia previa<br>• Inicio: martes 03/11<br><br>¿Está todo correcto? | `template` |
| *Candidate* | Casi todo está bien, pero hay un dato que no coincide. Yo dije que podría empezar dentro de dos semanas, no el martes 3 de noviembre. Hoy es martes 20 de octubre, así que dentro de dos semanas sería alrededor del martes 3 de noviembre, pero prefiero que conste "dentro de dos semanas" para tener margen. Lo demás es correcto: carnet de moto en vigor, Sevilla (Triana), media jornada, turno de mañanas y sin experiencia previa. | correction,provide_info · drivers_license=yes, location_text=Sevilla (Triana), location_city_id=sevilla, location_zone=Triana, location_outside_service_area=False, availability=['part_time'], schedule=['morning'], experience_months=0, start_date={'kind': 'in_weeks', 'amount': 2, 'weekday': None, 'exact_date': None} |
| **Sofía** | Tal como lo has dicho, "dentro de dos semanas" desde hoy, martes 20/10, es el martes 03/11, y por eso aparece escrito como fecha en el resumen. Te envío ahora el resumen con todos tus datos. | `llm` |
| **Sofía** | Antes de terminar, revisa tus datos:<br>• Nombre: Carmen Vidal<br>• Carnet de conducir: Sí<br>• Zona: Sevilla (Triana)<br>• Disponibilidad: media jornada<br>• Turno: mañana<br>• Experiencia: Sin experiencia previa<br>• Inicio: martes 03/11<br><br>¿Está todo correcto? | `template` |
| *Candidate* | Vale, entiendo que sea una forma de expresarlo. Pero prefiero que en el resumen conste "dentro de dos semanas" y no una fecha concreta, por si necesito algo de margen. Lo demás está bien: Carmen Vidal, carnet de moto en vigor, Sevilla (Triana), media jornada, turno de mañanas y sin experiencia previa. | provide_info,correction · full_name=Carmen Vidal, drivers_license=yes, location_text=Sevilla (Triana), location_city_id=sevilla, location_zone=Triana, location_outside_service_area=False, availability=['part_time'], schedule=['morning'], experience_months=0, start_date={'kind': 'in_weeks', 'amount': 2, 'weekday': None, 'exact_date': None} |
| **Sofía** | Entendido: "dentro de dos semanas" desde hoy, martes 20/10, equivale al martes 03/11, y por eso aparece como fecha en el resumen. El resto coincide con lo que me has contado. Ahora te envío el resumen. | `llm` |
| **Sofía** | Antes de terminar, revisa tus datos:<br>• Nombre: Carmen Vidal<br>• Carnet de conducir: Sí<br>• Zona: Sevilla (Triana)<br>• Disponibilidad: media jornada<br>• Turno: mañana<br>• Experiencia: Sin experiencia previa<br>• Inicio: martes 03/11<br><br>¿Está todo correcto? | `template` |
| *Candidate* | Vale, mientras la fecha aparezca así no puedo darlo por correcto. Yo solo dije "dentro de dos semanas", y prefiero que en el resumen conste exactamente eso. El resto sí es correcto: Carmen Vidal, carnet de moto en vigor, Sevilla (Triana), media jornada, turno de mañanas y sin experiencia previa. ¿Podéis corregirlo así? | correction,question,provide_info · full_name=Carmen Vidal, drivers_license=yes, location_text=Sevilla (Triana), location_city_id=sevilla, location_zone=Triana, location_outside_service_area=False, availability=['part_time'], schedule=['morning'], experience_months=0, start_date={'kind': 'in_weeks', 'amount': 2, 'weekday': None, 'exact_date': None} |
| **Sofía** | Gracias por tu tiempo y por tus respuestas, Carmen. Tomamos nota de lo que nos has indicado sobre tu fecha de inicio. Una persona del equipo de selección revisará tus respuestas y se pondrá en contacto contigo pronto. ¡Que tengas muy buen día! | `llm` |

**Screening data:** `{"full_name": "Carmen Vidal", "has_drivers_license": true, "license_status": "yes", "location_raw": "Sevilla (Triana)", "city_id": "sevilla", "city": "Sevilla", "country": "ES", "zone": "Triana", "in_service_area": true, "availability": ["part_time"], "preferred_schedule": ["morning"], "experience_years": 0.0, "experience_months": 0, "start_date": "2026-11-03", "start_date_raw": "dentro de dos semanas"}`
**Flags:** recap_not_confirmed

**Recruiter summary:** Perfil apto en los criterios básicos: carnet de moto en vigor, moto propia, zona Triana dentro del área de servicio, media jornada en turno de mañana. Sin experiencia previa en reparto. No confirmó el resumen final porque pidió que la fecha de inicio constara como "dentro de dos semanas" y no como 03/11; el agente repitió el mismo resumen tres veces sin corregirlo.

**Judge:** warmth 4/5 · clarity 4/5 · brevity 4/5 · language 5/5 · honesty 4/5 · handling 2/5 · summary_faithful 5/5
- Messages 19 and 22 ignore the requested correction and repeat the justification ("por eso aparece como fecha en el resumen") instead of updating or escalating.
- The recap was resent three times unchanged (messages 17, 20, 23), creating a loop.
- Closing "Tomamos nota de lo que nos has indicado sobre tu fecha de inicio" does not confirm whether the date will be recorded as she asked.
- Message 9 asserts fuel compensation per km and company motos, terms that may not be confirmed policy.
- Recap shows "Carnet de conducir: Sí" without noting it is a moto licence (fixed template).
