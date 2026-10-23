# ex02_personal_questions_to_the_bot

**End:** qualified · interview booked · triage: as expected

- **Sofía:** ¡Hola! 👋 Soy Sofía, la asistente virtual (IA) de Grupo Sazón. Te escribo por tu solicitud como repartidor/a: son 7 preguntas rápidas, unos 3 minutos. Tus datos solo se usan para este proceso de selección. ¿Empezamos?  
  `[¡Empezamos! | Tengo una pregunta]`
- *Candidate:* sí  
  <sub>affirm · events: stage_changed</sub>
- **Sofía:** ¡Genial, empezamos! ¿Cómo te llamas? Nombre y apellido, por favor.
- *Candidate:* Rubén Prieto  
  <sub>provide_info · {"full_name": "Rubén Prieto"} · events: field_valid</sub>
- **Sofía:** Encantada, Rubén. ¿Tienes carnet de conducir en vigor, ya sea de coche o de moto?  
  `[Sí | No]`
- *Candidate:* ¿cuántos años tienes tú?  
  <sub>question · faq=is_bot · events: question_answered</sub>
- **Sofía:** Soy una asistente virtual con inteligencia artificial, así que no tengo edad. Te hago estas preguntas para agilizar el proceso, y una persona del equipo de selección revisa siempre cada candidatura. ¿Tienes carnet de conducir en vigor, de coche o de moto?  
  `[Sí | No]`
- *Candidate:* sí, de moto  
  <sub>provide_info, affirm · {"drivers_license": "yes", "license_type": "motorbike"} · events: field_valid</sub>
- **Sofía:** Perfecto, con el carnet de moto en vigor vamos bien. ¿En qué ciudad y zona te gustaría repartir?
- *Candidate:* ¿tienes novio? jaja  
  <sub>question, smalltalk · events: question_unanswered</sub>
- **Sofía:** Jaja, soy una IA, así que de eso no tengo nada que contar. Sigamos con lo tuyo: ¿en qué ciudad y zona te gustaría repartir?
- *Candidate:* Valencia, Ruzafa  
  <sub>provide_info · {"location_text": "Valencia, Ruzafa", "location_city_id": "valencia", "location_zone": "Ruzafa", "location_outside_service_area": false} · events: field_valid, field_valid</sub>
- **Sofía:** Genial, Valencia y la zona de Ruzafa anotado. ¿Qué disponibilidad tienes: jornada completa, media jornada o fines de semana?  
  `[Jornada completa | Media jornada | Fines de semana]`
- *Candidate:* fines de semana  
  <sub>provide_info · {"availability": ["weekends"]} · events: field_valid</sub>
- **Sofía:** Perfecto, fines de semana. ¿Qué turno prefieres: mañana, tarde, noche o flexible?  
  `[Mañana | Tarde | Noche | Flexible]`
- *Candidate:* por la noche  
  <sub>provide_info · {"schedule": ["evening"]} · events: field_valid</sub>
- **Sofía:** Anotado, turno de noche. ¿Tienes experiencia repartiendo? Si es así, cuéntame cuánto tiempo y en qué plataformas.
- *Candidate:* dos años en Glovo  
  <sub>provide_info · {"experience_months": 24, "experience_platforms": ["Glovo"]} · events: field_valid, field_valid</sub>
- **Sofía:** Genial, dos años en Glovo es una buena experiencia. ¿Cuándo podrías empezar?
- *Candidate:* ya mismo  
  <sub>provide_info · {"start_date": {"kind": "immediate", "amount": null, "weekday": null, "exact_date": null}} · events: field_valid, stage_changed</sub>
- **Sofía:** Antes de terminar, revisa tus datos:
• Nombre: Rubén Prieto
• Carnet de conducir: Sí (moto)
• Zona: Valencia (Ruzafa)
• Disponibilidad: fines de semana
• Turno: noche
• Experiencia: 2 años (Glovo)
• Inicio: lo antes posible (martes 20/10)

¿Está todo correcto?  
  `[Sí, todo correcto | Quiero corregir algo]`
- *Candidate:* sí  
  <sub>affirm · events: stage_changed, completed, interview_offered</sub>
- **Sofía:** ¡Genial, Rubén! Con lo que me has contado cumples los requisitos para pasar a entrevista. Ahora mismo puedes elegir el horario que mejor te venga: te envío las opciones justo después de este mensaje.
- **Sofía:** Elige día y hora para tu entrevista (unos 20 minutos) en Grupo Sazón Ruzafa (Valencia):
1) miércoles 21/10 a las 17:00
2) jueves 22/10 a las 17:00
3) viernes 23/10 a las 17:00  
  `[mié 21/10 · 17:00 | jue 22/10 · 17:00 | vie 23/10 · 17:00 | Ninguno me va bien]`
- *Candidate:* la segunda  
  <sub>provide_info · option=2 · events: interview_booked</sub>
- **Sofía:** ¡Listo! Tu entrevista es el jueves 22/10 a las 17:00 en Grupo Sazón Ruzafa (Valencia). Trae tu carnet de conducir. Si no puedes ir, escríbeme y buscamos otro horario.

**Data:** `{"full_name": "Rubén Prieto", "has_drivers_license": true, "license_status": "yes", "license_type": "motorbike", "location_raw": "Valencia, Ruzafa", "city_id": "valencia", "city": "Valencia", "country": "ES", "zone": "Ruzafa", "in_service_area": true, "availability": ["weekends"], "preferred_schedule": ["evening"], "experience_years": 2.0, "experience_months": 24, "experience_platforms": ["Glovo"], "start_date": "2026-10-20", "start_date_raw": "ya mismo"}`
