# ex26_asks_about_the_new_topics

**End:** qualified · interview booked · triage: as expected

- **Sofía:** ¡Hola! 👋 Soy Sofía, la asistente virtual (IA) de Grupo Sazón. Te escribo por tu solicitud como repartidor/a: son 7 preguntas rápidas, unos 3 minutos. Tus datos solo se usan para este proceso de selección. ¿Empezamos?  
  `[¡Empezamos! | Tengo una pregunta]`
- *Candidate:* sí, pero antes una cosa: ¿las propinas son para mí?  
  <sub>affirm, question · faq=tips · events: question_answered, stage_changed</sub>
- **Sofía:** Buena pregunta: sí, las propinas que te dejen los clientes en tus entregas son para ti y van aparte del sueldo. Para empezar, ¿cómo te llamas? Nombre y apellido, por favor.
- *Candidate:* vale. Soy Samira El Idrissi  
  <sub>provide_info · {"full_name": "Samira El Idrissi"} · events: field_valid</sub>
- **Sofía:** Encantada, Samira. Pasamos a lo siguiente: ¿tienes carnet de conducir en vigor, de coche o de moto?  
  `[Sí | No]`
- *Candidate:* tengo carnet de coche, pero es de Marruecos, ¿vale aquí?  
  <sub>provide_info, question · {"drivers_license": "yes", "license_type": "car", "license_country": "Marruecos"} · faq=foreign_licence · events: question_answered, field_valid</sub>
- **Sofía:** Perfecto, con carnet de coche en vigor vamos bien. Un carnet de Marruecos vale en España durante los 6 primeros meses desde que resides aquí; después hay que canjearlo por el español en la DGT, sin examen para coche o moto. El equipo lo revisa contigo en la entrevista. ¿En qué ciudad y zona te gustaría repartir?
- *Candidate:* ok. Madrid, Usera  
  <sub>provide_info · {"location_text": "Madrid, Usera", "location_city_id": "madrid", "location_outside_service_area": false} · events: field_valid, zone_not_listed</sub>
- **Sofía:** Perfecto, Madrid entonces. Usera no es una de nuestras zonas de reparto, pero tenemos Arganzuela, Carabanchel y Puente de Vallecas. Puedes elegir una de ellas o decirme "cualquier zona". ¿Cuál te viene mejor?  
  `[Arganzuela | Carabanchel | Puente de Vallecas | Cualquier zona]`
- *Candidate:* ¿y hay sitio para dejar el coche en el restaurante?  
  <sub>question · faq=parking · events: question_answered</sub>
- **Sofía:** Depende del restaurante: el equipo te explica dónde se deja el vehículo durante el turno en el que te toque. Usera no es una de nuestras zonas de reparto en Madrid, así que dime cuál te encaja mejor: Arganzuela, Carabanchel, Puente de Vallecas o cualquier zona.  
  `[Arganzuela | Carabanchel | Puente de Vallecas | Cualquier zona]`
- *Candidate:* jornada completa  
  <sub>provide_info · {"availability": ["full_time"]} · events: field_valid, field_skipped</sub>
- **Sofía:** Perfecto, jornada completa. ¿Qué turno prefieres: mañana, tarde, noche o flexible?  
  `[Mañana | Tarde | Noche | Flexible]`
- *Candidate:* tardes. Oye, ¿la gasolina la pagáis vosotros?  
  <sub>provide_info, question · {"schedule": ["afternoon"]} · faq=expenses · events: question_answered, field_valid</sub>
- **Sofía:** Perfecto, turno de tardes. Si repartes con tu vehículo, te compensamos el combustible por kilómetro recorrido en las entregas; el importe exacto te lo confirma el equipo en la entrevista. ¿Tienes experiencia como repartidor/a? Si es así, ¿cuánto tiempo y en qué plataformas?
- *Candidate:* un año en Glovo  
  <sub>provide_info · {"experience_months": 12, "experience_platforms": ["Glovo"]} · events: field_valid, field_valid</sub>
- **Sofía:** Genial, un año en Glovo es una buena experiencia. ¿Cuándo podrías empezar?
- *Candidate:* ¿se puede llevar música con cascos mientras reparto?  
  <sub>question · events: question_unanswered</sub>
- **Sofía:** Sobre la música con cascos no tengo ese dato, así que te lo confirma el equipo de selección. Y dime, ¿cuándo podrías empezar?
- *Candidate:* el lunes  
  <sub>provide_info · {"start_date": {"kind": "next_weekday", "amount": null, "weekday": 0, "exact_date": null}} · events: field_valid, stage_changed</sub>
- **Sofía:** Antes de terminar, revisa tus datos:
• Nombre: Samira El Idrissi
• Carnet de conducir: Sí (coche, Marruecos)
• Zona: Madrid (Usera)
• Disponibilidad: jornada completa
• Turno: tarde
• Experiencia: 1 año (Glovo)
• Inicio: lunes 26/10

¿Está todo correcto?  
  `[Sí, todo correcto | Quiero corregir algo]`
- *Candidate:* sí, todo bien  
  <sub>affirm · {"drivers_license": "yes"} · events: field_valid, stage_changed, completed, interview_offered</sub>
- **Sofía:** ¡Genial, Samira! Con lo que me has contado cumples los requisitos para pasar a la entrevista. Ahora mismo puedes elegir el horario que mejor te venga: te envío las opciones justo después de este mensaje.
- **Sofía:** Elige día y hora para tu entrevista (unos 20 minutos) en Grupo Sazón Malasaña (Madrid):
1) miércoles 21/10 a las 16:00
2) jueves 22/10 a las 16:00
3) viernes 23/10 a las 16:00  
  `[mié 21/10 · 16:00 | jue 22/10 · 16:00 | vie 23/10 · 16:00 | Ninguno me va bien]`
- *Candidate:* 1  
  <sub>provide_info · option=1 · events: interview_booked</sub>
- **Sofía:** ¡Listo! Tu entrevista es el miércoles 21/10 a las 16:00 en Grupo Sazón Malasaña (Madrid). Trae tu carnet de conducir. Si no puedes ir, escríbeme y buscamos otro horario.

**Data:** `{"full_name": "Samira El Idrissi", "has_drivers_license": true, "license_status": "yes", "license_type": "car", "license_country": "MA", "location_raw": "Madrid, Usera", "city_id": "madrid", "city": "Madrid", "country": "ES", "unlisted_zone": "Usera", "in_service_area": true, "availability": ["full_time"], "preferred_schedule": ["afternoon"], "experience_years": 1.0, "experience_months": 12, "experience_platforms": ["Glovo"], "start_date": "2026-10-26", "start_date_raw": "el lunes"}`
**Flags:** licence_exchange
