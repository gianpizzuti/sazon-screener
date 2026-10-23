# ex26_asks_about_the_new_topics

**End:** confirming · triage: stage: expected qualified, got confirming

- **Sofía:** ¡Hola! 👋 Soy Sofía, la asistente virtual (IA) de Grupo Sazón. Te escribo por tu solicitud como repartidor/a: son 7 preguntas rápidas, unos 3 minutos. Tus datos solo se usan para este proceso de selección. ¿Empezamos?  
  `[¡Empezamos! | Tengo una pregunta]`
- *Candidate:* sí, pero antes una cosa: ¿las propinas son para mí?  
  <sub>affirm, question · faq=tips · events: question_answered, stage_changed</sub>
- **Sofía:** Buena pregunta: sí, las propinas que te dejen los clientes en tus entregas son para ti y van aparte del sueldo. Y para empezar, ¿cómo te llamas? Nombre y apellido, por favor.
- *Candidate:* vale. Soy Samira El Idrissi  
  <sub>provide_info · {"full_name": "Samira El Idrissi"} · events: field_valid</sub>
- **Sofía:** Encantada, Samira. Por cierto, antes me he pasado de rápida: no tengo ningún dato sobre propinas, así que eso te lo confirma el equipo de selección. Siguiente: ¿tienes carnet de conducir en vigor (coche o moto)?  
  `[Sí | No]`
- *Candidate:* tengo carnet de coche, pero es de Marruecos, ¿vale aquí?  
  <sub>provide_info, question · {"license_type": "car"} · faq=foreign_licence · events: question_answered</sub>
- **Sofía:** Depende del país que lo expidió y de tu situación de residencia, así que eso lo revisa contigo el equipo en la entrevista; lleva el carnet. Para seguir, ¿tu carnet de coche está en vigor ahora mismo?  
  `[Sí | No]`
- *Candidate:* ok. Madrid, Usera  
  <sub>provide_info · {"location_text": "Madrid, Usera", "location_city_id": "madrid", "location_zone": "Usera", "location_outside_service_area": false} · events: field_valid, zone_not_listed</sub>
- **Sofía:** Perfecto, Madrid entonces. Vuelvo a lo del carnet, que se me ha quedado en el aire: ¿tienes ahora mismo un carnet de conducir en vigor, de coche o de moto?  
  `[Sí | No]`
- *Candidate:* ¿y hay sitio para dejar el coche en el restaurante?  
  <sub>question · faq=parking · events: question_answered</sub>
- **Sofía:** Eso depende de cada restaurante; el equipo te explica dónde se deja el vehículo durante el turno en el que te toque. Y una cosa más sencilla: ¿tu carnet de conducir está en vigor, sí o no?  
  `[Sí | No]`
- *Candidate:* jornada completa  
  <sub>provide_info · {"availability": ["full_time"]} · events: field_valid</sub>
- **Sofía:** Apuntado, jornada completa. Para poder seguir con tu solicitud necesito saber una cosa: ¿tienes ahora mismo un carnet de conducir en vigor, de coche o de moto?  
  `[Sí | No]`
- *Candidate:* tardes. Oye, ¿la gasolina la pagáis vosotros?  
  <sub>question · {"schedule": ["afternoon"]} · faq=expenses · events: question_answered, field_valid</sub>
- **Sofía:** Anotado, turno de tardes. Si repartes con tu propio vehículo, te compensamos el combustible por kilómetro recorrido en las entregas; el importe exacto te lo confirma el equipo en la entrevista. ¿Tienes carnet de conducir en vigor, de coche o de moto?  
  `[Sí | No]`
- *Candidate:* un año en Glovo  
  <sub>provide_info · {"experience_months": 12, "experience_platforms": ["Glovo"]} · events: field_valid, field_valid</sub>
- **Sofía:** Genial, un año repartiendo con Glovo, eso suma. Y ahora lo más sencillo, solo sí o no: ¿tienes carnet de conducir en vigor, de coche o de moto?  
  `[Sí | No]`
- *Candidate:* ¿se puede llevar música con cascos mientras reparto?  
  <sub>question · events: question_unanswered</sub>
- **Sofía:** Eso del uso de cascos con música no lo sé, te lo confirma el equipo de selección. Y una vez más, de forma sencilla: ¿tienes carnet de conducir en vigor, de coche o de moto?  
  `[Sí | No]`
- *Candidate:* el lunes  
  <sub>other · events: field_unclear</sub>
- **Sofía:** Lo de Usera no lo tenemos entre nuestras zonas de reparto en Madrid, pero hay otras cerca. ¿Cuál te viene mejor: Arganzuela, Carabanchel, Puente de Vallecas o cualquier zona?  
  `[Arganzuela | Carabanchel | Puente de Vallecas | Cualquier zona]`
- *Candidate:* sí, todo bien  
  <sub>affirm · events: field_skipped</sub>
- **Sofía:** Genial, gracias. ¿Cuándo podrías empezar?
- *Candidate:* 1  
  <sub>provide_info · {"start_date": {"kind": "in_days", "amount": 1, "weekday": null, "exact_date": null}} · events: field_valid, stage_changed</sub>
- **Sofía:** Antes de terminar, revisa tus datos:
• Nombre: Samira El Idrissi
• Carnet de conducir: (por confirmar)
• Zona: Madrid (Usera)
• Disponibilidad: jornada completa
• Turno: tarde
• Experiencia: 1 año (Glovo)
• Inicio: mañana, miércoles 21/10

¿Está todo correcto?  
  `[Sí, todo correcto | Quiero corregir algo]`

**Data:** `{"full_name": "Samira El Idrissi", "location_raw": "Madrid, Usera", "city_id": "madrid", "city": "Madrid", "country": "ES", "unlisted_zone": "Usera", "in_service_area": true, "availability": ["full_time"], "preferred_schedule": ["afternoon"], "experience_years": 1.0, "experience_months": 12, "experience_platforms": ["Glovo"], "start_date": "2026-10-21", "start_date_raw": "1"}`
**Flags:** unclear_field
