# ex25_leaves_and_comes_back

**End:** qualified · interview booked · triage: as expected

- **Sofía:** ¡Hola! 👋 Soy Sofía, la asistente virtual (IA) de Grupo Sazón. Te escribo por tu solicitud como repartidor/a: son 7 preguntas rápidas, unos 3 minutos. Tus datos solo se usan para este proceso de selección. ¿Empezamos?  
  `[¡Empezamos! | Tengo una pregunta]`
- *Candidate:* sí  
  <sub>affirm · events: stage_changed</sub>
- **Sofía:** Genial, vamos allá. ¿Cómo te llamas? Nombre y apellido, por favor.
- *Candidate:* Nuria Cano  
  <sub>provide_info · {"full_name": "Nuria Cano"} · events: field_valid</sub>
- **Sofía:** Encantada, Nuria. Ahora, ¿tienes carnet de conducir en vigor (coche o moto)?  
  `[Sí | No]`
- *Candidate:* sí, de coche  
  <sub>affirm, provide_info · {"drivers_license": "yes", "license_type": "car"} · events: field_valid</sub>
- **Sofía:** Perfecto, con el carnet de coche vamos bien. ¿En qué ciudad y zona te gustaría repartir?
- *Candidate:* me tengo que ir, luego sigo  
  <sub>postpone</sub>
- **Sofía:** No pasa nada, cuando quieras me escribes y seguimos justo donde lo dejamos. ¡Hasta luego! 🙂
- *Candidate:* ya estoy, perdona. Vivo en Valencia, Ruzafa  
  <sub>provide_info · {"location_text": "Valencia, Ruzafa", "location_city_id": "valencia", "location_zone": "Ruzafa", "location_outside_service_area": false} · events: field_valid, field_valid</sub>
- **Sofía:** Genial, Valencia y la zona de Ruzafa, apuntado. ¿Qué disponibilidad tienes: jornada completa, media jornada o fines de semana?  
  `[Jornada completa | Media jornada | Fines de semana]`
- *Candidate:* jornada completa  
  <sub>provide_info · {"availability": ["full_time"]} · events: field_valid</sub>
- **Sofía:** Perfecto, jornada completa. ¿Qué turno prefieres: mañana, tarde, noche o flexible?  
  `[Mañana | Tarde | Noche | Flexible]`
- *Candidate:* flexible  
  <sub>provide_info · {"schedule": ["flexible"]} · events: field_valid</sub>
- **Sofía:** Genial, con turno flexible tienes más opciones. ¿Tienes experiencia como repartidor/a? Si es así, cuéntame cuánto tiempo y en qué plataformas.
- *Candidate:* nunca  
  <sub>provide_info · {"experience_months": 0} · events: field_valid</sub>
- **Sofía:** No pasa nada, todo el mundo empieza por algún sitio. ¿Cuándo podrías empezar?
- *Candidate:* el lunes  
  <sub>provide_info · {"start_date": {"kind": "next_weekday", "amount": null, "weekday": 0, "exact_date": null}} · events: field_valid, stage_changed</sub>
- **Sofía:** Antes de terminar, revisa tus datos:
• Nombre: Nuria Cano
• Carnet de conducir: Sí (coche)
• Zona: Valencia (Ruzafa)
• Disponibilidad: jornada completa
• Turno: flexible
• Experiencia: Sin experiencia previa
• Inicio: lunes 26/10

¿Está todo correcto?  
  `[Sí, todo correcto | Quiero corregir algo]`
- *Candidate:* sí  
  <sub>affirm · events: stage_changed, completed, interview_offered</sub>
- **Sofía:** ¡Perfecto, Nuria! Cumples los requisitos para pasar a la entrevista, y puedes elegir el horario ahora mismo: te envío las opciones justo después de este mensaje. ¡Gracias por tu tiempo! 😊
- **Sofía:** Elige día y hora para tu entrevista (unos 20 minutos) en Grupo Sazón Ruzafa (Valencia):
1) miércoles 21/10 a las 12:30
2) jueves 22/10 a las 10:00
3) viernes 23/10 a las 10:00  
  `[mié 21/10 · 12:30 | jue 22/10 · 10:00 | vie 23/10 · 10:00 | Ninguno me va bien]`
- *Candidate:* 1  
  <sub>affirm, provide_info · option=1 · events: interview_booked</sub>
- **Sofía:** ¡Listo! Tu entrevista es el miércoles 21/10 a las 12:30 en Grupo Sazón Ruzafa (Valencia). Trae tu carnet de conducir. Si no puedes ir, escríbeme y buscamos otro horario.

**Data:** `{"full_name": "Nuria Cano", "has_drivers_license": true, "license_status": "yes", "license_type": "car", "location_raw": "Valencia, Ruzafa", "city_id": "valencia", "city": "Valencia", "country": "ES", "zone": "Ruzafa", "in_service_area": true, "availability": ["full_time"], "preferred_schedule": ["flexible"], "experience_years": 0.0, "experience_months": 0, "start_date": "2026-10-26", "start_date_raw": "el lunes"}`
