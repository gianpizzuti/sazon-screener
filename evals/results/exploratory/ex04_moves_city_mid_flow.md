# ex04_moves_city_mid_flow

**End:** qualified · interview booked · triage: as expected

- **Sofía:** ¡Hola! 👋 Soy Sofía, la asistente virtual (IA) de Grupo Sazón. Te escribo por tu solicitud como repartidor/a: son 7 preguntas rápidas, unos 3 minutos. Tus datos solo se usan para este proceso de selección. ¿Empezamos?  
  `[¡Empezamos! | Tengo una pregunta]`
- *Candidate:* sí  
  <sub>affirm · events: stage_changed</sub>
- **Sofía:** Genial, empezamos. ¿Cómo te llamas? Nombre y apellido, por favor.
- *Candidate:* Mario Gil  
  <sub>provide_info · {"full_name": "Mario Gil"} · events: field_valid</sub>
- **Sofía:** Encantada, Mario. ¿Tienes carnet de conducir en vigor, ya sea de coche o de moto?  
  `[Sí | No]`
- *Candidate:* sí, de coche  
  <sub>affirm, provide_info · {"drivers_license": "yes", "license_type": "car"} · events: field_valid</sub>
- **Sofía:** Perfecto, carnet de coche en vigor. ¿En qué ciudad y zona te gustaría repartir?
- *Candidate:* Madrid, centro  
  <sub>provide_info · {"location_text": "Madrid, centro", "location_city_id": "madrid", "location_zone": "Centro", "location_outside_service_area": false} · events: field_valid, field_valid</sub>
- **Sofía:** Genial, Madrid centro. ¿Qué disponibilidad tienes: jornada completa, media jornada o fines de semana?  
  `[Jornada completa | Media jornada | Fines de semana]`
- *Candidate:* media jornada  
  <sub>provide_info · {"availability": ["part_time"]} · events: field_valid</sub>
- **Sofía:** Perfecto, media jornada. ¿Qué turno prefieres: mañana, tarde, noche o flexible?  
  `[Mañana | Tarde | Noche | Flexible]`
- *Candidate:* perdona, al final me mudo a Valencia el mes que viene, mejor allí  
  <sub>correction, provide_info · {"location_text": "Valencia", "location_city_id": "valencia", "location_outside_service_area": false} · events: field_valid, field_corrected</sub>
- **Sofía:** Sin problema, entonces Valencia. ¿Y en qué zona o barrio? Así vemos el restaurante más cercano. Puedes tocar una de las opciones o escribir tu barrio.  
  `[Ciutat Vella | Ruzafa | Benimaclet | Campanar | El Cabanyal | Cualquier zona]`
- *Candidate:* Benimaclet  
  <sub>provide_info · {"location_text": "Benimaclet", "location_city_id": "valencia", "location_zone": "Benimaclet", "location_outside_service_area": false} · events: field_valid</sub>
- **Sofía:** Perfecto, Benimaclet. ¿Qué turno prefieres: mañana, tarde, noche o flexible?  
  `[Mañana | Tarde | Noche | Flexible]`
- *Candidate:* tardes  
  <sub>provide_info · {"schedule": ["afternoon"]} · events: field_valid</sub>
- **Sofía:** Genial, turno de tardes. ¿Tienes experiencia repartiendo? Si es así, cuéntame cuánto tiempo y en qué plataformas.
- *Candidate:* nunca  
  <sub>provide_info · {"experience_months": 0} · events: field_valid</sub>
- **Sofía:** No pasa nada, todos empezamos de cero. ¿Cuándo podrías empezar?
- *Candidate:* dentro de un mes  
  <sub>provide_info · {"start_date": {"kind": "in_months", "amount": 1, "weekday": null, "exact_date": null}} · events: field_valid, stage_changed</sub>
- **Sofía:** Antes de terminar, revisa tus datos:
• Nombre: Mario Gil
• Carnet de conducir: Sí (coche)
• Zona: Valencia (Benimaclet)
• Disponibilidad: media jornada
• Turno: tarde
• Experiencia: Sin experiencia previa
• Inicio: viernes 20/11

¿Está todo correcto?  
  `[Sí, todo correcto | Quiero corregir algo]`
- *Candidate:* sí  
  <sub>affirm · events: stage_changed, completed, interview_offered</sub>
- **Sofía:** ¡Perfecto, Mario! Cumples los requisitos para pasar a la entrevista. Ahora mismo puedes elegir el horario que mejor te venga: te envío las opciones justo después de este mensaje. ¡Gracias por tu tiempo!
- **Sofía:** Elige día y hora para tu entrevista (unos 20 minutos) en Grupo Sazón Ruzafa (Valencia):
1) miércoles 21/10 a las 16:00
2) jueves 22/10 a las 16:00
3) viernes 23/10 a las 16:00  
  `[mié 21/10 · 16:00 | jue 22/10 · 16:00 | vie 23/10 · 16:00 | Ninguno me va bien]`
- *Candidate:* 1  
  <sub>provide_info · option=1 · events: interview_booked</sub>
- **Sofía:** ¡Listo! Tu entrevista es el miércoles 21/10 a las 16:00 en Grupo Sazón Ruzafa (Valencia). Trae tu carnet de conducir. Si no puedes ir, escríbeme y buscamos otro horario.

**Data:** `{"full_name": "Mario Gil", "has_drivers_license": true, "license_status": "yes", "license_type": "car", "location_raw": "Valencia", "city_id": "valencia", "city": "Valencia", "country": "ES", "zone": "Benimaclet", "in_service_area": true, "availability": ["part_time"], "preferred_schedule": ["afternoon"], "experience_years": 0.0, "experience_months": 0, "start_date": "2026-11-20", "start_date_raw": "dentro de un mes"}`
