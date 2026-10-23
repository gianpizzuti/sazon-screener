# ex09_emojis_and_one_word_replies

**End:** qualified · interview booked · triage: as expected

- **Sofía:** ¡Hola! 👋 Soy Sofía, la asistente virtual (IA) de Grupo Sazón. Te escribo por tu solicitud como repartidor/a: son 7 preguntas rápidas, unos 3 minutos. Tus datos solo se usan para este proceso de selección. ¿Empezamos?  
  `[¡Empezamos! | Tengo una pregunta]`
- *Candidate:* 👍  
  <sub>affirm · events: stage_changed</sub>
- **Sofía:** Perfecto, gracias por animarte. Para empezar, ¿cómo te llamas? Nombre y apellido, por favor.
- *Candidate:* Nacho Ruiz  
  <sub>provide_info · {"full_name": "Nacho Ruiz"} · events: field_valid</sub>
- **Sofía:** Encantada, Nacho. Vamos con la primera pregunta de las 7: ¿tienes carnet de conducir en vigor, ya sea de coche o de moto?  
  `[Sí | No]`
- *Candidate:* si  
  <sub>affirm, provide_info · {"drivers_license": "yes"} · events: field_valid</sub>
- **Sofía:** Genial, entonces tienes el carnet en vigor. ¿Es de coche, de moto o de ambos?  
  `[Coche | Moto | Los dos]`
- *Candidate:* ?  
  <sub>question · events: question_unanswered, sentiment</sub>
- **Sofía:** Perdona si no me expliqué bien. Sobre esa duda, el equipo de selección te lo confirmará más adelante. Sigamos con otra cosa: ¿en qué ciudad y zona te gustaría repartir? Por ejemplo: Madrid, zona centro.
- *Candidate:* coche  
  <sub>other</sub>
- **Sofía:** Vale, coche anotado. Lo que me falta es la ciudad: ¿en cuál te gustaría repartir y en qué zona?
- *Candidate:* madrid  
  <sub>provide_info · {"location_text": "madrid", "location_city_id": "madrid", "location_outside_service_area": false} · events: field_valid</sub>
- **Sofía:** Perfecto, Madrid. ¿Y en qué zona o barrio? Así podemos ver cuál es el restaurante más cercano a ti. Puedes pulsar una de las opciones o escribirme tu barrio, como prefieras.  
  `[Centro | Norte | Sur | Este | Cualquier zona]`
- *Candidate:* Cualquier zona  
  <sub>other · events: field_skipped</sub>
- **Sofía:** Genial, cualquier zona de Madrid nos sirve. ¿Qué disponibilidad tienes: jornada completa, media jornada o fines de semana?  
  `[Jornada completa | Media jornada | Fines de semana]`
- *Candidate:* ok  
  <sub>other</sub>
- **Sofía:** Perdona, creo que no quedó claro. ¿Cuánto tiempo podrías trabajar: jornada completa, media jornada, solo fines de semana, o una mezcla?  
  `[Jornada completa | Media jornada | Fines de semana]`
- *Candidate:* media  
  <sub>provide_info · {"availability": ["part_time"]} · events: field_valid</sub>
- **Sofía:** Perfecto, media jornada. ¿Y qué turno prefieres: mañana, tarde, noche o flexible?  
  `[Mañana | Tarde | Noche | Flexible]`
- *Candidate:* noche  
  <sub>provide_info · {"schedule": ["evening"]} · events: field_valid</sub>
- **Sofía:** Anotado, turno de noche. ¿Tienes experiencia como repartidor/a? Si es así, cuéntame cuánto tiempo y en qué plataformas.
- *Candidate:* no  
  <sub>deny · {"experience_months": 0} · events: field_valid</sub>
- **Sofía:** Sin problema, no hace falta experiencia previa para empezar. ¿Cuándo podrías incorporarte?
- *Candidate:* ya  
  <sub>provide_info · {"start_date": {"kind": "immediate", "amount": null, "weekday": null, "exact_date": null}} · events: field_valid, stage_changed</sub>
- **Sofía:** Antes de terminar, revisa tus datos:
• Nombre: Nacho Ruiz
• Carnet de conducir: Sí
• Zona: Madrid
• Disponibilidad: media jornada
• Turno: noche
• Experiencia: Sin experiencia previa
• Inicio: lo antes posible (martes 20/10)

¿Está todo correcto?  
  `[Sí, todo correcto | Quiero corregir algo]`
- *Candidate:* 👌  
  <sub>affirm · events: stage_changed, completed, interview_offered</sub>
- **Sofía:** Gracias por confirmar, Nacho, y por tu tiempo. Cumples los requisitos para pasar a la entrevista, y puedes elegir el horario que mejor te venga ahora mismo: te envío las opciones justo después de este mensaje. 😊
- **Sofía:** Elige día y hora para tu entrevista (unos 20 minutos) en Grupo Sazón Malasaña (Madrid):
1) miércoles 21/10 a las 17:00
2) jueves 22/10 a las 17:00
3) viernes 23/10 a las 17:00  
  `[mié 21/10 · 17:00 | jue 22/10 · 17:00 | vie 23/10 · 17:00 | Ninguno me va bien]`
- *Candidate:* 1  
  <sub>provide_info · option=1 · events: interview_booked</sub>
- **Sofía:** ¡Listo! Tu entrevista es el miércoles 21/10 a las 17:00 en Grupo Sazón Malasaña (Madrid). Trae tu carnet de conducir. Si no puedes ir, escríbeme y buscamos otro horario.

**Data:** `{"full_name": "Nacho Ruiz", "has_drivers_license": true, "license_status": "yes", "location_raw": "madrid", "city_id": "madrid", "city": "Madrid", "country": "ES", "in_service_area": true, "availability": ["part_time"], "preferred_schedule": ["evening"], "experience_years": 0.0, "experience_months": 0, "start_date": "2026-10-20", "start_date_raw": "ya"}`
