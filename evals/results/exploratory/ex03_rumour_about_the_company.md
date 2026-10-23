# ex03_rumour_about_the_company

**End:** qualified · interview handed_off · triage: as expected

- **Sofía:** ¡Hola! 👋 Soy Sofía, la asistente virtual (IA) de Grupo Sazón. Te escribo por tu solicitud como repartidor/a: son 7 preguntas rápidas, unos 3 minutos. Tus datos solo se usan para este proceso de selección. ¿Empezamos?  
  `[¡Empezamos! | Tengo una pregunta]`
- *Candidate:* sí, empecemos  
  <sub>affirm · events: stage_changed</sub>
- **Sofía:** ¡Genial, vamos allá! Para empezar, ¿cómo te llamas? Nombre y apellido, por favor.
- *Candidate:* Lorena Díaz Vidal  
  <sub>provide_info · {"full_name": "Lorena Díaz Vidal"} · events: field_valid</sub>
- **Sofía:** Encantada, Lorena. Vamos con la siguiente: ¿tienes carnet de conducir en vigor, de coche o de moto?  
  `[Sí | No]`
- *Candidate:* sí, carnet de coche. Oye, me han dicho que en Sazón pagáis tarde, ¿es verdad?  
  <sub>provide_info, affirm, question · {"drivers_license": "yes", "license_type": "car"} · faq=payday · events: question_answered, field_valid</sub>
- **Sofía:** Perfecto, con el carnet de coche en vigor vamos bien. Sobre lo del pago, lo que te puedo confirmar es que se cobra por nómina mensual, por transferencia a tu cuenta; no tengo más detalle sobre plazos, eso te lo concreta el equipo de selección. ¿En qué ciudad y zona te gustaría repartir?
- *Candidate:* Sevilla, Triana  
  <sub>provide_info · {"location_text": "Sevilla, Triana", "location_city_id": "sevilla", "location_zone": "Triana", "location_outside_service_area": false} · events: field_valid, field_valid</sub>
- **Sofía:** Genial, Sevilla y la zona de Triana. ¿Qué disponibilidad tienes: jornada completa, media jornada o fines de semana?  
  `[Jornada completa | Media jornada | Fines de semana]`
- *Candidate:* jornada completa  
  <sub>provide_info · {"availability": ["full_time"]} · events: field_valid</sub>
- **Sofía:** Perfecto, jornada completa. ¿Y qué turno prefieres: mañana, tarde, noche o flexible?  
  `[Mañana | Tarde | Noche | Flexible]`
- *Candidate:* flexible  
  <sub>provide_info · {"schedule": ["flexible"]} · events: field_valid</sub>
- **Sofía:** Genial, turno flexible. ¿Tienes experiencia como repartidor/a? Si es así, cuéntame cuánto tiempo y en qué plataformas.
- *Candidate:* un año en Just Eat  
  <sub>provide_info · {"experience_months": 12, "experience_platforms": ["Just Eat"]} · events: field_valid, field_valid</sub>
- **Sofía:** Estupendo, un año repartiendo con Just Eat es una buena experiencia. ¿Cuándo podrías empezar?
- *Candidate:* en dos semanas  
  <sub>provide_info · {"start_date": {"kind": "in_weeks", "amount": 2, "weekday": null, "exact_date": null}} · events: field_valid, stage_changed</sub>
- **Sofía:** Antes de terminar, revisa tus datos:
• Nombre: Lorena Díaz Vidal
• Carnet de conducir: Sí (coche)
• Zona: Sevilla (Triana)
• Disponibilidad: jornada completa
• Turno: flexible
• Experiencia: 1 año (Just Eat)
• Inicio: martes 03/11

¿Está todo correcto?  
  `[Sí, todo correcto | Quiero corregir algo]`
- *Candidate:* sí, correcto  
  <sub>affirm · events: stage_changed, completed, interview_offered</sub>
- **Sofía:** ¡Gracias, Lorena! Cumples los requisitos para pasar a la entrevista, y ya puedes elegir el horario que mejor te venga: te mando las opciones justo después de este mensaje. ¡Mucha suerte!
- **Sofía:** Elige día y hora para tu entrevista (unos 20 minutos) en Grupo Sazón Triana (Sevilla):
1) miércoles 21/10 a las 12:30
2) jueves 22/10 a las 10:00
3) viernes 23/10 a las 10:00  
  `[mié 21/10 · 12:30 | jue 22/10 · 10:00 | vie 23/10 · 10:00 | Ninguno me va bien]`
- *Candidate:* Ninguno me va bien  
  <sub>deny, provide_info · events: interview_offered</sub>
- **Sofía:** Sin problema. Estas son otras opciones en Grupo Sazón Triana (Sevilla):
1) miércoles 21/10 a las 16:00
2) jueves 22/10 a las 10:30
3) viernes 23/10 a las 10:30  
  `[mié 21/10 · 16:00 | jue 22/10 · 10:30 | vie 23/10 · 10:30 | Ninguno me va bien]`
- *Candidate:* Ninguno me va bien  
  <sub>deny, provide_info · events: interview_handoff</sub>
- **Sofía:** Vale. Una persona del equipo de selección te escribirá para encontrar un horario que te venga bien.

**Data:** `{"full_name": "Lorena Díaz Vidal", "has_drivers_license": true, "license_status": "yes", "license_type": "car", "location_raw": "Sevilla, Triana", "city_id": "sevilla", "city": "Sevilla", "country": "ES", "zone": "Triana", "in_service_area": true, "availability": ["full_time"], "preferred_schedule": ["flexible"], "experience_years": 1.0, "experience_months": 12, "experience_platforms": ["Just Eat"], "start_date": "2026-11-03", "start_date_raw": "en dos semanas"}`
**Flags:** scheduling_needed
