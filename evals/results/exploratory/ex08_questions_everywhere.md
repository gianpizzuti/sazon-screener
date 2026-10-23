# ex08_questions_everywhere

**End:** qualified · interview booked · triage: as expected

- **Sofía:** ¡Hola! 👋 Soy Sofía, la asistente virtual (IA) de Grupo Sazón. Te escribo por tu solicitud como repartidor/a: son 7 preguntas rápidas, unos 3 minutos. Tus datos solo se usan para este proceso de selección. ¿Empezamos?  
  `[¡Empezamos! | Tengo una pregunta]`
- *Candidate:* antes de nada, ¿cuánto se paga?  
  <sub>question · faq=pay · events: question_answered, stage_changed</sub>
- **Sofía:** Claro. Es un contrato laboral directo con Grupo Sazón (no como autónomo), con el salario del convenio de hostelería de tu provincia, más propinas. El importe exacto según tus horas te lo confirma el equipo en la entrevista. ¿Cómo te llamas? Nombre y apellido, por favor.
- *Candidate:* vale. Soy Elena Castro  
  <sub>provide_info · {"full_name": "Elena Castro"} · events: field_valid</sub>
- **Sofía:** Encantada, Elena. ¿Tienes carnet de conducir en vigor, de coche o de moto?  
  `[Sí | No]`
- *Candidate:* sí tengo carnet. ¿Hace falta moto propia?  
  <sub>provide_info, question · {"drivers_license": "yes"} · faq=vehicle · events: question_answered, field_valid</sub>
- **Sofía:** Perfecto, con carnet vamos bien. No hace falta moto propia: puedes repartir con tu moto o coche y te compensamos el combustible por kilómetro, y en algunos restaurantes hay motos de la empresa (el equipo te lo confirma según tu zona). ¿Tu carnet es de coche, de moto o de ambos?  
  `[Coche | Moto | Los dos]`
- *Candidate:* de coche  
  <sub>provide_info · {"license_type": "car"} · events: field_valid, field_refined</sub>
- **Sofía:** Perfecto, carnet de coche anotado. ¿En qué ciudad y zona te gustaría repartir?
- *Candidate:* Madrid  
  <sub>provide_info · {"location_text": "Madrid", "location_city_id": "madrid", "location_outside_service_area": false} · events: field_valid</sub>
- **Sofía:** Genial, en Madrid entonces. ¿Y en qué zona o barrio? Es opcional, pero nos ayuda a asignarte el restaurante más cercano. Puedes pulsar una de las opciones de abajo o escribir tu barrio.  
  `[Centro | Norte | Sur | Este | Cualquier zona]`
- *Candidate:* ¿qué zonas hay?  
  <sub>question · faq=zones · events: question_answered</sub>
- **Sofía:** En Madrid repartimos por el Centro (Chamberí, Salamanca, Retiro, Arganzuela), el Norte (Chamartín, Tetuán, Alcobendas), el Sur (Carabanchel, Getafe, Leganés) y el Este (Puente de Vallecas, Ciudad Lineal). ¿Cuál te viene mejor? Puedes pulsar una opción o escribir tu barrio, o decirme que te da igual.  
  `[Centro | Norte | Sur | Este | Cualquier zona]`
- *Candidate:* Norte  
  <sub>provide_info · {"location_text": "Norte", "location_city_id": "madrid", "location_zone": "Norte", "location_outside_service_area": false} · events: field_valid</sub>
- **Sofía:** Perfecto, zona Norte anotada. ¿Qué disponibilidad tienes: jornada completa, media jornada o fines de semana?  
  `[Jornada completa | Media jornada | Fines de semana]`
- *Candidate:* ¿es contrato o autónomo?  
  <sub>question · faq=contract · events: question_answered</sub>
- **Sofía:** Eres empleado/a de Grupo Sazón, con contrato laboral y alta en la Seguridad Social, así que no necesitas darte de alta como autónomo. ¿Qué disponibilidad tienes: jornada completa, media jornada o fines de semana?  
  `[Jornada completa | Media jornada | Fines de semana]`
- *Candidate:* media jornada  
  <sub>provide_info · {"availability": ["part_time"]} · events: field_valid</sub>
