# ex27_neighbourhood_without_a_zone

**End:** qualified · interview booked · triage: as expected

- **Sofía:** ¡Hola! 👋 Soy Sofía, la asistente virtual (IA) de Grupo Sazón. Te escribo por tu solicitud como repartidor/a: son 7 preguntas rápidas, unos 3 minutos. Tus datos solo se usan para este proceso de selección. ¿Empezamos?  
  `[¡Empezamos! | Tengo una pregunta]`
- *Candidate:* sí  
  <sub>affirm · events: stage_changed</sub>
- **Sofía:** ¡Genial, vamos allá! ¿Cómo te llamas? Nombre y apellido, por favor.
- *Candidate:* Kevin Ramos  
  <sub>provide_info · {"full_name": "Kevin Ramos"} · events: field_valid</sub>
- **Sofía:** Encantada, Kevin. ¿Tienes carnet de conducir en vigor, ya sea de coche o de moto?  
  `[Sí | No]`
- *Candidate:* sí, de moto  
  <sub>provide_info, affirm · {"drivers_license": "yes", "license_type": "motorbike"} · events: field_valid</sub>
- **Sofía:** Perfecto, carnet de moto en vigor, anotado. ¿En qué ciudad y zona te gustaría repartir?
- *Candidate:* Madrid  
  <sub>provide_info · {"location_text": "Madrid", "location_city_id": "madrid", "location_outside_service_area": false} · events: field_valid</sub>
- **Sofía:** Madrid, perfecto. ¿En qué zona o barrio te vendría mejor? Es opcional, pero nos ayuda a asignarte el restaurante más cercano. Puedes pulsar una de las opciones o escribirme tu barrio.  
  `[Centro | Norte | Sur | Este | Cualquier zona]`
- *Candidate:* yo vivo en Moratalaz  
  <sub>provide_info · {"location_text": "Moratalaz", "location_city_id": "madrid", "location_zone": "Moratalaz", "location_outside_service_area": false} · events: zone_not_listed</sub>
- **Sofía:** Moratalaz no es una de nuestras zonas de reparto en Madrid, pero tienes cerca estas tres: Puente de Vallecas, Retiro y Ciudad Lineal. ¿Cuál te vendría mejor? También puedes decirme que te da igual la zona.  
  `[Puente de Vallecas | Retiro | Ciudad Lineal | Cualquier zona]`
- *Candidate:* Retiro  
  <sub>provide_info · {"location_text": "Retiro", "location_city_id": "madrid", "location_zone": "Retiro", "location_outside_service_area": false} · events: field_valid</sub>
- **Sofía:** Retiro, anotado. ¿Qué disponibilidad tienes: jornada completa, media jornada o fines de semana?  
  `[Jornada completa | Media jornada | Fines de semana]`
- *Candidate:* media jornada  
  <sub>provide_info · {"availability": ["part_time"]} · events: field_valid</sub>
- **Sofía:** Media jornada, perfecto. ¿Qué turno prefieres: mañana, tarde, noche o flexible?  
  `[Mañana | Tarde | Noche | Flexible]`
- *Candidate:* noches  
  <sub>provide_info · {"schedule": ["evening"]} · events: field_valid</sub>
- **Sofía:** Noches, anotado. ¿Tienes experiencia como repartidor/a? Si es así, ¿cuánto tiempo y en qué plataformas?
- *Candidate:* nunca  
  <sub>provide_info · {"experience_months": 0} · events: field_valid</sub>
- **Sofía:** No pasa nada, aquí también damos la bienvenida a quien empieza desde cero. ¿Cuándo podrías empezar?
- *Candidate:* en una semana  
  <sub>provide_info · {"start_date": {"kind": "in_weeks", "amount": 1, "weekday": null, "exact_date": null}} · events: field_valid, stage_changed</sub>
- **Sofía:** Antes de terminar, revisa tus datos:
• Nombre: Kevin Ramos
• Carnet de conducir: Sí (moto)
• Zona: Madrid (Retiro)
• Disponibilidad: media jornada
• Turno: noche
• Experiencia: Sin experiencia previa
• Inicio: martes 27/10

¿Está todo correcto?  
  `[Sí, todo correcto | Quiero corregir algo]`
- *Candidate:* sí  
  <sub>affirm · events: stage_changed, completed, interview_offered</sub>
- **Sofía:** Gracias por confirmarlo, Kevin. Cumples los requisitos para pasar a la entrevista, así que ya puedes elegir el horario que mejor te venga: te envío las opciones justo después de este mensaje.
- **Sofía:** Elige día y hora para tu entrevista (unos 20 minutos) en Grupo Sazón Malasaña (Madrid):
1) miércoles 21/10 a las 17:00
2) jueves 22/10 a las 17:00
3) viernes 23/10 a las 17:00  
  `[mié 21/10 · 17:00 | jue 22/10 · 17:00 | vie 23/10 · 17:00 | Ninguno me va bien]`
- *Candidate:* 1  
  <sub>provide_info · option=1 · events: interview_booked</sub>
- **Sofía:** ¡Listo! Tu entrevista es el miércoles 21/10 a las 17:00 en Grupo Sazón Malasaña (Madrid). Trae tu carnet de conducir. Si no puedes ir, escríbeme y buscamos otro horario.

**Data:** `{"full_name": "Kevin Ramos", "has_drivers_license": true, "license_status": "yes", "license_type": "motorbike", "location_raw": "Madrid", "city_id": "madrid", "city": "Madrid", "country": "ES", "zone": "Retiro", "unlisted_zone": "Moratalaz", "in_service_area": true, "availability": ["part_time"], "preferred_schedule": ["evening"], "experience_years": 0.0, "experience_months": 0, "start_date": "2026-10-27", "start_date_raw": "en una semana"}`
