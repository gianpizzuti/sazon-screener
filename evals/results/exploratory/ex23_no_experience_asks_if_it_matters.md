# ex23_no_experience_asks_if_it_matters

**End:** qualified · interview booked · triage: as expected

- **Sofía:** ¡Hola! 👋 Soy Sofía, la asistente virtual (IA) de Grupo Sazón. Te escribo por tu solicitud como repartidor/a: son 7 preguntas rápidas, unos 3 minutos. Tus datos solo se usan para este proceso de selección. ¿Empezamos?  
  `[¡Empezamos! | Tengo una pregunta]`
- *Candidate:* sí  
  <sub>affirm · events: stage_changed</sub>
- **Sofía:** ¡Genial, empezamos! ¿Cómo te llamas? Nombre y apellido, por favor.
- *Candidate:* Irene Lozano  
  <sub>provide_info · {"full_name": "Irene Lozano"} · events: field_valid</sub>
- **Sofía:** Encantada, Irene. Pasamos a lo siguiente: ¿tienes carnet de conducir en vigor (coche o moto)?  
  `[Sí | No]`
- *Candidate:* sí, de moto  
  <sub>provide_info, affirm · {"drivers_license": "yes", "license_type": "motorbike"} · events: field_valid</sub>
- **Sofía:** Perfecto, carnet de moto en vigor. ¿En qué ciudad y zona te gustaría repartir?
- *Candidate:* Málaga, Centro  
  <sub>provide_info · {"location_text": "Málaga, Centro", "location_city_id": "malaga", "location_zone": "Centro", "location_outside_service_area": false} · events: field_valid, field_valid</sub>
- **Sofía:** Genial, Málaga Centro. ¿Qué disponibilidad tienes: jornada completa, media jornada o fines de semana?  
  `[Jornada completa | Media jornada | Fines de semana]`
- *Candidate:* fines de semana  
  <sub>provide_info · {"availability": ["weekends"]} · events: field_valid</sub>
- **Sofía:** Fines de semana, anotado. ¿Qué turno prefieres: mañana, tarde, noche o flexible?  
  `[Mañana | Tarde | Noche | Flexible]`
- *Candidate:* tarde  
  <sub>provide_info · {"schedule": ["afternoon"]} · events: field_valid</sub>
- **Sofía:** Perfecto, turno de tarde. ¿Tienes experiencia repartiendo? Si es así, cuéntame cuánto tiempo y en qué plataformas.
- *Candidate:* nunca he repartido, ¿pasa algo? ¿hace falta experiencia?  
  <sub>provide_info, question · {"experience_months": 0} · faq=requirements · events: question_answered, sentiment, field_valid</sub>
- **Sofía:** No pasa nada, no hace falta experiencia previa. Los requisitos son ser mayor de edad, tener permiso para trabajar en España, carnet de conducir en vigor y repartir en una de nuestras zonas. ¿Cuándo podrías empezar? Por ejemplo: esta semana, el mes que viene o una fecha concreta.
- *Candidate:* en una semana  
  <sub>provide_info · {"start_date": {"kind": "in_weeks", "amount": 1, "weekday": null, "exact_date": null}} · events: field_valid, stage_changed</sub>
- **Sofía:** Antes de terminar, revisa tus datos:
• Nombre: Irene Lozano
• Carnet de conducir: Sí (moto)
• Zona: Málaga (Centro)
• Disponibilidad: fines de semana
• Turno: tarde
• Experiencia: Sin experiencia previa
• Inicio: martes 27/10

¿Está todo correcto?  
  `[Sí, todo correcto | Quiero corregir algo]`
- *Candidate:* sí  
  <sub>affirm · events: stage_changed, completed, interview_offered</sub>
- **Sofía:** ¡Genial, Irene! Con lo que me has contado, cumples los requisitos para pasar a la entrevista. Ahora mismo te envío las opciones para que elijas el horario que mejor te venga. 😊
- **Sofía:** Elige día y hora para tu entrevista (unos 20 minutos) en Grupo Sazón Centro (Málaga):
1) miércoles 21/10 a las 16:00
2) jueves 22/10 a las 16:00
3) viernes 23/10 a las 16:00  
  `[mié 21/10 · 16:00 | jue 22/10 · 16:00 | vie 23/10 · 16:00 | Ninguno me va bien]`
- *Candidate:* 1  
  <sub>provide_info · option=1 · events: interview_booked</sub>
- **Sofía:** ¡Listo! Tu entrevista es el miércoles 21/10 a las 16:00 en Grupo Sazón Centro (Málaga). Trae tu carnet de conducir. Si no puedes ir, escríbeme y buscamos otro horario.

**Data:** `{"full_name": "Irene Lozano", "has_drivers_license": true, "license_status": "yes", "license_type": "motorbike", "location_raw": "Málaga, Centro", "city_id": "malaga", "city": "Málaga", "country": "ES", "zone": "Centro", "in_service_area": true, "availability": ["weekends"], "preferred_schedule": ["afternoon"], "experience_years": 0.0, "experience_months": 0, "start_date": "2026-10-27", "start_date_raw": "en una semana"}`
