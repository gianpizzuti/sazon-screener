# ex29_venezuelan_licence

**End:** needs_review · triage: as expected

- **Sofía:** ¡Hola! 👋 Soy Sofía, la asistente virtual (IA) de Grupo Sazón. Te escribo por tu solicitud como repartidor/a: son 7 preguntas rápidas, unos 3 minutos. Tus datos solo se usan para este proceso de selección. ¿Empezamos?  
  `[¡Empezamos! | Tengo una pregunta]`
- *Candidate:* sí  
  <sub>affirm · events: stage_changed</sub>
- **Sofía:** ¡Genial, empezamos! ¿Cómo te llamas? Nombre y apellido, por favor.
- *Candidate:* Andrés Pérez  
  <sub>provide_info · {"full_name": "Andrés Pérez"} · events: field_valid</sub>
- **Sofía:** Encantada, Andrés. ¿Tienes carnet de conducir en vigor, ya sea de coche o de moto?  
  `[Sí | No]`
- *Candidate:* tengo licencia venezolana de carro, ¿vale en España?  
  <sub>provide_info, question · {"drivers_license": "yes", "license_type": "car", "license_country": "Venezuela"} · faq=foreign_licence · events: question_answered, field_valid</sub>
- **Sofía:** Perfecto, con licencia de carro vamos bien. Sobre tu pregunta: un carnet de Venezuela vale en España solo durante los 6 primeros meses desde que resides aquí, y después hace falta sacarse el carnet español. Una persona del equipo lo revisará contigo. ¿En qué ciudad y zona te gustaría repartir?
- *Candidate:* Madrid, Tetuán  
  <sub>provide_info · {"location_text": "Madrid, Tetuán", "location_city_id": "madrid", "location_zone": "Tetuán", "location_outside_service_area": false} · events: field_valid, field_valid</sub>
- **Sofía:** Perfecto, Madrid y la zona de Tetuán. ¿Qué disponibilidad tienes: jornada completa, media jornada o fines de semana?  
  `[Jornada completa | Media jornada | Fines de semana]`
- *Candidate:* jornada completa  
  <sub>provide_info · {"availability": ["full_time"]} · events: field_valid</sub>
- **Sofía:** Perfecto, jornada completa. ¿Qué turno prefieres: mañana, tarde, noche o flexible?  
  `[Mañana | Tarde | Noche | Flexible]`
- *Candidate:* mañanas  
  <sub>provide_info · {"schedule": ["morning"]} · events: field_valid</sub>
- **Sofía:** Perfecto, turno de mañanas. ¿Tienes experiencia como repartidor/a? Si es así, ¿cuánto tiempo y en qué plataformas?
- *Candidate:* dos años en Rappi en Caracas  
  <sub>provide_info · {"experience_months": 24, "experience_platforms": ["Rappi"]} · events: field_valid, field_valid</sub>
- **Sofía:** Dos años en Rappi, genial, es una experiencia que se valora. ¿Cuándo podrías empezar?
- *Candidate:* ya  
  <sub>provide_info · {"start_date": {"kind": "immediate", "amount": null, "weekday": null, "exact_date": null}} · events: field_valid, stage_changed</sub>
- **Sofía:** Antes de terminar, revisa tus datos:
• Nombre: Andrés Pérez
• Carnet de conducir: Sí (coche, Venezuela)
• Zona: Madrid (Tetuán)
• Disponibilidad: jornada completa
• Turno: mañana
• Experiencia: 2 años (Rappi)
• Inicio: lo antes posible (martes 20/10)

¿Está todo correcto?  
  `[Sí, todo correcto | Quiero corregir algo]`
- *Candidate:* sí  
  <sub>affirm · events: foreign_licence_review, stage_changed, completed</sub>
- **Sofía:** Gracias, Andrés, por tu tiempo y tus respuestas. Una persona del equipo de selección revisará tu solicitud y se pondrá en contacto contigo pronto. ¡Que tengas un buen día! 😊

**Data:** `{"full_name": "Andrés Pérez", "has_drivers_license": true, "license_status": "yes", "license_type": "car", "license_country": "VE", "location_raw": "Madrid, Tetuán", "city_id": "madrid", "city": "Madrid", "country": "ES", "zone": "Tetuán", "in_service_area": true, "availability": ["full_time"], "preferred_schedule": ["morning"], "experience_years": 2.0, "experience_months": 24, "experience_platforms": ["Rappi"], "start_date": "2026-10-20", "start_date_raw": "ya"}`
**Flags:** foreign_licence_check
