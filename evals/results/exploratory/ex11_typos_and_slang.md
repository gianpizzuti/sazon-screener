# ex11_typos_and_slang

**End:** qualified · interview booked · triage: as expected

- **Sofía:** ¡Hola! 👋 Soy Sofía, la asistente virtual (IA) de Grupo Sazón. Te escribo por tu solicitud como repartidor/a: son 7 preguntas rápidas, unos 3 minutos. Tus datos solo se usan para este proceso de selección. ¿Empezamos?  
  `[¡Empezamos! | Tengo una pregunta]`
- *Candidate:* sii vamoss  
  <sub>affirm · events: stage_changed</sub>
- **Sofía:** ¡Genial, empezamos! ¿Cómo te llamas? Nombre y apellido, por favor.
- *Candidate:* soy jorge mrtn lopez  
  <sub>provide_info · {"full_name": "jorge mrtn lopez"} · events: field_valid</sub>
- **Sofía:** Encantada, Jorge. ¿Tienes carnet de conducir en vigor, de coche o de moto?  
  `[Sí | No]`
- *Candidate:* si tngo carnet d moto  
  <sub>provide_info, affirm · {"drivers_license": "yes", "license_type": "motorbike"} · events: field_valid</sub>
- **Sofía:** Perfecto, carnet de moto en vigor, apuntado. ¿En qué ciudad y zona te gustaría repartir?
- *Candidate:* vivo n madriz centro  
  <sub>provide_info · {"location_text": "vivo n madriz centro", "location_city_id": "madrid", "location_zone": "Centro", "location_outside_service_area": false} · events: field_valid, field_valid</sub>
- **Sofía:** Madrid Centro, anotado. ¿Qué disponibilidad tienes: jornada completa, media jornada o fines de semana?  
  `[Jornada completa | Media jornada | Fines de semana]`
- *Candidate:* media jornda  
  <sub>provide_info · {"availability": ["part_time"]} · events: field_valid</sub>
- **Sofía:** Media jornada, perfecto. ¿Qué turno prefieres: mañana, tarde, noche o flexible?  
  `[Mañana | Tarde | Noche | Flexible]`
- *Candidate:* x las tardes  
  <sub>provide_info · {"schedule": ["afternoon"]} · events: field_valid</sub>
- **Sofía:** Turno de tarde, anotado. ¿Tienes experiencia como repartidor/a? Si es así, cuéntame cuánto tiempo y en qué plataformas.
- *Candidate:* 1 año n glovo  
  <sub>provide_info · {"experience_months": 12, "experience_platforms": ["Glovo"]} · events: field_valid, field_valid</sub>
- **Sofía:** Un año repartiendo con Glovo, genial. ¿Cuándo podrías empezar?
- *Candidate:* l lunes q viene  
  <sub>provide_info · {"start_date": {"kind": "next_weekday", "amount": null, "weekday": 0, "exact_date": null}} · events: field_valid, stage_changed</sub>
- **Sofía:** Antes de terminar, revisa tus datos:
• Nombre: Jorge Mrtn Lopez
• Carnet de conducir: Sí (moto)
• Zona: Madrid (Centro)
• Disponibilidad: media jornada
• Turno: tarde
• Experiencia: 1 año (Glovo)
• Inicio: lunes 26/10

¿Está todo correcto?  
  `[Sí, todo correcto | Quiero corregir algo]`
- *Candidate:* sip  
  <sub>affirm · events: stage_changed, completed, interview_offered</sub>
- **Sofía:** Genial, Jorge, ya tenemos todo. Cumples los requisitos para pasar a la entrevista, y puedes elegir el horario ahora mismo: te mando las opciones justo después de este mensaje. ¡Gracias por tu tiempo!
- **Sofía:** Elige día y hora para tu entrevista (unos 20 minutos) en Grupo Sazón Malasaña (Madrid):
1) miércoles 21/10 a las 16:00
2) jueves 22/10 a las 16:00
3) viernes 23/10 a las 16:00  
  `[mié 21/10 · 16:00 | jue 22/10 · 16:00 | vie 23/10 · 16:00 | Ninguno me va bien]`
- *Candidate:* 1  
  <sub>provide_info · option=1 · events: interview_booked</sub>
- **Sofía:** ¡Listo! Tu entrevista es el miércoles 21/10 a las 16:00 en Grupo Sazón Malasaña (Madrid). Trae tu carnet de conducir. Si no puedes ir, escríbeme y buscamos otro horario.

**Data:** `{"full_name": "Jorge Mrtn Lopez", "has_drivers_license": true, "license_status": "yes", "license_type": "motorbike", "location_raw": "vivo n madriz centro", "city_id": "madrid", "city": "Madrid", "country": "ES", "zone": "Centro", "in_service_area": true, "availability": ["part_time"], "preferred_schedule": ["afternoon"], "experience_years": 1.0, "experience_months": 12, "experience_platforms": ["Glovo"], "start_date": "2026-10-26", "start_date_raw": "l lunes q viene"}`
