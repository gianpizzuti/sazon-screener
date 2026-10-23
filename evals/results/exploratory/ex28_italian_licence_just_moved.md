# ex28_italian_licence_just_moved

**End:** qualified · interview booked · triage: as expected

- **Sofía:** ¡Hola! 👋 Soy Sofía, la asistente virtual (IA) de Grupo Sazón. Te escribo por tu solicitud como repartidor/a: son 7 preguntas rápidas, unos 3 minutos. Tus datos solo se usan para este proceso de selección. ¿Empezamos?  
  `[¡Empezamos! | Tengo una pregunta]`
- *Candidate:* sí  
  <sub>affirm · events: stage_changed</sub>
- **Sofía:** ¡Genial, vamos allá! ¿Cómo te llamas? Nombre y apellido, por favor.
- *Candidate:* Giulia Rossi  
  <sub>provide_info · {"full_name": "Giulia Rossi"} · events: field_valid</sub>
- **Sofía:** Encantada, Giulia. ¿Tienes carnet de conducir en vigor (coche o moto)?  
  `[Sí | No]`
- *Candidate:* sí, el carnet italiano de coche, me acabo de mudar a España. ¿Me sirve?  
  <sub>provide_info, affirm, question · {"drivers_license": "yes", "license_type": "car", "license_country": "Italia"} · faq=foreign_licence · events: question_answered, field_valid</sub>
- **Sofía:** Perfecto, con carnet de coche en vigor vamos bien. Y sí, te sirve: un carnet de Italia vale para conducir en España mientras esté en vigor, igual que el español. ¿En qué ciudad y zona te gustaría repartir?
- *Candidate:* Barcelona, Gràcia  
  <sub>provide_info · {"location_text": "Barcelona, Gràcia", "location_city_id": "barcelona", "location_zone": "Gràcia", "location_outside_service_area": false} · events: field_valid, field_valid</sub>
- **Sofía:** Genial, Barcelona y la zona de Gràcia. ¿Qué disponibilidad tienes: jornada completa, media jornada o fines de semana?  
  `[Jornada completa | Media jornada | Fines de semana]`
- *Candidate:* media jornada  
  <sub>provide_info · {"availability": ["part_time"]} · events: field_valid</sub>
- **Sofía:** Perfecto, media jornada. ¿Qué turno prefieres: mañana, tarde, noche o flexible?  
  `[Mañana | Tarde | Noche | Flexible]`
- *Candidate:* tardes  
  <sub>provide_info · {"schedule": ["afternoon"]} · events: field_valid</sub>
- **Sofía:** Anotado, turno de tardes. ¿Tienes experiencia repartiendo? Si es así, cuéntame cuánto tiempo y en qué plataformas.
- *Candidate:* un año en Deliveroo en Milán  
  <sub>provide_info · {"experience_months": 12, "experience_platforms": ["Deliveroo"]} · events: field_valid, field_valid</sub>
- **Sofía:** Genial, un año repartiendo con Deliveroo es una buena experiencia. ¿Cuándo podrías empezar?
- *Candidate:* el lunes  
  <sub>provide_info · {"start_date": {"kind": "next_weekday", "amount": null, "weekday": 0, "exact_date": null}} · events: field_valid, stage_changed</sub>
- **Sofía:** Antes de terminar, revisa tus datos:
• Nombre: Giulia Rossi
• Carnet de conducir: Sí (coche, Italia)
• Zona: Barcelona (Gràcia)
• Disponibilidad: media jornada
• Turno: tarde
• Experiencia: 1 año (Deliveroo)
• Inicio: lunes 26/10

¿Está todo correcto?  
  `[Sí, todo correcto | Quiero corregir algo]`
- *Candidate:* sí  
  <sub>affirm · events: stage_changed, completed, interview_offered</sub>
- **Sofía:** ¡Genial, Giulia! Cumples los requisitos para pasar a la entrevista. Ahora mismo puedes elegir el horario que mejor te venga: te mando las opciones justo después de este mensaje. ¡Gracias por tu tiempo!
- **Sofía:** Elige día y hora para tu entrevista (unos 20 minutos) en Grupo Sazón Gràcia (Barcelona):
1) miércoles 21/10 a las 16:00
2) jueves 22/10 a las 16:00
3) viernes 23/10 a las 16:00  
  `[mié 21/10 · 16:00 | jue 22/10 · 16:00 | vie 23/10 · 16:00 | Ninguno me va bien]`
- *Candidate:* 1  
  <sub>provide_info · option=1 · events: interview_booked</sub>
- **Sofía:** ¡Listo! Tu entrevista es el miércoles 21/10 a las 16:00 en Grupo Sazón Gràcia (Barcelona). Trae tu carnet de conducir. Si no puedes ir, escríbeme y buscamos otro horario.

**Data:** `{"full_name": "Giulia Rossi", "has_drivers_license": true, "license_status": "yes", "license_type": "car", "license_country": "IT", "location_raw": "Barcelona, Gràcia", "city_id": "barcelona", "city": "Barcelona", "country": "ES", "zone": "Gràcia", "in_service_area": true, "availability": ["part_time"], "preferred_schedule": ["afternoon"], "experience_years": 1.0, "experience_months": 12, "experience_platforms": ["Deliveroo"], "start_date": "2026-10-26", "start_date_raw": "el lunes"}`
