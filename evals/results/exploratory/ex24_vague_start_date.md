# ex24_vague_start_date

**End:** qualified · interview booked · triage: as expected

- **Sofía:** ¡Hola! 👋 Soy Sofía, la asistente virtual (IA) de Grupo Sazón. Te escribo por tu solicitud como repartidor/a: son 7 preguntas rápidas, unos 3 minutos. Tus datos solo se usan para este proceso de selección. ¿Empezamos?  
  `[¡Empezamos! | Tengo una pregunta]`
- *Candidate:* sí  
  <sub>affirm · events: stage_changed</sub>
- **Sofía:** ¡Genial, vamos allá! Para empezar, ¿cómo te llamas? Nombre y apellido, por favor.
- *Candidate:* Álvaro Méndez  
  <sub>provide_info · {"full_name": "Álvaro Méndez"} · events: field_valid</sub>
- **Sofía:** Encantada, Álvaro. ¿Tienes carnet de conducir en vigor, ya sea de coche o de moto?  
  `[Sí | No]`
- *Candidate:* sí, de coche  
  <sub>affirm, provide_info · {"drivers_license": "yes", "license_type": "car"} · events: field_valid</sub>
- **Sofía:** Perfecto, el carnet de coche en vigor cuenta. ¿En qué ciudad y zona te gustaría repartir?
- *Candidate:* Barcelona, Poblenou  
  <sub>provide_info · {"location_text": "Barcelona, Poblenou", "location_city_id": "barcelona", "location_outside_service_area": false} · events: field_valid, field_valid</sub>
- **Sofía:** Perfecto, Barcelona, zona de Sant Martí. ¿Qué disponibilidad tienes: jornada completa, media jornada o fines de semana?  
  `[Jornada completa | Media jornada | Fines de semana]`
- *Candidate:* media jornada  
  <sub>provide_info · {"availability": ["part_time"]} · events: field_valid</sub>
- **Sofía:** Genial, media jornada entonces. ¿Qué turno prefieres: mañana, tarde, noche o flexible?  
  `[Mañana | Tarde | Noche | Flexible]`
- *Candidate:* mañanas  
  <sub>provide_info · {"schedule": ["morning"]} · events: field_valid</sub>
- **Sofía:** Perfecto, turno de mañanas. ¿Tienes experiencia repartiendo? Si es así, cuéntame cuánto tiempo y en qué plataformas.
- *Candidate:* un año en Just Eat  
  <sub>provide_info · {"experience_months": 12, "experience_platforms": ["Just Eat"]} · events: field_valid, field_valid</sub>
- **Sofía:** Estupendo, un año repartiendo con Just Eat es una buena experiencia. ¿Cuándo podrías empezar?
- *Candidate:* cuando pueda, depende  
  <sub>provide_info · {"start_date": {"kind": "unclear", "amount": null, "weekday": null, "exact_date": null}} · events: field_invalid</sub>
- **Sofía:** Entendido, no pasa nada si aún no lo tienes claro. ¿Podrías darme una fecha aproximada, por ejemplo "el lunes que viene" o "dentro de dos semanas"?
- *Candidate:* pues en tres semanas  
  <sub>provide_info · {"start_date": {"kind": "in_weeks", "amount": 3, "weekday": null, "exact_date": null}} · events: field_valid, stage_changed</sub>
- **Sofía:** Antes de terminar, revisa tus datos:
• Nombre: Álvaro Méndez
• Carnet de conducir: Sí (coche)
• Zona: Barcelona (Sant Martí)
• Disponibilidad: media jornada
• Turno: mañana
• Experiencia: 1 año (Just Eat)
• Inicio: martes 10/11

¿Está todo correcto?  
  `[Sí, todo correcto | Quiero corregir algo]`
- *Candidate:* sí  
  <sub>affirm · events: stage_changed, completed, interview_offered</sub>
- **Sofía:** ¡Genial, Álvaro, muchas gracias! Cumples con los requisitos para pasar a la entrevista. Ahora mismo puedes elegir el horario que mejor te venga: te envío las opciones justo después de este mensaje.
- **Sofía:** Elige día y hora para tu entrevista (unos 20 minutos) en Grupo Sazón Gràcia (Barcelona):
1) miércoles 21/10 a las 12:30
2) jueves 22/10 a las 10:00
3) viernes 23/10 a las 10:00  
  `[mié 21/10 · 12:30 | jue 22/10 · 10:00 | vie 23/10 · 10:00 | Ninguno me va bien]`
- *Candidate:* 1  
  <sub>provide_info · option=1 · events: interview_booked</sub>
- **Sofía:** ¡Listo! Tu entrevista es el miércoles 21/10 a las 12:30 en Grupo Sazón Gràcia (Barcelona). Trae tu carnet de conducir. Si no puedes ir, escríbeme y buscamos otro horario.

**Data:** `{"full_name": "Álvaro Méndez", "has_drivers_license": true, "license_status": "yes", "license_type": "car", "location_raw": "Barcelona, Poblenou", "city_id": "barcelona", "city": "Barcelona", "country": "ES", "zone": "Sant Martí", "in_service_area": true, "availability": ["part_time"], "preferred_schedule": ["morning"], "experience_years": 1.0, "experience_months": 12, "experience_platforms": ["Just Eat"], "start_date": "2026-11-10", "start_date_raw": "en tres semanas"}`
