# ex17_insult_then_apology

**End:** qualified · interview booked · triage: as expected

- **Sofía:** ¡Hola! 👋 Soy Sofía, la asistente virtual (IA) de Grupo Sazón. Te escribo por tu solicitud como repartidor/a: son 7 preguntas rápidas, unos 3 minutos. Tus datos solo se usan para este proceso de selección. ¿Empezamos?  
  `[¡Empezamos! | Tengo una pregunta]`
- *Candidate:* sí  
  <sub>affirm · events: stage_changed</sub>
- **Sofía:** ¡Genial, vamos allá! ¿Cómo te llamas? Nombre y apellido, por favor.
- *Candidate:* Dani Fuentes  
  <sub>provide_info · {"full_name": "Dani Fuentes"} · events: field_valid</sub>
- **Sofía:** Encantada, Dani Fuentes. ¿Tienes carnet de conducir en vigor (coche o moto)?  
  `[Sí | No]`
- *Candidate:* esto es una mierda de proceso, joder  
  <sub>abuse · events: abuse_strike, sentiment</sub>
- **Sofía:** Entiendo que se te haga pesado, y te pido que mantengamos un trato respetuoso. Quedan solo 6 preguntas. ¿Tienes carnet de conducir en vigor (coche o moto)?  
  `[Sí | No]`
- *Candidate:* perdona, mal día. Sí, tengo carnet de coche  
  <sub>provide_info, affirm, other · {"drivers_license": "yes", "license_type": "car"} · events: field_valid</sub>
- **Sofía:** No pasa nada, a todos nos pasa. Perfecto, carnet de coche en vigor. ¿En qué ciudad y zona te gustaría repartir?
- *Candidate:* Barcelona, Sants  
  <sub>provide_info · {"location_text": "Barcelona, Sants", "location_city_id": "barcelona", "location_zone": "Sants-Montjuïc", "location_outside_service_area": false} · events: field_valid, field_valid</sub>
- **Sofía:** Perfecto, Barcelona, zona Sants-Montjuïc. ¿Qué disponibilidad tienes: jornada completa, media jornada o fines de semana?  
  `[Jornada completa | Media jornada | Fines de semana]`
- *Candidate:* media jornada  
  <sub>provide_info · {"availability": ["part_time"]} · events: field_valid</sub>
- **Sofía:** Media jornada, anotado. ¿Qué turno prefieres: mañana, tarde, noche o flexible?  
  `[Mañana | Tarde | Noche | Flexible]`
- *Candidate:* tarde  
  <sub>provide_info · {"schedule": ["afternoon"]} · events: field_valid</sub>
- **Sofía:** Turno de tarde, apuntado. ¿Tienes experiencia repartiendo? Si es así, ¿cuánto tiempo y en qué plataformas?
- *Candidate:* nunca  
  <sub>provide_info · {"experience_months": 0} · events: field_valid</sub>
- **Sofía:** Sin problema, no hace falta experiencia previa para este puesto. ¿Cuándo podrías empezar?
- *Candidate:* ya  
  <sub>provide_info · {"start_date": {"kind": "immediate", "amount": null, "weekday": null, "exact_date": null}} · events: field_valid, stage_changed</sub>
- **Sofía:** Antes de terminar, revisa tus datos:
• Nombre: Dani Fuentes
• Carnet de conducir: Sí (coche)
• Zona: Barcelona (Sants-Montjuïc)
• Disponibilidad: media jornada
• Turno: tarde
• Experiencia: Sin experiencia previa
• Inicio: lo antes posible (martes 20/10)

¿Está todo correcto?  
  `[Sí, todo correcto | Quiero corregir algo]`
- *Candidate:* sí  
  <sub>affirm · events: stage_changed, completed, interview_offered</sub>
- **Sofía:** ¡Gracias, Dani! Cumples los requisitos para pasar a la entrevista, así que ya puedes elegir el horario que mejor te venga: te envío las opciones justo después de este mensaje.
- **Sofía:** Elige día y hora para tu entrevista (unos 20 minutos) en Grupo Sazón Gràcia (Barcelona):
1) miércoles 21/10 a las 16:00
2) jueves 22/10 a las 16:00
3) viernes 23/10 a las 16:00  
  `[mié 21/10 · 16:00 | jue 22/10 · 16:00 | vie 23/10 · 16:00 | Ninguno me va bien]`
- *Candidate:* 1  
  <sub>provide_info · option=1 · events: interview_booked</sub>
- **Sofía:** ¡Listo! Tu entrevista es el miércoles 21/10 a las 16:00 en Grupo Sazón Gràcia (Barcelona). Trae tu carnet de conducir. Si no puedes ir, escríbeme y buscamos otro horario.

**Data:** `{"full_name": "Dani Fuentes", "has_drivers_license": true, "license_status": "yes", "license_type": "car", "location_raw": "Barcelona, Sants", "city_id": "barcelona", "city": "Barcelona", "country": "ES", "zone": "Sants-Montjuïc", "in_service_area": true, "availability": ["part_time"], "preferred_schedule": ["afternoon"], "experience_years": 0.0, "experience_months": 0, "start_date": "2026-10-20", "start_date_raw": "ya"}`
**Flags:** abuse
