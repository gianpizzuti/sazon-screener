# ex01_small_talk_and_weather

**End:** qualified · interview booked · triage: as expected

- **Sofía:** ¡Hola! 👋 Soy Sofía, la asistente virtual (IA) de Grupo Sazón. Te escribo por tu solicitud como repartidor/a: son 7 preguntas rápidas, unos 3 minutos. Tus datos solo se usan para este proceso de selección. ¿Empezamos?  
  `[¡Empezamos! | Tengo una pregunta]`
- *Candidate:* holaa! sí, vamos  
  <sub>smalltalk, affirm · events: stage_changed</sub>
- **Sofía:** ¡Genial, empezamos! ¿Cómo te llamas? Nombre y apellido, por favor.
- *Candidate:* Me llamo Andrea Sanz. Por cierto, ¿qué tiempo hace hoy en Madrid?  
  <sub>provide_info, question · {"full_name": "Andrea Sanz"} · events: question_unanswered, field_valid</sub>
- **Sofía:** Encantada, Andrea. Del tiempo en Madrid no tengo información, así que no me atrevo a decirte nada. Sigamos con lo tuyo: ¿tienes carnet de conducir en vigor, de coche o de moto?  
  `[Sí | No]`
- *Candidate:* jaja vale. sí, tengo carnet de coche  
  <sub>provide_info, affirm · {"drivers_license": "yes", "license_type": "car"} · events: field_valid</sub>
- **Sofía:** Perfecto, con el carnet de coche ya tenemos un punto clave. ¿En qué ciudad y zona te gustaría repartir?
- *Candidate:* Madrid, Chamberí  
  <sub>provide_info · {"location_text": "Madrid, Chamberí", "location_city_id": "madrid", "location_zone": "Chamberí", "location_outside_service_area": false} · events: field_valid, field_valid</sub>
- **Sofía:** Madrid, Chamberí, anotado. ¿Qué disponibilidad tienes: jornada completa, media jornada o fines de semana?  
  `[Jornada completa | Media jornada | Fines de semana]`
- *Candidate:* me encanta tu nombre, Sofía 😄  
  <sub>smalltalk</sub>
- **Sofía:** Mil gracias, qué majo/a... bueno, qué amable 😄 Sigamos: ¿qué disponibilidad tienes, jornada completa, media jornada o fines de semana?  
  `[Jornada completa | Media jornada | Fines de semana]`
- *Candidate:* media jornada  
  <sub>provide_info · {"availability": ["part_time"]} · events: field_valid</sub>
- **Sofía:** Perfecto, media jornada. ¿Qué turno prefieres: mañana, tarde, noche o flexible?  
  `[Mañana | Tarde | Noche | Flexible]`
- *Candidate:* por las mañanas  
  <sub>provide_info · {"schedule": ["morning"]} · events: field_valid</sub>
- **Sofía:** Genial, turno de mañana. ¿Tienes experiencia repartiendo? Si es así, cuéntame cuánto tiempo y en qué plataformas.
- *Candidate:* no, nunca he repartido  
  <sub>provide_info, deny · {"experience_months": 0} · events: field_valid</sub>
- **Sofía:** No pasa nada, mucha gente empieza sin experiencia repartiendo. ¿Cuándo podrías empezar?
- *Candidate:* el lunes que viene  
  <sub>provide_info · {"start_date": {"kind": "next_weekday", "amount": null, "weekday": 0, "exact_date": null}} · events: field_valid, stage_changed</sub>
- **Sofía:** Antes de terminar, revisa tus datos:
• Nombre: Andrea Sanz
• Carnet de conducir: Sí (coche)
• Zona: Madrid (Chamberí)
• Disponibilidad: media jornada
• Turno: mañana
• Experiencia: Sin experiencia previa
• Inicio: lunes 26/10

¿Está todo correcto?  
  `[Sí, todo correcto | Quiero corregir algo]`
- *Candidate:* sí, todo bien  
  <sub>affirm · events: stage_changed, completed, interview_offered</sub>
- **Sofía:** ¡Genial, Andrea! Cumples los requisitos para pasar a la entrevista, y ya puedes elegir el horario que mejor te encaje: te envío las opciones justo después de este mensaje. ¡Gracias por tu tiempo!
- **Sofía:** Elige día y hora para tu entrevista (unos 20 minutos) en Grupo Sazón Malasaña (Madrid):
1) miércoles 21/10 a las 12:30
2) jueves 22/10 a las 10:00
3) viernes 23/10 a las 10:00  
  `[mié 21/10 · 12:30 | jue 22/10 · 10:00 | vie 23/10 · 10:00 | Ninguno me va bien]`
- *Candidate:* 1  
  <sub>provide_info · option=1 · events: interview_booked</sub>
- **Sofía:** ¡Listo! Tu entrevista es el miércoles 21/10 a las 12:30 en Grupo Sazón Malasaña (Madrid). Trae tu carnet de conducir. Si no puedes ir, escríbeme y buscamos otro horario.

**Data:** `{"full_name": "Andrea Sanz", "has_drivers_license": true, "license_status": "yes", "license_type": "car", "location_raw": "Madrid, Chamberí", "city_id": "madrid", "city": "Madrid", "country": "ES", "zone": "Chamberí", "in_service_area": true, "availability": ["part_time"], "preferred_schedule": ["morning"], "experience_years": 0.0, "experience_months": 0, "start_date": "2026-10-26", "start_date_raw": "el lunes que viene"}`
