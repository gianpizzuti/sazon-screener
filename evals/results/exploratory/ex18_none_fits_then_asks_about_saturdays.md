# ex18_none_fits_then_asks_about_saturdays

**End:** qualified · interview booked · triage: as expected

- **Sofía:** ¡Hola! 👋 Soy Sofía, la asistente virtual (IA) de Grupo Sazón. Te escribo por tu solicitud como repartidor/a: son 7 preguntas rápidas, unos 3 minutos. Tus datos solo se usan para este proceso de selección. ¿Empezamos?  
  `[¡Empezamos! | Tengo una pregunta]`
- *Candidate:* sí  
  <sub>affirm · events: stage_changed</sub>
- **Sofía:** Genial, vamos con la primera. ¿Cómo te llamas? Nombre y apellido, por favor.
- *Candidate:* Alba Moreno  
  <sub>provide_info · {"full_name": "Alba Moreno"} · events: field_valid</sub>
- **Sofía:** Encantada, Alba. ¿Tienes carnet de conducir en vigor, ya sea de coche o de moto?  
  `[Sí | No]`
- *Candidate:* sí, de coche  
  <sub>affirm, provide_info · {"drivers_license": "yes", "license_type": "car"} · events: field_valid</sub>
- **Sofía:** Perfecto, con el carnet de coche ya tenemos esa parte. ¿En qué ciudad y zona te gustaría repartir?
- *Candidate:* Madrid, Retiro  
  <sub>provide_info · {"location_text": "Madrid, Retiro", "location_city_id": "madrid", "location_zone": "Retiro", "location_outside_service_area": false} · events: field_valid, field_valid</sub>
- **Sofía:** Madrid, zona Retiro, anotado. ¿Qué disponibilidad tienes: jornada completa, media jornada o fines de semana?  
  `[Jornada completa | Media jornada | Fines de semana]`
- *Candidate:* jornada completa  
  <sub>provide_info · {"availability": ["full_time"]} · events: field_valid</sub>
- **Sofía:** Jornada completa, perfecto. ¿Qué turno prefieres: mañana, tarde, noche o flexible?  
  `[Mañana | Tarde | Noche | Flexible]`
- *Candidate:* mañanas  
  <sub>provide_info · {"schedule": ["morning"]} · events: field_valid</sub>
- **Sofía:** Turno de mañana, apuntado. ¿Tienes experiencia como repartidor/a? Si es así, ¿cuánto tiempo y en qué plataformas?
- *Candidate:* sin experiencia  
  <sub>provide_info · {"experience_months": 0} · events: field_valid</sub>
- **Sofía:** No pasa nada, aquí también damos la bienvenida a quien empieza. ¿Cuándo podrías incorporarte?
- *Candidate:* el lunes  
  <sub>provide_info · {"start_date": {"kind": "next_weekday", "amount": null, "weekday": 0, "exact_date": null}} · events: field_valid, stage_changed</sub>
- **Sofía:** Antes de terminar, revisa tus datos:
• Nombre: Alba Moreno
• Carnet de conducir: Sí (coche)
• Zona: Madrid (Retiro)
• Disponibilidad: jornada completa
• Turno: mañana
• Experiencia: Sin experiencia previa
• Inicio: lunes 26/10

¿Está todo correcto?  
  `[Sí, todo correcto | Quiero corregir algo]`
- *Candidate:* sí  
  <sub>affirm · events: stage_changed, completed, interview_offered</sub>
- **Sofía:** ¡Gracias, Alba! Cumples los requisitos para pasar a la entrevista, y ya puedes elegir el horario que mejor te venga: te envío las opciones justo después de este mensaje. Un placer hablar contigo.
- **Sofía:** Elige día y hora para tu entrevista (unos 20 minutos) en Grupo Sazón Malasaña (Madrid):
1) miércoles 21/10 a las 12:30
2) jueves 22/10 a las 10:00
3) viernes 23/10 a las 10:00  
  `[mié 21/10 · 12:30 | jue 22/10 · 10:00 | vie 23/10 · 10:00 | Ninguno me va bien]`
- *Candidate:* ¿no hay entrevistas los sábados?  
  <sub>question · faq=interviews · events: question_answered</sub>
- **Sofía:** Los sábados no hay entrevistas: son de lunes a viernes, de 10:00 a 13:00 y de 16:00 a 19:00. Si ninguno de los horarios te va bien, una persona del equipo te ayuda a encontrar otro. ¿Con cuál de los tres que te he enviado te quedas?
- *Candidate:* Ninguno me va bien  
  <sub>deny · events: interview_offered</sub>
- **Sofía:** Sin problema. Estas son otras opciones en Grupo Sazón Malasaña (Madrid):
1) jueves 22/10 a las 10:30
2) viernes 23/10 a las 10:30
3) lunes 26/10 a las 10:00  
  `[jue 22/10 · 10:30 | vie 23/10 · 10:30 | lun 26/10 · 10:00 | Ninguno me va bien]`
- *Candidate:* vale, el primero entonces  
  <sub>provide_info · option=1 · events: interview_booked</sub>
- **Sofía:** ¡Listo! Tu entrevista es el jueves 22/10 a las 10:30 en Grupo Sazón Malasaña (Madrid). Trae tu carnet de conducir. Si no puedes ir, escríbeme y buscamos otro horario.

**Data:** `{"full_name": "Alba Moreno", "has_drivers_license": true, "license_status": "yes", "license_type": "car", "location_raw": "Madrid, Retiro", "city_id": "madrid", "city": "Madrid", "country": "ES", "zone": "Retiro", "in_service_area": true, "availability": ["full_time"], "preferred_schedule": ["morning"], "experience_years": 0.0, "experience_months": 0, "start_date": "2026-10-26", "start_date_raw": "el lunes"}`
