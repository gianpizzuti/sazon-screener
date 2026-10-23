# ex14_mexico_full_flow_with_interview

**End:** qualified · interview booked · triage: as expected

- **Sofía:** ¡Hola! 👋 Soy Sofía, la asistente virtual (IA) de Grupo Sazón. Te escribo por tu solicitud como repartidor/a: son 7 preguntas rápidas, unos 3 minutos. Tus datos solo se usan para este proceso de selección. ¿Empezamos?  
  `[¡Empezamos! | Tengo una pregunta]`
- *Candidate:* qué onda, sí le entro  
  <sub>affirm, smalltalk · events: stage_changed</sub>
- **Sofía:** ¡Qué bueno, arrancamos! Para empezar, ¿cómo te llamas? Nombre y apellido, por favor.
- *Candidate:* Fernando Ríos  
  <sub>provide_info · {"full_name": "Fernando Ríos"} · events: field_valid</sub>
- **Sofía:** Mucho gusto, Fernando. Va con la siguiente pregunta: ¿tienes licencia de manejo vigente, ya sea de carro o de moto?  
  `[Sí | No]`
- *Candidate:* simón, licencia de carro  
  <sub>provide_info, affirm · {"drivers_license": "yes", "license_type": "car"} · events: field_valid</sub>
- **Sofía:** Perfecto, licencia de carro vigente anotada. ¿En qué ciudad y zona te gustaría repartir?
- *Candidate:* CDMX, en la Narvarte  
  <sub>provide_info · {"location_text": "CDMX, en la Narvarte", "location_city_id": "cdmx", "location_outside_service_area": false} · events: field_valid, field_valid</sub>
- **Sofía:** Perfecto, repartirías en CDMX, por la zona de Benito Juárez. ¿Qué disponibilidad tienes: tiempo completo, medio tiempo o fines de semana?  
  `[Tiempo completo | Medio tiempo | Fines de semana]`
- *Candidate:* tiempo completo  
  <sub>provide_info · {"availability": ["full_time"]} · events: field_valid</sub>
- **Sofía:** Anotado, tiempo completo. ¿Qué turno prefieres: mañana, tarde, noche o flexible?  
  `[Mañana | Tarde | Noche | Flexible]`
- *Candidate:* en la noche  
  <sub>provide_info · {"schedule": ["evening"]} · events: field_valid</sub>
- **Sofía:** Listo, turno de noche. ¿Tienes experiencia como repartidor/a? Si es así, ¿cuánto tiempo y en qué plataformas?
- *Candidate:* dos años en Rappi  
  <sub>provide_info · {"experience_months": 24, "experience_platforms": ["Rappi"]} · events: field_valid, field_valid</sub>
- **Sofía:** Qué bien, dos años en Rappi es una buena experiencia. ¿Cuándo podrías empezar?
- *Candidate:* ahorita  
  <sub>provide_info · {"start_date": {"kind": "immediate", "amount": null, "weekday": null, "exact_date": null}} · events: field_valid, stage_changed</sub>
- **Sofía:** Antes de terminar, revisa tus datos:
• Nombre: Fernando Ríos
• Licencia de manejo: Sí (auto)
• Zona: Ciudad de México (Benito Juárez)
• Disponibilidad: tiempo completo
• Turno: noche
• Experiencia: 2 años (Rappi)
• Inicio: lo antes posible (martes 20/10)

¿Está todo correcto?  
  `[Sí, todo correcto | Quiero corregir algo]`
- *Candidate:* sí, todo bien  
  <sub>affirm · events: stage_changed, completed, interview_offered</sub>
- **Sofía:** ¡Listo, Fernando, gracias por tus respuestas! Cumples con los requisitos para pasar a entrevista, y ya puedes elegir el horario que mejor te acomode: te mando las opciones justo después de este mensaje.
- **Sofía:** Elige día y hora para tu entrevista (unos 20 minutos) en Grupo Sazón Roma Norte (Ciudad de México):
1) miércoles 21/10 a las 17:00
2) jueves 22/10 a las 17:00
3) viernes 23/10 a las 17:00  
  `[mié 21/10 · 17:00 | jue 22/10 · 17:00 | vie 23/10 · 17:00 | Ninguno me funciona]`
- *Candidate:* la del viernes porfa  
  <sub>provide_info · option=3 · events: interview_booked</sub>
- **Sofía:** ¡Listo! Tu entrevista es el viernes 23/10 a las 17:00 en Grupo Sazón Roma Norte (Ciudad de México). Trae tu licencia de manejo. Si no puedes ir, escríbeme y buscamos otro horario.

**Data:** `{"full_name": "Fernando Ríos", "has_drivers_license": true, "license_status": "yes", "license_type": "car", "location_raw": "CDMX, en la Narvarte", "city_id": "cdmx", "city": "Ciudad de México", "country": "MX", "zone": "Benito Juárez", "in_service_area": true, "availability": ["full_time"], "preferred_schedule": ["evening"], "experience_years": 2.0, "experience_months": 24, "experience_platforms": ["Rappi"], "start_date": "2026-10-20", "start_date_raw": "ahorita"}`