- **Sofía:** Media jornada, perfecto. ¿Qué turno prefieres: mañana, tarde, noche o flexible?  
  `[Mañana | Tarde | Noche | Flexible]`
- *Candidate:* tarde  
  <sub>provide_info · {"schedule": ["afternoon"]} · events: field_valid</sub>
- **Sofía:** Turno de tarde, anotado. ¿Tienes experiencia repartiendo? Si es así, cuéntame cuánto tiempo y en qué plataformas.
- *Candidate:* un año en Glovo  
  <sub>provide_info · {"experience_months": 12, "experience_platforms": ["Glovo"]} · events: field_valid, field_valid</sub>
- **Sofía:** Un año en Glovo, genial, es una buena base. ¿Cuándo podrías empezar?
- *Candidate:* ¿cuándo se cobra, a final de mes?  
  <sub>question · faq=pay · events: question_answered</sub>
- **Sofía:** Esa fecha concreta de cobro no la tengo, así que te la confirma el equipo de selección. Lo que sí sé es que es un contrato laboral con Grupo Sazón, con el salario del convenio de hostelería de tu provincia, más propinas. ¿Cuándo podrías empezar?
- *Candidate:* el lunes que viene  
  <sub>provide_info · {"start_date": {"kind": "next_weekday", "amount": null, "weekday": 0, "exact_date": null}} · events: field_valid, stage_changed</sub>
- **Sofía:** Antes de terminar, revisa tus datos:
• Nombre: Elena Castro
• Carnet de conducir: Sí (coche)
• Zona: Madrid (Norte)
• Disponibilidad: media jornada
• Turno: tarde
• Experiencia: 1 año (Glovo)
• Inicio: lunes 26/10

¿Está todo correcto?  
  `[Sí, todo correcto | Quiero corregir algo]`
- *Candidate:* ¿eres un bot?  
  <sub>question · faq=is_bot · events: question_answered</sub>
- **Sofía:** Sí, soy una asistente virtual con inteligencia artificial. Te hago estas preguntas para agilizar el proceso, y una persona del equipo de selección revisa siempre cada candidatura.
- **Sofía:** Antes de terminar, revisa tus datos:
• Nombre: Elena Castro
• Carnet de conducir: Sí (coche)
• Zona: Madrid (Norte)
• Disponibilidad: media jornada
• Turno: tarde
• Experiencia: 1 año (Glovo)
• Inicio: lunes 26/10

¿Está todo correcto?  
  `[Sí, todo correcto | Quiero corregir algo]`
- *Candidate:* vale, sí, todo correcto  
  <sub>affirm, provide_info · events: stage_changed, completed, interview_offered</sub>
- **Sofía:** Genial, Elena: cumples los requisitos para pasar a la entrevista. Ahora mismo puedes elegir el horario que mejor te venga, te envío las opciones justo después de este mensaje. ¡Gracias por tu tiempo!
- **Sofía:** Elige día y hora para tu entrevista (unos 20 minutos) en Grupo Sazón Malasaña (Madrid):
1) miércoles 21/10 a las 16:00
2) jueves 22/10 a las 16:00
3) viernes 23/10 a las 16:00  
  `[mié 21/10 · 16:00 | jue 22/10 · 16:00 | vie 23/10 · 16:00 | Ninguno me va bien]`
- *Candidate:* 2  
  <sub>provide_info · option=2 · events: interview_booked</sub>
- **Sofía:** ¡Listo! Tu entrevista es el jueves 22/10 a las 16:00 en Grupo Sazón Malasaña (Madrid). Trae tu carnet de conducir. Si no puedes ir, escríbeme y buscamos otro horario.

**Data:** `{"full_name": "Elena Castro", "has_drivers_license": true, "license_status": "yes", "license_type": "car", "location_raw": "Madrid", "city_id": "madrid", "city": "Madrid", "country": "ES", "zone": "Norte", "in_service_area": true, "availability": ["part_time"], "preferred_schedule": ["afternoon"], "experience_years": 1.0, "experience_months": 12, "experience_platforms": ["Glovo"], "start_date": "2026-10-26", "start_date_raw": "el lunes que viene"}`
