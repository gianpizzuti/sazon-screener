# ex09_emojis_and_one_word_replies

**End:** qualified · interview booked · triage: as expected

- **Sofía:** ¡Hola! 👋 Soy Sofía, la asistente virtual (IA) de Grupo Sazón. Te escribo por tu solicitud como repartidor/a: son 7 preguntas rápidas, unos 3 minutos. Tus datos solo se usan para este proceso de selección. ¿Empezamos?  
  `[¡Empezamos! | Tengo una pregunta]`
- *Candidate:* 👍  
  <sub>affirm · events: stage_changed</sub>
- **Sofía:** ¡Genial, empezamos! ¿Cómo te llamas? Nombre y apellido, por favor.
- *Candidate:* Nacho Ruiz  
  <sub>provide_info · {"full_name": "Nacho Ruiz"} · events: field_valid</sub>
- **Sofía:** Encantada, Nacho. ¿Tienes carnet de conducir en vigor, ya sea de coche o de moto?  
  `[Sí | No]`
- *Candidate:* si  
  <sub>affirm, provide_info · {"drivers_license": "yes"} · events: field_valid</sub>
- **Sofía:** Perfecto, gracias. ¿Tu carnet es de coche, de moto o de ambos?  
  `[Coche | Moto | Los dos]`
- *Candidate:* ?  
  <sub>other</sub>
- **Sofía:** Perdona, me adelanté. Dejemos eso por ahora: ¿en qué ciudad y zona te gustaría repartir?
- *Candidate:* coche  
  <sub>provide_info · {"license_type": "car"} · events: field_valid, field_refined</sub>
- **Sofía:** Anotado, carnet de coche. ¿En qué ciudad y zona te gustaría repartir?
- *Candidate:* madrid  
  <sub>provide_info · {"location_text": "madrid", "location_city_id": "madrid", "location_outside_service_area": false} · events: field_valid</sub>
- **Sofía:** Madrid, perfecto. ¿Y en qué zona o barrio? Es opcional, pero nos ayuda a asignarte el restaurante más cercano. Puedes tocar una de las opciones o escribirme tu barrio.  
  `[Centro | Norte | Sur | Este | Cualquier zona]`
- *Candidate:* Cualquier zona  
  <sub>provide_info · events: field_skipped</sub>
- **Sofía:** Sin problema, cualquier zona. ¿Qué disponibilidad tienes: jornada completa, media jornada o fines de semana?  
  `[Jornada completa | Media jornada | Fines de semana]`
- *Candidate:* ok  
  <sub>other</sub>
- **Sofía:** Vale, creo que mi pregunta no estaba clara. ¿Cuánto tiempo podrías trabajar: jornada completa, media jornada o solo fines de semana?  
  `[Jornada completa | Media jornada | Fines de semana]`
- *Candidate:* media  
  <sub>provide_info · events: field_unclear</sub>
- **Sofía:** Media jornada, anotado. ¿Qué turno prefieres: mañana, tarde, noche o flexible?  
  `[Mañana | Tarde | Noche | Flexible]`
- *Candidate:* noche  
  <sub>provide_info · {"schedule": ["evening"]} · events: field_valid</sub>
- **Sofía:** Turno de noche, anotado. ¿Tienes experiencia repartiendo? Si es así, cuéntame cuánto tiempo y en qué plataformas.
- *Candidate:* no  
  <sub>deny · {"experience_months": 0} · events: field_valid</sub>
- **Sofía:** Sin problema, no hace falta experiencia previa. ¿Cuándo podrías empezar?
- *Candidate:* ya  
  <sub>provide_info · {"start_date": {"kind": "immediate", "amount": null, "weekday": null, "exact_date": null}} · events: field_valid, stage_changed</sub>
- **Sofía:** Antes de terminar, revisa tus datos:
• Nombre: Nacho Ruiz
• Carnet de conducir: Sí (coche)
• Zona: Madrid
• Disponibilidad: (por confirmar)
• Turno: noche
• Experiencia: Sin experiencia previa
• Inicio: lo antes posible (martes 20/10)

¿Está todo correcto?  
  `[Sí, todo correcto | Quiero corregir algo]`
- *Candidate:* 👌  
  <sub>affirm · events: stage_changed, completed, interview_offered</sub>
- **Sofía:** ¡Genial, Nacho, gracias por tu tiempo! Cumples los requisitos para pasar a la entrevista, y puedes elegir el horario que mejor te venga ahora mismo: te envío las opciones justo después de este mensaje.
- **Sofía:** Elige día y hora para tu entrevista (unos 20 minutos) en Grupo Sazón Malasaña (Madrid):
1) miércoles 21/10 a las 17:00
2) jueves 22/10 a las 17:00
3) viernes 23/10 a las 17:00  
  `[mié 21/10 · 17:00 | jue 22/10 · 17:00 | vie 23/10 · 17:00 | Ninguno me va bien]`
- *Candidate:* 1  
  <sub>provide_info · option=1 · events: interview_booked</sub>
- **Sofía:** ¡Listo! Tu entrevista es el miércoles 21/10 a las 17:00 en Grupo Sazón Malasaña (Madrid). Trae tu carnet de conducir. Si no puedes ir, escríbeme y buscamos otro horario.

**Data:** `{"full_name": "Nacho Ruiz", "has_drivers_license": true, "license_status": "yes", "license_type": "car", "location_raw": "madrid", "city_id": "madrid", "city": "Madrid", "country": "ES", "in_service_area": true, "preferred_schedule": ["evening"], "experience_years": 0.0, "experience_months": 0, "start_date": "2026-10-20", "start_date_raw": "ya"}`
**Flags:** unclear_field
