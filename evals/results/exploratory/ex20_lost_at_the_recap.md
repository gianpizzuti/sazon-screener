# ex20_lost_at_the_recap

**End:** qualified · interview booked · triage: as expected

- **Sofía:** ¡Hola! 👋 Soy Sofía, la asistente virtual (IA) de Grupo Sazón. Te escribo por tu solicitud como repartidor/a: son 7 preguntas rápidas, unos 3 minutos. Tus datos solo se usan para este proceso de selección. ¿Empezamos?  
  `[¡Empezamos! | Tengo una pregunta]`
- *Candidate:* sí  
  <sub>affirm · events: stage_changed</sub>
- **Sofía:** ¡Genial, empezamos! ¿Cómo te llamas? Nombre y apellido, por favor.
- *Candidate:* Rosa Jiménez  
  <sub>provide_info · {"full_name": "Rosa Jiménez"} · events: field_valid</sub>
- **Sofía:** Encantada, Rosa. ¿Tienes carnet de conducir en vigor (coche o moto)?  
  `[Sí | No]`
- *Candidate:* sí, de coche  
  <sub>affirm, provide_info · {"drivers_license": "yes", "license_type": "car"} · events: field_valid</sub>
- **Sofía:** Perfecto, con el carnet de coche vamos bien. ¿En qué ciudad y zona te gustaría repartir?
- *Candidate:* Bilbao, Abando  
  <sub>provide_info · {"location_text": "Bilbao, Abando", "location_city_id": "bilbao", "location_zone": "Abando", "location_outside_service_area": false} · events: field_valid, field_valid</sub>
- **Sofía:** Genial, Bilbao y la zona de Abando. ¿Qué disponibilidad tienes: jornada completa, media jornada o fines de semana?  
  `[Jornada completa | Media jornada | Fines de semana]`
- *Candidate:* media jornada  
  <sub>provide_info · {"availability": ["part_time"]} · events: field_valid</sub>
- **Sofía:** Perfecto, media jornada. ¿Qué turno prefieres: mañana, tarde, noche o flexible?  
  `[Mañana | Tarde | Noche | Flexible]`
- *Candidate:* mañanas  
  <sub>provide_info · {"schedule": ["morning"]} · events: field_valid</sub>
- **Sofía:** Anotado, turno de mañanas. ¿Tienes experiencia repartiendo? Si es así, cuéntame cuánto tiempo y en qué plataformas.
- *Candidate:* nunca  
  <sub>provide_info · {"experience_months": 0} · events: field_valid</sub>
- **Sofía:** No pasa nada, aquí también damos la bienvenida a quien empieza desde cero. ¿Cuándo podrías empezar?
- *Candidate:* dentro de una semana  
  <sub>provide_info · {"start_date": {"kind": "in_weeks", "amount": 1, "weekday": null, "exact_date": null}} · events: field_valid, stage_changed</sub>
- **Sofía:** Antes de terminar, revisa tus datos:
• Nombre: Rosa Jiménez
• Carnet de conducir: Sí (coche)
• Zona: Bilbao (Abando)
• Disponibilidad: media jornada
• Turno: mañana
• Experiencia: Sin experiencia previa
• Inicio: martes 27/10

¿Está todo correcto?  
  `[Sí, todo correcto | Quiero corregir algo]`
- *Candidate:* no entiendo qué tengo que hacer ahora  
  <sub>question · faq=process · events: question_answered, sentiment</sub>
- **Sofía:** Solo tienes que revisar los datos del resumen y decirme "sí" si están bien, o qué quieres cambiar. Después, si cumples los requisitos, podrás elegir aquí mismo día y hora para una entrevista breve (unos 20 minutos) en uno de nuestros restaurantes. Una persona revisa siempre cada candidatura.
- **Sofía:** Antes de terminar, revisa tus datos:
• Nombre: Rosa Jiménez
• Carnet de conducir: Sí (coche)
• Zona: Bilbao (Abando)
• Disponibilidad: media jornada
• Turno: mañana
• Experiencia: Sin experiencia previa
• Inicio: martes 27/10

¿Está todo correcto?  
  `[Sí, todo correcto | Quiero corregir algo]`
- *Candidate:* ah vale, sí, está todo bien  
  <sub>affirm · events: stage_changed, completed, interview_offered</sub>
- **Sofía:** ¡Perfecto, Rosa, muchas gracias! Cumples los requisitos para pasar a la entrevista, así que ya puedes elegir el día y la hora que mejor te vengan: te envío las opciones justo después de este mensaje.
- **Sofía:** Elige día y hora para tu entrevista (unos 20 minutos) en Grupo Sazón Abando (Bilbao):
1) miércoles 21/10 a las 12:30
2) jueves 22/10 a las 10:00
3) viernes 23/10 a las 10:00  
  `[mié 21/10 · 12:30 | jue 22/10 · 10:00 | vie 23/10 · 10:00 | Ninguno me va bien]`
- *Candidate:* 1  
  <sub>provide_info · option=1 · events: interview_booked</sub>
- **Sofía:** ¡Listo! Tu entrevista es el miércoles 21/10 a las 12:30 en Grupo Sazón Abando (Bilbao). Trae tu carnet de conducir. Si no puedes ir, escríbeme y buscamos otro horario.

**Data:** `{"full_name": "Rosa Jiménez", "has_drivers_license": true, "license_status": "yes", "license_type": "car", "location_raw": "Bilbao, Abando", "city_id": "bilbao", "city": "Bilbao", "country": "ES", "zone": "Abando", "in_service_area": true, "availability": ["part_time"], "preferred_schedule": ["morning"], "experience_years": 0.0, "experience_months": 0, "start_date": "2026-10-27", "start_date_raw": "dentro de una semana"}`
