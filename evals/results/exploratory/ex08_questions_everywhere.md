# ex08_questions_everywhere

**End:** qualified · interview booked · triage: as expected

- **Sofía:** ¡Hola! 👋 Soy Sofía, la asistente virtual (IA) de Grupo Sazón. Te escribo por tu solicitud como repartidor/a: son 7 preguntas rápidas, unos 3 minutos. Tus datos solo se usan para este proceso de selección. ¿Empezamos?  
  `[¡Empezamos! | Tengo una pregunta]`
- *Candidate:* antes de nada, ¿cuánto se paga?  
  <sub>question · faq=pay · events: question_answered, stage_changed</sub>
- **Sofía:** Claro: es un contrato laboral con Grupo Sazón, no como autónomo, con el salario del convenio de hostelería de tu provincia más propinas. El importe exacto según horas te lo confirma el equipo en la entrevista. ¿Cómo te llamas? Nombre y apellido, por favor.
- *Candidate:* vale. Soy Elena Castro  
  <sub>provide_info · {"full_name": "Elena Castro"} · events: field_valid</sub>
- **Sofía:** Encantada, Elena. ¿Tienes carnet de conducir en vigor, ya sea de coche o de moto?  
  `[Sí | No]`
- *Candidate:* sí tengo carnet. ¿Hace falta moto propia?  
  <sub>provide_info, question · {"drivers_license": "yes"} · faq=vehicle · events: question_answered, field_valid</sub>
- **Sofía:** Perfecto, con carnet ya vamos bien. No hace falta que tengas moto propia: puedes repartir con tu moto o coche, y en algunos restaurantes hay motos de la empresa; el equipo te lo confirma según tu zona. Eso sí, tiene que ser vehículo a motor, no bici ni patinete. ¿Tu carnet es de coche, de moto o de ambos?  
  `[Coche | Moto | Los dos]`
- *Candidate:* de coche  
  <sub>provide_info · {"license_type": "car"} · events: field_valid, field_refined</sub>
- **Sofía:** Perfecto, carnet de coche anotado. ¿En qué ciudad y zona te gustaría repartir?
- *Candidate:* Madrid  
  <sub>provide_info · {"location_text": "Madrid", "location_city_id": "madrid", "location_outside_service_area": false} · events: field_valid</sub>
- **Sofía:** Genial, Madrid entonces. ¿Y en qué zona o barrio? Así podemos buscarte el restaurante más cercano. Puedes tocar una de las opciones de abajo o escribirme tu barrio.  
  `[Centro | Norte | Sur | Este | Cualquier zona]`
- *Candidate:* ¿qué zonas hay?  
  <sub>question · faq=zones · events: question_answered</sub>
- **Sofía:** Repartimos por todo Madrid: centro, norte, sur y este, con barrios como Chamberí, Salamanca, Chamartín, Carabanchel o Ciudad Lineal, y también Alcobendas, Getafe y Leganés. ¿En qué zona o barrio te viene mejor? Puedes tocar una opción o escribirme tu barrio, y si te da igual, dime "cualquier zona".  
  `[Centro | Norte | Sur | Este | Cualquier zona]`
- *Candidate:* Norte  
  <sub>provide_info · {"location_text": "Norte", "location_city_id": "madrid", "location_zone": "Norte"} · events: field_valid</sub>
- **Sofía:** Perfecto, zona norte. ¿Qué disponibilidad tienes: jornada completa, media jornada o fines de semana?  
  `[Jornada completa | Media jornada | Fines de semana]`
- *Candidate:* ¿es contrato o autónomo?  
  <sub>question · faq=contract · events: question_answered</sub>
- **Sofía:** Eres empleado/a de Grupo Sazón, con contrato laboral y alta en la Seguridad Social. No necesitas darte de alta como autónomo. ¿Qué disponibilidad tienes: jornada completa, media jornada o fines de semana?  
  `[Jornada completa | Media jornada | Fines de semana]`
- *Candidate:* media jornada  
  <sub>provide_info · {"availability": ["part_time"]} · events: field_valid</sub>
- **Sofía:** Perfecto, media jornada anotada. ¿Qué turno prefieres: mañana, tarde, noche o flexible?  
  `[Mañana | Tarde | Noche | Flexible]`
- *Candidate:* tarde  
  <sub>provide_info · {"schedule": ["afternoon"]} · events: field_valid</sub>
- **Sofía:** Perfecto, turno de tarde. ¿Tienes experiencia repartiendo? Si es así, cuéntame cuánto tiempo y en qué plataformas.
- *Candidate:* un año en Glovo  
  <sub>provide_info · {"experience_months": 12, "experience_platforms": ["Glovo"]} · events: field_valid, field_valid</sub>
- **Sofía:** Genial, un año repartiendo con Glovo es una buena base. ¿Cuándo podrías empezar?
- *Candidate:* ¿cuándo se cobra, a final de mes?  
  <sub>question · faq=payday · events: question_answered</sub>
- **Sofía:** Se cobra por nómina mensual, mediante transferencia a tu cuenta. El día exacto de ingreso te lo confirma el equipo de selección. ¿Cuándo podrías empezar?
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
  <sub>affirm · events: stage_changed, completed, interview_offered</sub>
- **Sofía:** Genial, Elena: cumples los requisitos para pasar a la entrevista. Ahora mismo puedes elegir el horario que mejor te venga entre las opciones que te envío justo después de este mensaje. ¡Gracias por tu tiempo y mucha suerte!
- **Sofía:** Elige día y hora para tu entrevista (unos 20 minutos) en Grupo Sazón Malasaña (Madrid):
1) miércoles 21/10 a las 16:00
2) jueves 22/10 a las 16:00
3) viernes 23/10 a las 16:00  
  `[mié 21/10 · 16:00 | jue 22/10 · 16:00 | vie 23/10 · 16:00 | Ninguno me va bien]`
- *Candidate:* 2  
  <sub>provide_info · option=2 · events: interview_booked</sub>
- **Sofía:** ¡Listo! Tu entrevista es el jueves 22/10 a las 16:00 en Grupo Sazón Malasaña (Madrid). Trae tu carnet de conducir. Si no puedes ir, escríbeme y buscamos otro horario.

**Data:** `{"full_name": "Elena Castro", "has_drivers_license": true, "license_status": "yes", "license_type": "car", "location_raw": "Madrid", "city_id": "madrid", "city": "Madrid", "country": "ES", "zone": "Norte", "in_service_area": true, "availability": ["part_time"], "preferred_schedule": ["afternoon"], "experience_years": 1.0, "experience_months": 12, "experience_platforms": ["Glovo"], "start_date": "2026-10-26", "start_date_raw": "el lunes que viene"}`
