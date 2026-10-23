# ex10_long_life_story

**End:** qualified · interview booked · triage: as expected

- **Sofía:** ¡Hola! 👋 Soy Sofía, la asistente virtual (IA) de Grupo Sazón. Te escribo por tu solicitud como repartidor/a: son 7 preguntas rápidas, unos 3 minutos. Tus datos solo se usan para este proceso de selección. ¿Empezamos?  
  `[¡Empezamos! | Tengo una pregunta]`
- *Candidate:* sí claro  
  <sub>affirm · events: stage_changed</sub>
- **Sofía:** Genial, vamos allá. ¿Cómo te llamas? Nombre y apellido, por favor.
- *Candidate:* Hola Sofía, te cuento un poco: me llamo Beatriz Molina Ruiz, tengo 27 años y vivo en Madrid, en Lavapiés, desde hace tres años. Tengo el carnet de coche desde los 18 y también el de moto. Antes trabajé dos años de camarera y luego año y medio repartiendo con Glovo, que lo dejé porque me cambiaron las zonas. Ahora busco algo de media jornada, preferiblemente por las tardes, y podría empezar el lunes que viene.  
  <sub>provide_info · {"full_name": "Beatriz Molina Ruiz", "drivers_license": "yes", "license_type": "both", "location_text": "Madrid, en Lavapiés", "location_city_id": "madrid", "location_zone": "Lavapiés", "location_outside_service_area": false, "availability": ["part_time"], "schedule": ["afternoon"], "experience_months": 18, "experience_platforms": ["Glovo"], "start_date": {"kind": "next_weekday", "amount": null, "weekday": 0, "exact_date": null}} · events: field_valid, field_valid, field_valid, field_valid, field_valid, field_valid, field_valid, field_valid, field_valid, stage_changed</sub>
- **Sofía:** Antes de terminar, revisa tus datos:
• Nombre: Beatriz Molina Ruiz
• Carnet de conducir: Sí (coche y moto)
• Zona: Madrid (Centro)
• Disponibilidad: media jornada
• Turno: tarde
• Experiencia: 1,5 años (Glovo)
• Inicio: lunes 26/10

¿Está todo correcto?  
  `[Sí, todo correcto | Quiero corregir algo]`
- *Candidate:* sí, todo correcto  
  <sub>affirm · events: stage_changed, completed, interview_offered</sub>
- **Sofía:** ¡Perfecto, Beatriz! Con lo que me has contado, cumples los requisitos para pasar a la entrevista. Ahora mismo puedes elegir el horario que mejor te venga: te mando las opciones justo después de este mensaje.
- **Sofía:** Elige día y hora para tu entrevista (unos 20 minutos) en Grupo Sazón Malasaña (Madrid):
1) miércoles 21/10 a las 16:00
2) jueves 22/10 a las 16:00
3) viernes 23/10 a las 16:00  
  `[mié 21/10 · 16:00 | jue 22/10 · 16:00 | vie 23/10 · 16:00 | Ninguno me va bien]`
- *Candidate:* 1  
  <sub>provide_info · option=1 · events: interview_booked</sub>
- **Sofía:** ¡Listo! Tu entrevista es el miércoles 21/10 a las 16:00 en Grupo Sazón Malasaña (Madrid). Trae tu carnet de conducir. Si no puedes ir, escríbeme y buscamos otro horario.

**Data:** `{"full_name": "Beatriz Molina Ruiz", "has_drivers_license": true, "license_status": "yes", "license_type": "both", "location_raw": "Madrid, en Lavapiés", "city_id": "madrid", "city": "Madrid", "country": "ES", "zone": "Centro", "in_service_area": true, "availability": ["part_time"], "preferred_schedule": ["afternoon"], "experience_years": 1.5, "experience_months": 18, "experience_platforms": ["Glovo"], "start_date": "2026-10-26", "start_date_raw": "podría empezar el lunes que viene"}`
