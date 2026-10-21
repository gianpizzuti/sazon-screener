# p13_wants_a_person

> Laura. Right after giving her name she says she would rather talk to a person than a bot. When the assistant explains, she agrees to continue and answers everything.

**Expected:** qualified · **Got:** needs_review · **Checks:** outcome failed

| | Message | |
|---|---|---|
| **Sofía** | ¡Hola! 👋 Soy Sofía, la asistente virtual (IA) de Grupo Sazón. Te escribo por tu solicitud como repartidor/a: son 7 preguntas rápidas, unos 3 minutos. Tus datos solo se usan para este proceso de selección. ¿Empezamos? | `template` |
| *Candidate* | Hola. Antes de seguir, prefiero hablar con una persona y no con un bot. ¿Me pueden decir cómo va esto? | human_request,question |
| **Sofía** | Claro. Soy una asistente virtual con IA y hago estas preguntas para agilizar el proceso, pero una persona del equipo de selección revisa siempre cada candidatura. Alguien del equipo verá esta conversación y podrá contactarte; si respondes ahora, todo irá más rápido. ¿Cómo te llamas? Nombre y apellido, por favor. | `llm` |
| *Candidate* | Vale, gracias por explicarlo. Me llamo Laura Gómez. | provide_info,smalltalk · full_name=Laura Gómez |
| **Sofía** | Gracias, Laura, encantada. Primera pregunta: ¿tienes carnet de conducir en vigor, ya sea de coche o de moto? | `llm` |
| *Candidate* | Sí, tengo el carnet de moto en vigor. | provide_info,affirm · drivers_license=yes |
| **Sofía** | Perfecto, con el carnet de moto en vigor vamos bien. ¿En qué ciudad y zona te gustaría repartir? | `llm` |
| *Candidate* | Vivo en Málaga, en la zona de Teatinos. | provide_info · location_text=Vivo en Málaga, en la zona de Teatinos, location_city_id=malaga, location_zone=Teatinos, location_outside_service_area=False |
| **Sofía** | Genial, Málaga y la zona de Teatinos. ¿Qué disponibilidad tienes: jornada completa, media jornada o fines de semana? | `llm` |
| *Candidate* | Solo puedo los fines de semana. | provide_info · availability=['weekends'] |
| **Sofía** | Perfecto, fines de semana anotado. ¿Qué turno prefieres: mañana, tarde, noche o flexible? | `llm` |
| *Candidate* | Solo por las tardes no, prefiero turno de noche, es decir, de tardes-noche. Vamos, que solo me va bien el turno de noche. | provide_info · schedule=['evening'] |
| **Sofía** | Entendido, turno de tarde-noche entonces. ¿Tienes experiencia como repartidor/a? Si es así, cuéntame cuánto tiempo y en qué plataformas. | `llm` |
| *Candidate* | Sí, tengo dos años de experiencia con Glovo. | provide_info,affirm · experience_months=24, experience_platforms=['Glovo'] |
| **Sofía** | Dos años con Glovo, genial, es una experiencia que se agradece mucho. ¿Cuándo podrías empezar? | `llm` |
| *Candidate* | Podría empezar el próximo lunes. | provide_info · start_date={'kind': 'next_weekday', 'amount': None, 'weekday': 0, 'exact_date': None} |
| **Sofía** | Antes de terminar, revisa tus datos:<br>• Nombre: Laura Gómez<br>• Carnet de conducir: Sí<br>• Zona: Málaga (Teatinos)<br>• Disponibilidad: fines de semana<br>• Turno: noche<br>• Experiencia: 2 años (Glovo)<br>• Inicio: lunes 26/10<br><br>¿Está todo correcto? | `template` |
| *Candidate* | Casi todo está bien. Solo quiero aclarar dos cosas: tengo carnet de moto (no de coche), y mi turno es de tardes-noche, no solo de noche. Solo puedo por la tarde-noche, no por la tarde sola. | correction,provide_info · drivers_license=yes, schedule=['afternoon', 'evening'] |
| **Sofía** | Antes de terminar, revisa tus datos:<br>• Nombre: Laura Gómez<br>• Carnet de conducir: Sí<br>• Zona: Málaga (Teatinos)<br>• Disponibilidad: fines de semana<br>• Turno: tarde, noche<br>• Experiencia: 2 años (Glovo)<br>• Inicio: lunes 26/10<br><br>¿Está todo correcto? | `template` |
| *Candidate* | Casi. Falta un detalle: tengo carnet de moto, no solo "sí". Y el turno tiene que ser solo de noche (tardes-noche), no de tarde. Lo demás está bien. | correction,provide_info · drivers_license=yes, schedule=['evening'] |
| **Sofía** | Antes de terminar, revisa tus datos:<br>• Nombre: Laura Gómez<br>• Carnet de conducir: Sí<br>• Zona: Málaga (Teatinos)<br>• Disponibilidad: fines de semana<br>• Turno: noche<br>• Experiencia: 2 años (Glovo)<br>• Inicio: lunes 26/10<br><br>¿Está todo correcto? | `template` |
| *Candidate* | Casi, pero siguen faltando dos cosas. El carn | correction,provide_info |
| **Sofía** | Gracias por todo, Laura. Un recruiter del equipo revisará tus respuestas, incluidos los matices que nos has comentado sobre el carnet de moto y el turno de tarde-noche, y se pondrá en contacto contigo pronto. | `llm` |

**Screening data:** `{"full_name": "Laura Gómez", "has_drivers_license": true, "license_status": "yes", "location_raw": "Vivo en Málaga, en la zona de Teatinos", "city_id": "malaga", "city": "Málaga", "country": "ES", "zone": "Teatinos", "in_service_area": true, "availability": ["weekends"], "preferred_schedule": ["evening"], "experience_years": 2.0, "experience_months": 24, "experience_platforms": ["Glovo"], "start_date": "2026-10-26", "start_date_raw": "Podría empezar el próximo lunes."}`
**Flags:** human_requested, recap_not_confirmed

**Recruiter summary:** Perfil con carnet de moto en vigor, dentro de zona de servicio y con 2 años de experiencia en reparto con Glovo. Disponible solo fines de semana en turno de tarde-noche, con inicio inmediato. Pidió hablar con una persona al principio y el resumen final no quedó confirmado porque el sistema no recogió bien el tipo de carnet ni el turno.

**Judge:** warmth 4/5 · clarity 3/5 · brevity 4/5 · language 4/5 · honesty 5/5 · handling 2/5 · summary_faithful 4/5
- The recap in messages 19 and 21 kept "Carnet de conducir: Sí" despite the candidate twice saying it is a moto licence.
- The shift flip-flopped from "Turno: tarde, noche" in message 19 back to "noche" in message 21, without acknowledging the corrections.
- The recap was re-sent identically with no acknowledgement such as "Corregido", creating a frustrating loop.
- The anglicism "Un recruiter del equipo" appears in the closing message.
- The summary's "inicio inmediato" stretches "el próximo lunes".
