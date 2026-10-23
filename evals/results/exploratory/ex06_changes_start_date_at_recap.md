# ex06_changes_start_date_at_recap

**End:** qualified · interview booked · triage: as expected

- **Sofía:** ¡Hola! 👋 Soy Sofía, la asistente virtual (IA) de Grupo Sazón. Te escribo por tu solicitud como repartidor/a: son 7 preguntas rápidas, unos 3 minutos. Tus datos solo se usan para este proceso de selección. ¿Empezamos?  
  `[¡Empezamos! | Tengo una pregunta]`
- *Candidate:* sí  
  <sub>affirm · events: stage_changed</sub>
- **Sofía:** ¡Genial, vamos allá! ¿Cómo te llamas? Nombre y apellido, por favor.
- *Candidate:* Paula Ortiz  
  <sub>provide_info · {"full_name": "Paula Ortiz"} · events: field_valid</sub>
- **Sofía:** Encantada, Paula. ¿Tienes carnet de conducir en vigor, ya sea de coche o de moto?  
  `[Sí | No]`
- *Candidate:* sí, de coche  
  <sub>provide_info, affirm · {"drivers_license": "yes", "license_type": "car"} · events: field_valid</sub>
- **Sofía:** Perfecto, carnet de coche en vigor, anotado. ¿En qué ciudad y zona te gustaría repartir?
- *Candidate:* Málaga, Teatinos  
  <sub>provide_info · {"location_text": "Málaga, Teatinos", "location_city_id": "malaga", "location_zone": "Teatinos", "location_outside_service_area": false} · events: field_valid, field_valid</sub>
- **Sofía:** Málaga, zona Teatinos, apuntado. ¿Qué disponibilidad tienes: jornada completa, media jornada o fines de semana?  
  `[Jornada completa | Media jornada | Fines de semana]`
- *Candidate:* fines de semana  
  <sub>provide_info · {"availability": ["weekends"]} · events: field_valid</sub>
- **Sofía:** Genial, fines de semana. ¿Qué turno prefieres: mañana, tarde, noche o flexible?  
  `[Mañana | Tarde | Noche | Flexible]`
- *Candidate:* tardes  
  <sub>provide_info · {"schedule": ["afternoon"]} · events: field_valid</sub>
- **Sofía:** Perfecto, turno de tardes. ¿Tienes experiencia repartiendo? Si es así, cuéntame cuánto tiempo y en qué plataformas.
- *Candidate:* sin experiencia  
  <sub>provide_info · {"experience_months": 0} · events: field_valid</sub>
- **Sofía:** No pasa nada, aquí también damos la bienvenida a quien empieza desde cero. ¿Cuándo podrías empezar?
- *Candidate:* el lunes  
  <sub>provide_info · {"start_date": {"kind": "next_weekday", "amount": null, "weekday": 0, "exact_date": null}} · events: field_valid, stage_changed</sub>
- **Sofía:** Antes de terminar, revisa tus datos:
• Nombre: Paula Ortiz
• Carnet de conducir: Sí (coche)
• Zona: Málaga (Teatinos)
• Disponibilidad: fines de semana
• Turno: tarde
• Experiencia: Sin experiencia previa
• Inicio: lunes 26/10

¿Está todo correcto?  
  `[Sí, todo correcto | Quiero corregir algo]`
- *Candidate:* uy, la fecha mejor el 2 de noviembre  
  <sub>correction, provide_info · {"start_date": {"kind": "exact_date", "amount": null, "weekday": null, "exact_date": "2026-11-02"}} · events: field_valid, field_corrected</sub>
- **Sofía:** Listo, he actualizado tus datos. Revísalos:
• Nombre: Paula Ortiz
• Carnet de conducir: Sí (coche)
• Zona: Málaga (Teatinos)
• Disponibilidad: fines de semana
• Turno: tarde
• Experiencia: Sin experiencia previa
• Inicio: lunes 02/11

¿Está todo correcto?  
  `[Sí, todo correcto | Quiero corregir algo]`
- *Candidate:* sí, ahora sí  
  <sub>affirm · events: stage_changed, completed, interview_offered</sub>
- **Sofía:** Gracias, Paula, ya tenemos todo. Cumples los requisitos para pasar a la entrevista, y puedes elegir el horario ahora mismo: te envío las opciones justo después de este mensaje. 😊
- **Sofía:** Elige día y hora para tu entrevista (unos 20 minutos) en Grupo Sazón Centro (Málaga):
1) miércoles 21/10 a las 16:00
2) jueves 22/10 a las 16:00
3) viernes 23/10 a las 16:00  
  `[mié 21/10 · 16:00 | jue 22/10 · 16:00 | vie 23/10 · 16:00 | Ninguno me va bien]`
- *Candidate:* 1  
  <sub>provide_info · option=1 · events: interview_booked</sub>
- **Sofía:** ¡Listo! Tu entrevista es el miércoles 21/10 a las 16:00 en Grupo Sazón Centro (Málaga). Trae tu carnet de conducir. Si no puedes ir, escríbeme y buscamos otro horario.

**Data:** `{"full_name": "Paula Ortiz", "has_drivers_license": true, "license_status": "yes", "license_type": "car", "location_raw": "Málaga, Teatinos", "city_id": "malaga", "city": "Málaga", "country": "ES", "zone": "Teatinos", "in_service_area": true, "availability": ["weekends"], "preferred_schedule": ["afternoon"], "experience_years": 0.0, "experience_months": 0, "start_date": "2026-11-02", "start_date_raw": "la fecha mejor el 2 de noviembre"}`
