# ex15_withdraws_and_comes_back

**End:** qualified · interview booked · triage: as expected

- **Sofía:** ¡Hola! 👋 Soy Sofía, la asistente virtual (IA) de Grupo Sazón. Te escribo por tu solicitud como repartidor/a: son 7 preguntas rápidas, unos 3 minutos. Tus datos solo se usan para este proceso de selección. ¿Empezamos?  
  `[¡Empezamos! | Tengo una pregunta]`
- *Candidate:* sí  
  <sub>affirm · events: stage_changed</sub>
- **Sofía:** ¡Genial, empezamos! ¿Cómo te llamas? Nombre y apellido, por favor.
- *Candidate:* Clara Vega  
  <sub>provide_info · {"full_name": "Clara Vega"} · events: field_valid</sub>
- **Sofía:** Encantada, Clara. ¿Tienes carnet de conducir en vigor, de coche o de moto?  
  `[Sí | No]`
- *Candidate:* sí, de moto  
  <sub>provide_info, affirm · {"drivers_license": "yes", "license_type": "motorbike"} · events: field_valid</sub>
- **Sofía:** Perfecto, carnet de moto en vigor. ¿En qué ciudad y zona te gustaría repartir?
- *Candidate:* Sevilla, Nervión  
  <sub>provide_info · {"location_text": "Sevilla, Nervión", "location_city_id": "sevilla", "location_zone": "Nervión", "location_outside_service_area": false} · events: field_valid, field_valid</sub>
- **Sofía:** Genial, Sevilla, zona Nervión. ¿Qué disponibilidad tienes: jornada completa, media jornada o fines de semana?  
  `[Jornada completa | Media jornada | Fines de semana]`
- *Candidate:* mira, ahora mismo no me interesa, gracias  
  <sub>opt_out, smalltalk · events: stage_changed, completed</sub>
- **Sofía:** Sin problema, Clara, gracias por tu tiempo. Si en algún momento te interesa retomarlo, escríbenos cuando quieras. ¡Que tengas muy buen día!
- *Candidate:* perdona, lo he pensado mejor y sí me interesa  
  <sub>correction, affirm · events: stage_changed</sub>
- **Sofía:** ¡Qué bien, te damos la bienvenida de nuevo! Seguimos entonces: ¿qué disponibilidad tienes, jornada completa, media jornada o fines de semana?  
  `[Jornada completa | Media jornada | Fines de semana]`
- *Candidate:* media jornada  
  <sub>provide_info · {"availability": ["part_time"]} · events: field_valid</sub>
- **Sofía:** Perfecto, media jornada. ¿Qué turno prefieres: mañana, tarde, noche o flexible?  
  `[Mañana | Tarde | Noche | Flexible]`
- *Candidate:* mañanas  
  <sub>provide_info · {"schedule": ["morning"]} · events: field_valid</sub>
- **Sofía:** Anotado, turno de mañana. ¿Tienes experiencia repartiendo? Si es así, cuéntame cuánto tiempo y en qué plataformas.
- *Candidate:* nunca  
  <sub>provide_info · {"experience_months": 0} · events: field_valid</sub>
- **Sofía:** No pasa nada, muchas personas empiezan sin experiencia repartiendo. ¿Cuándo podrías empezar?
- *Candidate:* en dos semanas  
  <sub>provide_info · {"start_date": {"kind": "in_weeks", "amount": 2, "weekday": null, "exact_date": null}} · events: field_valid, stage_changed</sub>
- **Sofía:** Antes de terminar, revisa tus datos:
• Nombre: Clara Vega
• Carnet de conducir: Sí (moto)
• Zona: Sevilla (Nervión)
• Disponibilidad: media jornada
• Turno: mañana
• Experiencia: Sin experiencia previa
• Inicio: martes 03/11

¿Está todo correcto?  
  `[Sí, todo correcto | Quiero corregir algo]`
- *Candidate:* sí  
  <sub>affirm · events: stage_changed, completed, interview_offered</sub>
- **Sofía:** ¡Genial, Clara, gracias por confirmar! Cumples los requisitos para pasar a la entrevista. Ahora mismo puedes elegir el horario que mejor te venga: te mando las opciones justo después de este mensaje.
- **Sofía:** Elige día y hora para tu entrevista (unos 20 minutos) en Grupo Sazón Triana (Sevilla):
1) miércoles 21/10 a las 12:30
2) jueves 22/10 a las 10:00
3) viernes 23/10 a las 10:00  
  `[mié 21/10 · 12:30 | jue 22/10 · 10:00 | vie 23/10 · 10:00 | Ninguno me va bien]`
- *Candidate:* 1  
  <sub>provide_info · option=1 · events: interview_booked</sub>
- **Sofía:** ¡Listo! Tu entrevista es el miércoles 21/10 a las 12:30 en Grupo Sazón Triana (Sevilla). Trae tu carnet de conducir. Si no puedes ir, escríbeme y buscamos otro horario.

**Data:** `{"full_name": "Clara Vega", "has_drivers_license": true, "license_status": "yes", "license_type": "motorbike", "location_raw": "Sevilla, Nervión", "city_id": "sevilla", "city": "Sevilla", "country": "ES", "zone": "Nervión", "in_service_area": true, "availability": ["part_time"], "preferred_schedule": ["morning"], "experience_years": 0.0, "experience_months": 0, "start_date": "2026-11-03", "start_date_raw": "en dos semanas"}`
