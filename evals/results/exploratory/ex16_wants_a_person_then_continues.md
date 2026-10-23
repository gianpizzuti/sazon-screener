# ex16_wants_a_person_then_continues

**End:** qualified · interview booked · triage: as expected

- **Sofía:** ¡Hola! 👋 Soy Sofía, la asistente virtual (IA) de Grupo Sazón. Te escribo por tu solicitud como repartidor/a: son 7 preguntas rápidas, unos 3 minutos. Tus datos solo se usan para este proceso de selección. ¿Empezamos?  
  `[¡Empezamos! | Tengo una pregunta]`
- *Candidate:* hola, quiero hablar con una persona de recursos humanos, no con una máquina  
  <sub>human_request · events: human_requested, stage_changed</sub>
- **Sofía:** Claro, lo entiendo. Soy una IA, pero una persona del equipo de selección revisa todas las solicitudes y puede ponerse en contacto contigo. Si me respondes ahora a las preguntas, todo irá más rápido. ¿Cómo te llamas? Nombre y apellido, por favor.
- *Candidate:* vale, sigamos. Soy Óscar Benítez  
  <sub>provide_info · {"full_name": "Óscar Benítez"} · events: field_valid</sub>
- **Sofía:** Gracias, Óscar, encantada. Vamos con la primera: ¿tienes carnet de conducir en vigor, ya sea de coche o de moto?  
  `[Sí | No]`
- *Candidate:* sí, de coche  
  <sub>provide_info, affirm · {"drivers_license": "yes", "license_type": "car"} · events: field_valid</sub>
- **Sofía:** Perfecto, carnet de coche en vigor, eso nos viene bien. ¿En qué ciudad y zona te gustaría repartir?
- *Candidate:* Málaga, El Palo  
  <sub>provide_info · {"location_text": "Málaga, El Palo", "location_city_id": "malaga", "location_zone": "El Palo", "location_outside_service_area": false} · events: field_valid, field_valid</sub>
- **Sofía:** Genial, Málaga, zona El Palo, anotado. ¿Qué disponibilidad tienes: jornada completa, media jornada o fines de semana?  
  `[Jornada completa | Media jornada | Fines de semana]`
- *Candidate:* jornada completa  
  <sub>provide_info · {"availability": ["full_time"]} · events: field_valid</sub>
- **Sofía:** Perfecto, jornada completa. ¿Qué turno prefieres: mañana, tarde, noche o flexible?  
  `[Mañana | Tarde | Noche | Flexible]`
- *Candidate:* flexible  
  <sub>provide_info · {"schedule": ["flexible"]} · events: field_valid</sub>
- **Sofía:** Genial, turno flexible. ¿Tienes experiencia como repartidor/a? Si es así, ¿cuánto tiempo y en qué plataformas?
- *Candidate:* un año en Glovo  
  <sub>provide_info · {"experience_months": 12, "experience_platforms": ["Glovo"]} · events: field_valid, field_valid</sub>
- **Sofía:** Genial, un año repartiendo con Glovo es una buena experiencia. ¿Cuándo podrías empezar?
- *Candidate:* el lunes  
  <sub>provide_info · {"start_date": {"kind": "next_weekday", "amount": null, "weekday": 0, "exact_date": null}} · events: field_valid, stage_changed</sub>
- **Sofía:** Antes de terminar, revisa tus datos:
• Nombre: Óscar Benítez
• Carnet de conducir: Sí (coche)
• Zona: Málaga (El Palo)
• Disponibilidad: jornada completa
• Turno: flexible
• Experiencia: 1 año (Glovo)
• Inicio: lunes 26/10

¿Está todo correcto?  
  `[Sí, todo correcto | Quiero corregir algo]`
- *Candidate:* sí  
  <sub>affirm · events: stage_changed, completed, interview_offered</sub>
- **Sofía:** ¡Genial, Óscar! Cumples los requisitos para pasar a la entrevista. Ahora mismo puedes elegir el horario que mejor te venga: te envío las opciones justo después de este mensaje. ¡Gracias por tu tiempo!
- **Sofía:** Elige día y hora para tu entrevista (unos 20 minutos) en Grupo Sazón Centro (Málaga):
1) miércoles 21/10 a las 12:30
2) jueves 22/10 a las 10:00
3) viernes 23/10 a las 10:00  
  `[mié 21/10 · 12:30 | jue 22/10 · 10:00 | vie 23/10 · 10:00 | Ninguno me va bien]`
- *Candidate:* 1  
  <sub>provide_info · option=1 · events: interview_booked</sub>
- **Sofía:** ¡Listo! Tu entrevista es el miércoles 21/10 a las 12:30 en Grupo Sazón Centro (Málaga). Trae tu carnet de conducir. Si no puedes ir, escríbeme y buscamos otro horario.

**Data:** `{"full_name": "Óscar Benítez", "has_drivers_license": true, "license_status": "yes", "license_type": "car", "location_raw": "Málaga, El Palo", "city_id": "malaga", "city": "Málaga", "country": "ES", "zone": "El Palo", "in_service_area": true, "availability": ["full_time"], "preferred_schedule": ["flexible"], "experience_years": 1.0, "experience_months": 12, "experience_platforms": ["Glovo"], "start_date": "2026-10-26", "start_date_raw": "el lunes"}`
**Flags:** human_requested
