# ex05_changes_availability_later

**End:** qualified · interview booked · triage: as expected

- **Sofía:** ¡Hola! 👋 Soy Sofía, la asistente virtual (IA) de Grupo Sazón. Te escribo por tu solicitud como repartidor/a: son 7 preguntas rápidas, unos 3 minutos. Tus datos solo se usan para este proceso de selección. ¿Empezamos?  
  `[¡Empezamos! | Tengo una pregunta]`
- *Candidate:* dale  
  <sub>affirm · events: stage_changed</sub>
- **Sofía:** ¡Genial, empezamos! ¿Cómo te llamas? Nombre y apellido, por favor.
- *Candidate:* Iván Romero  
  <sub>provide_info · {"full_name": "Iván Romero"} · events: field_valid</sub>
- **Sofía:** Encantada, Iván. ¿Tienes carnet de conducir en vigor, ya sea de coche o de moto?  
  `[Sí | No]`
- *Candidate:* sí, de moto  
  <sub>affirm, provide_info · {"drivers_license": "yes", "license_type": "motorbike"} · events: field_valid</sub>
- **Sofía:** Perfecto, carnet de moto en vigor, anotado. ¿En qué ciudad y zona te gustaría repartir?
- *Candidate:* Barcelona, Gràcia  
  <sub>provide_info · {"location_text": "Barcelona, Gràcia", "location_city_id": "barcelona", "location_zone": "Gràcia", "location_outside_service_area": false} · events: field_valid, field_valid</sub>
- **Sofía:** Genial, Barcelona y la zona de Gràcia, anotado. ¿Qué disponibilidad tienes: jornada completa, media jornada o fines de semana?  
  `[Jornada completa | Media jornada | Fines de semana]`
- *Candidate:* media jornada  
  <sub>provide_info · {"availability": ["part_time"]} · events: field_valid</sub>
- **Sofía:** Media jornada, perfecto. ¿Qué turno prefieres: mañana, tarde, noche o flexible?  
  `[Mañana | Tarde | Noche | Flexible]`
- *Candidate:* mañanas  
  <sub>provide_info · {"schedule": ["morning"]} · events: field_valid</sub>
- **Sofía:** Vale, turno de mañana, anotado. ¿Tienes experiencia como repartidor/a? Si es así, ¿cuánto tiempo y en qué plataformas?
- *Candidate:* ah, y mejor jornada completa en vez de media, que lo he pensado  
  <sub>correction, provide_info · {"availability": ["full_time"]} · events: field_valid, field_corrected</sub>
- **Sofía:** Hecho, jornada completa, apuntado. Y volviendo a la pregunta: ¿tienes experiencia como repartidor/a? Si es así, ¿cuánto tiempo y en qué plataformas?
- *Candidate:* seis meses con Deliveroo  
  <sub>provide_info · {"experience_months": 6, "experience_platforms": ["Deliveroo"]} · events: field_valid, field_valid</sub>
- **Sofía:** Seis meses con Deliveroo, buena experiencia. ¿Cuándo podrías empezar?
- *Candidate:* el 2 de noviembre  
  <sub>provide_info · {"start_date": {"kind": "exact_date", "amount": null, "weekday": null, "exact_date": "2026-11-02"}} · events: field_valid, stage_changed</sub>
- **Sofía:** Antes de terminar, revisa tus datos:
• Nombre: Iván Romero
• Carnet de conducir: Sí (moto)
• Zona: Barcelona (Gràcia)
• Disponibilidad: jornada completa
• Turno: mañana
• Experiencia: 6 meses (Deliveroo)
• Inicio: lunes 02/11

¿Está todo correcto?  
  `[Sí, todo correcto | Quiero corregir algo]`
- *Candidate:* sí  
  <sub>affirm · events: stage_changed, completed, interview_offered</sub>
- **Sofía:** Perfecto, Iván, cumples los requisitos para pasar a la entrevista. Ahora mismo puedes elegir el horario que mejor te venga: te envío las opciones justo después de este mensaje. ¡Gracias por tu tiempo!
- **Sofía:** Elige día y hora para tu entrevista (unos 20 minutos) en Grupo Sazón Gràcia (Barcelona):
1) miércoles 21/10 a las 12:30
2) jueves 22/10 a las 10:00
3) viernes 23/10 a las 10:00  
  `[mié 21/10 · 12:30 | jue 22/10 · 10:00 | vie 23/10 · 10:00 | Ninguno me va bien]`
- *Candidate:* 1  
  <sub>provide_info · option=1 · events: interview_booked</sub>
- **Sofía:** ¡Listo! Tu entrevista es el miércoles 21/10 a las 12:30 en Grupo Sazón Gràcia (Barcelona). Trae tu carnet de conducir. Si no puedes ir, escríbeme y buscamos otro horario.

**Data:** `{"full_name": "Iván Romero", "has_drivers_license": true, "license_status": "yes", "license_type": "motorbike", "location_raw": "Barcelona, Gràcia", "city_id": "barcelona", "city": "Barcelona", "country": "ES", "zone": "Gràcia", "in_service_area": true, "availability": ["full_time"], "preferred_schedule": ["morning"], "experience_years": 0.5, "experience_months": 6, "experience_platforms": ["Deliveroo"], "start_date": "2026-11-02", "start_date_raw": "el 2 de noviembre"}`
