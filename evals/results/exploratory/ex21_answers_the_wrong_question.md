# ex21_answers_the_wrong_question

**End:** qualified · interview booked · triage: as expected

- **Sofía:** ¡Hola! 👋 Soy Sofía, la asistente virtual (IA) de Grupo Sazón. Te escribo por tu solicitud como repartidor/a: son 7 preguntas rápidas, unos 3 minutos. Tus datos solo se usan para este proceso de selección. ¿Empezamos?  
  `[¡Empezamos! | Tengo una pregunta]`
- *Candidate:* sí  
  <sub>affirm · events: stage_changed</sub>
- **Sofía:** ¡Genial, gracias! Para empezar, ¿cómo te llamas? Nombre y apellido, por favor.
- *Candidate:* Luis Campos  
  <sub>provide_info · {"full_name": "Luis Campos"} · events: field_valid</sub>
- **Sofía:** Encantada, Luis. ¿Tienes carnet de conducir en vigor, ya sea de coche o de moto?  
  `[Sí | No]`
- *Candidate:* vivo en Sevilla, en Macarena  
  <sub>provide_info · {"location_text": "vivo en Sevilla, en Macarena", "location_city_id": "sevilla", "location_zone": "Macarena", "location_outside_service_area": false} · events: field_valid, field_valid</sub>
- **Sofía:** Perfecto, Sevilla y la zona de la Macarena, anotado. Y ahora sí, ¿tienes carnet de conducir en vigor, ya sea de coche o de moto?  
  `[Sí | No]`
- *Candidate:* sí tengo, de coche  
  <sub>provide_info, affirm · {"drivers_license": "yes", "license_type": "car"} · events: field_valid</sub>
- **Sofía:** Genial, carnet de coche en vigor, apuntado. ¿Qué disponibilidad tienes: jornada completa, media jornada o fines de semana?  
  `[Jornada completa | Media jornada | Fines de semana]`
- *Candidate:* he repartido un año con Glovo  
  <sub>provide_info · {"experience_months": 12, "experience_platforms": ["Glovo"]} · events: field_valid, field_valid</sub>
- **Sofía:** Un año con Glovo, buena experiencia, gracias por contármelo. Y para seguir, ¿qué disponibilidad tienes: jornada completa, media jornada o fines de semana?  
  `[Jornada completa | Media jornada | Fines de semana]`
- *Candidate:* jornada completa  
  <sub>provide_info · {"availability": ["full_time"]} · events: field_valid</sub>
- **Sofía:** Perfecto, jornada completa. ¿Qué turno prefieres: mañana, tarde, noche o flexible?  
  `[Mañana | Tarde | Noche | Flexible]`
- *Candidate:* noche  
  <sub>provide_info · {"schedule": ["evening"]} · events: field_valid</sub>
- **Sofía:** Perfecto, turno de noche, anotado. ¿Cuándo podrías empezar?
- *Candidate:* el lunes  
  <sub>provide_info · {"start_date": {"kind": "next_weekday", "amount": null, "weekday": 0, "exact_date": null}} · events: field_valid, stage_changed</sub>
- **Sofía:** Antes de terminar, revisa tus datos:
• Nombre: Luis Campos
• Carnet de conducir: Sí (coche)
• Zona: Sevilla (Macarena)
• Disponibilidad: jornada completa
• Turno: noche
• Experiencia: 1 año (Glovo)
• Inicio: lunes 26/10

¿Está todo correcto?  
  `[Sí, todo correcto | Quiero corregir algo]`
- *Candidate:* sí  
  <sub>affirm · events: stage_changed, completed, interview_offered</sub>
- **Sofía:** ¡Genial, Luis! Con lo que me has contado, cumples los requisitos para pasar a la entrevista. Ahora mismo puedes elegir el horario que mejor te venga: te envío las opciones justo después de este mensaje. 😊
- **Sofía:** Elige día y hora para tu entrevista (unos 20 minutos) en Grupo Sazón Triana (Sevilla):
1) miércoles 21/10 a las 17:00
2) jueves 22/10 a las 17:00
3) viernes 23/10 a las 17:00  
  `[mié 21/10 · 17:00 | jue 22/10 · 17:00 | vie 23/10 · 17:00 | Ninguno me va bien]`
- *Candidate:* 1  
  <sub>provide_info · option=1 · events: interview_booked</sub>
- **Sofía:** ¡Listo! Tu entrevista es el miércoles 21/10 a las 17:00 en Grupo Sazón Triana (Sevilla). Trae tu carnet de conducir. Si no puedes ir, escríbeme y buscamos otro horario.

**Data:** `{"full_name": "Luis Campos", "has_drivers_license": true, "license_status": "yes", "license_type": "car", "location_raw": "vivo en Sevilla, en Macarena", "city_id": "sevilla", "city": "Sevilla", "country": "ES", "zone": "Macarena", "in_service_area": true, "availability": ["full_time"], "preferred_schedule": ["evening"], "experience_years": 1.0, "experience_months": 12, "experience_platforms": ["Glovo"], "start_date": "2026-10-26", "start_date_raw": "el lunes"}`
