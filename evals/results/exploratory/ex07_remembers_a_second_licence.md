# ex07_remembers_a_second_licence

**End:** qualified · interview booked · triage: as expected

- **Sofía:** ¡Hola! 👋 Soy Sofía, la asistente virtual (IA) de Grupo Sazón. Te escribo por tu solicitud como repartidor/a: son 7 preguntas rápidas, unos 3 minutos. Tus datos solo se usan para este proceso de selección. ¿Empezamos?  
  `[¡Empezamos! | Tengo una pregunta]`
- *Candidate:* sí  
  <sub>affirm · events: stage_changed</sub>
- **Sofía:** ¡Genial, vamos allá! ¿Cómo te llamas? Nombre y apellido, por favor.
- *Candidate:* Hugo Navarro  
  <sub>provide_info · {"full_name": "Hugo Navarro"} · events: field_valid</sub>
- **Sofía:** Encantada, Hugo. ¿Tienes carnet de conducir en vigor, ya sea de coche o de moto?  
  `[Sí | No]`
- *Candidate:* sí, de coche  
  <sub>provide_info, affirm · {"drivers_license": "yes", "license_type": "car"} · events: field_valid</sub>
- **Sofía:** Perfecto, con el carnet de coche vamos bien. ¿En qué ciudad y zona te gustaría repartir?
- *Candidate:* Bilbao  
  <sub>provide_info · {"location_text": "Bilbao", "location_city_id": "bilbao", "location_outside_service_area": false} · events: field_valid</sub>
- **Sofía:** Genial, Bilbao entonces. ¿Y en qué zona o barrio? Así vemos cuál es el restaurante más cercano a ti. Puedes tocar una de las opciones de abajo o escribirme tu barrio.  
  `[Abando | Indautxu | Deusto | Cualquier zona]`
- *Candidate:* bueno, en realidad también tengo el de moto  
  <sub>provide_info, correction · {"license_type": "both"} · events: field_valid, field_corrected, field_skipped</sub>
- **Sofía:** Perfecto, entonces tienes carnet de coche y de moto. ¿Qué disponibilidad tienes: jornada completa, media jornada o fines de semana?  
  `[Jornada completa | Media jornada | Fines de semana]`
- *Candidate:* Deusto  
  <sub>provide_info · {"location_text": "Deusto", "location_city_id": "bilbao", "location_zone": "Deusto", "location_outside_service_area": false} · events: field_valid</sub>
- **Sofía:** Perfecto, Deusto. ¿Qué disponibilidad tienes: jornada completa, media jornada o fines de semana?  
  `[Jornada completa | Media jornada | Fines de semana]`
- *Candidate:* jornada completa  
  <sub>provide_info · {"availability": ["full_time"]} · events: field_valid</sub>
- **Sofía:** Genial, jornada completa. ¿Qué turno prefieres: mañana, tarde, noche o flexible?  
  `[Mañana | Tarde | Noche | Flexible]`
- *Candidate:* noches  
  <sub>provide_info · {"schedule": ["evening"]} · events: field_valid</sub>
- **Sofía:** Anotado, turno de noche. ¿Tienes experiencia como repartidor/a? Si es así, cuéntame cuánto tiempo y en qué plataformas.
- *Candidate:* tres años en Uber Eats  
  <sub>provide_info · {"experience_months": 36, "experience_platforms": ["Uber Eats"]} · events: field_valid, field_valid</sub>
- **Sofía:** Tres años en Uber Eats, estupendo. ¿Cuándo podrías empezar?
- *Candidate:* ya  
  <sub>provide_info · {"start_date": {"kind": "immediate", "amount": null, "weekday": null, "exact_date": null}} · events: field_valid, stage_changed</sub>
- **Sofía:** Antes de terminar, revisa tus datos:
• Nombre: Hugo Navarro
• Carnet de conducir: Sí (coche y moto)
• Zona: Bilbao (Deusto)
• Disponibilidad: jornada completa
• Turno: noche
• Experiencia: 3 años (Uber Eats)
• Inicio: lo antes posible (martes 20/10)

¿Está todo correcto?  
  `[Sí, todo correcto | Quiero corregir algo]`
- *Candidate:* sí  
  <sub>affirm · events: stage_changed, completed, interview_offered</sub>
- **Sofía:** ¡Perfecto, Hugo, muchas gracias! Cumples los requisitos para pasar a la entrevista. Ahora mismo puedes elegir el horario que mejor te venga: te envío las opciones justo después de este mensaje.
- **Sofía:** Elige día y hora para tu entrevista (unos 20 minutos) en Grupo Sazón Abando (Bilbao):
1) miércoles 21/10 a las 17:00
2) jueves 22/10 a las 17:00
3) viernes 23/10 a las 17:00  
  `[mié 21/10 · 17:00 | jue 22/10 · 17:00 | vie 23/10 · 17:00 | Ninguno me va bien]`
- *Candidate:* 3  
  <sub>provide_info · option=3 · events: interview_booked</sub>
- **Sofía:** ¡Listo! Tu entrevista es el viernes 23/10 a las 17:00 en Grupo Sazón Abando (Bilbao). Trae tu carnet de conducir. Si no puedes ir, escríbeme y buscamos otro horario.

**Data:** `{"full_name": "Hugo Navarro", "has_drivers_license": true, "license_status": "yes", "license_type": "both", "location_raw": "Bilbao", "city_id": "bilbao", "city": "Bilbao", "country": "ES", "zone": "Deusto", "in_service_area": true, "availability": ["full_time"], "preferred_schedule": ["evening"], "experience_years": 3.0, "experience_months": 36, "experience_platforms": ["Uber Eats"], "start_date": "2026-10-20", "start_date_raw": "ya"}`
