# ex19_reschedules_the_interview

**End:** qualified · interview booked · triage: as expected

- **Sofía:** ¡Hola! 👋 Soy Sofía, la asistente virtual (IA) de Grupo Sazón. Te escribo por tu solicitud como repartidor/a: son 7 preguntas rápidas, unos 3 minutos. Tus datos solo se usan para este proceso de selección. ¿Empezamos?  
  `[¡Empezamos! | Tengo una pregunta]`
- *Candidate:* sí  
  <sub>affirm · events: stage_changed</sub>
- **Sofía:** ¡Genial, empezamos! ¿Cómo te llamas? Nombre y apellido, por favor.
- *Candidate:* Tomás Herrera  
  <sub>provide_info · {"full_name": "Tomás Herrera"} · events: field_valid</sub>
- **Sofía:** Encantada, Tomás. ¿Tienes carnet de conducir en vigor, ya sea de coche o de moto?  
  `[Sí | No]`
- *Candidate:* sí, de moto  
  <sub>provide_info, affirm · {"drivers_license": "yes", "license_type": "motorbike"} · events: field_valid</sub>
- **Sofía:** Perfecto, carnet de moto en vigor. ¿En qué ciudad y zona te gustaría repartir?
- *Candidate:* Valencia, Campanar  
  <sub>provide_info · {"location_text": "Valencia, Campanar", "location_city_id": "valencia", "location_zone": "Campanar", "location_outside_service_area": false} · events: field_valid, field_valid</sub>
- **Sofía:** Genial, Valencia y la zona de Campanar. ¿Qué disponibilidad tienes: jornada completa, media jornada o fines de semana?  
  `[Jornada completa | Media jornada | Fines de semana]`
- *Candidate:* media jornada  
  <sub>provide_info · {"availability": ["part_time"]} · events: field_valid</sub>
- **Sofía:** Perfecto, media jornada. ¿Qué turno prefieres: mañana, tarde, noche o flexible?  
  `[Mañana | Tarde | Noche | Flexible]`
- *Candidate:* tarde  
  <sub>provide_info · {"schedule": ["afternoon"]} · events: field_valid</sub>
- **Sofía:** Anotado, turno de tarde. ¿Tienes experiencia como repartidor/a? Si es así, ¿cuánto tiempo y en qué plataformas?
- *Candidate:* seis meses en Glovo  
  <sub>provide_info · {"experience_months": 6, "experience_platforms": ["Glovo"]} · events: field_valid, field_valid</sub>
- **Sofía:** Seis meses en Glovo, genial. ¿Cuándo podrías empezar?
- *Candidate:* ya  
  <sub>provide_info · {"start_date": {"kind": "immediate", "amount": null, "weekday": null, "exact_date": null}} · events: field_valid, stage_changed</sub>
- **Sofía:** Antes de terminar, revisa tus datos:
• Nombre: Tomás Herrera
• Carnet de conducir: Sí (moto)
• Zona: Valencia (Campanar)
• Disponibilidad: media jornada
• Turno: tarde
• Experiencia: 6 meses (Glovo)
• Inicio: lo antes posible (martes 20/10)

¿Está todo correcto?  
  `[Sí, todo correcto | Quiero corregir algo]`
- *Candidate:* sí  
  <sub>affirm · events: stage_changed, completed, interview_offered</sub>
- **Sofía:** ¡Perfecto, Tomás! Cumples los requisitos para pasar a la entrevista, y ya puedes elegir el horario que mejor te venga: en un momento te mando las opciones. Gracias por tu tiempo y por tu interés en Grupo Sazón.
- **Sofía:** Elige día y hora para tu entrevista (unos 20 minutos) en Grupo Sazón Ruzafa (Valencia):
1) miércoles 21/10 a las 16:00
2) jueves 22/10 a las 16:00
3) viernes 23/10 a las 16:00  
  `[mié 21/10 · 16:00 | jue 22/10 · 16:00 | vie 23/10 · 16:00 | Ninguno me va bien]`
- *Candidate:* 1  
  <sub>provide_info · option=1 · events: interview_booked</sub>
- **Sofía:** ¡Listo! Tu entrevista es el miércoles 21/10 a las 16:00 en Grupo Sazón Ruzafa (Valencia). Trae tu carnet de conducir. Si no puedes ir, escríbeme y buscamos otro horario.
- *Candidate:* uy, al final ese día no puedo ir, ¿lo podemos cambiar?  
  <sub>postpone, question · faq=interviews · events: question_answered, interview_cancelled, interview_offered</sub>
- **Sofía:** Sin problema. Estas son otras opciones en Grupo Sazón Ruzafa (Valencia):
1) miércoles 21/10 a las 16:30
2) jueves 22/10 a las 16:30
3) viernes 23/10 a las 16:30  
  `[mié 21/10 · 16:30 | jue 22/10 · 16:30 | vie 23/10 · 16:30 | Ninguno me va bien]`
- *Candidate:* 2  
  <sub>provide_info · option=2 · events: interview_booked</sub>
- **Sofía:** ¡Listo! Tu entrevista es el jueves 22/10 a las 16:30 en Grupo Sazón Ruzafa (Valencia). Trae tu carnet de conducir. Si no puedes ir, escríbeme y buscamos otro horario.

**Data:** `{"full_name": "Tomás Herrera", "has_drivers_license": true, "license_status": "yes", "license_type": "motorbike", "location_raw": "Valencia, Campanar", "city_id": "valencia", "city": "Valencia", "country": "ES", "zone": "Campanar", "in_service_area": true, "availability": ["part_time"], "preferred_schedule": ["afternoon"], "experience_years": 0.5, "experience_months": 6, "experience_platforms": ["Glovo"], "start_date": "2026-10-20", "start_date_raw": "ya"}`
