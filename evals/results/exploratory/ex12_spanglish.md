# ex12_spanglish

**End:** qualified · interview booked · triage: as expected

- **Sofía:** ¡Hola! 👋 Soy Sofía, la asistente virtual (IA) de Grupo Sazón. Te escribo por tu solicitud como repartidor/a: son 7 preguntas rápidas, unos 3 minutos. Tus datos solo se usan para este proceso de selección. ¿Empezamos?  
  `[¡Empezamos! | Tengo una pregunta]`
- *Candidate:* yes, vamos  
  <sub>affirm · events: stage_changed</sub>
- **Sofía:** ¡Genial, empezamos! ¿Cómo te llamas? Nombre y apellido, por favor.
- *Candidate:* Kevin Ortega  
  <sub>provide_info · {"full_name": "Kevin Ortega"} · events: field_valid</sub>
- **Sofía:** Encantada, Kevin. ¿Tienes carnet de conducir en vigor, ya sea de coche o de moto?  
  `[Sí | No]`
- *Candidate:* yes tengo license de car  
  <sub>provide_info, affirm · {"drivers_license": "yes", "license_type": "car"} · events: field_valid</sub>
- **Sofía:** Perfecto, con el carnet de coche vamos bien. ¿En qué ciudad y zona te gustaría repartir?
- *Candidate:* Barcelona, Eixample  
  <sub>provide_info · {"location_text": "Barcelona, Eixample", "location_city_id": "barcelona", "location_zone": "Eixample", "location_outside_service_area": false} · events: field_valid, field_valid</sub>
- **Sofía:** Genial, Barcelona y la zona del Eixample, anotado. ¿Qué disponibilidad tienes: jornada completa, media jornada o fines de semana?  
  `[Jornada completa | Media jornada | Fines de semana]`
- *Candidate:* full time please  
  <sub>provide_info · {"availability": ["full_time"]} · events: language_switched, field_valid</sub>
- **Sofía:** Great, full-time noted. Which shift do you prefer: morning, afternoon, evening or flexible?  
  `[Morning | Afternoon | Evening | Flexible]`
- *Candidate:* mornings mejor  
  <sub>provide_info · {"schedule": ["morning"]} · events: field_valid</sub>
- **Sofía:** Morning shift, noted. Do you have any delivery experience? If so, for how long and on which platforms?
- *Candidate:* two years with Glovo  
  <sub>provide_info · {"experience_months": 24, "experience_platforms": ["Glovo"]} · events: field_valid, field_valid</sub>
- **Sofía:** Nice, two years with Glovo is solid experience. When could you start?
- *Candidate:* next monday  
  <sub>provide_info · {"start_date": {"kind": "next_weekday", "amount": null, "weekday": 0, "exact_date": null}} · events: field_valid, stage_changed</sub>
- **Sofía:** Before we finish, please check your details:
• Name: Kevin Ortega
• Driver's license: Yes (car)
• Area: Barcelona (Eixample)
• Availability: full-time
• Shift: morning
• Experience: 2 years (Glovo)
• Start: Monday 26 Oct

Is everything correct?  
  `[Yes, all correct | I want to fix something]`
- *Candidate:* sí, all good  
  <sub>affirm · events: stage_changed, completed, interview_offered</sub>
- **Sofía:** Thanks for confirming, Kevin! You meet the requirements to move on to an interview, and you can pick your time right now: the options are coming in the next message.
- **Sofía:** Pick a day and time for your interview (about 20 minutes) at Grupo Sazón Gràcia (Barcelona):
1) Wednesday 21 Oct at 12:30
2) Thursday 22 Oct at 10:00
3) Friday 23 Oct at 10:00  
  `[Wed 21 Oct · 12:30 | Thu 22 Oct · 10:00 | Fri 23 Oct · 10:00 | None of these work]`
- *Candidate:* 1  
  <sub>provide_info · option=1 · events: interview_booked</sub>
- **Sofía:** Done! Your interview is on Wednesday 21 Oct at 12:30 at Grupo Sazón Gràcia (Barcelona). Please bring your driving licence. If you can't make it, message me and we'll find another time.

**Data:** `{"full_name": "Kevin Ortega", "has_drivers_license": true, "license_status": "yes", "license_type": "car", "location_raw": "Barcelona, Eixample", "city_id": "barcelona", "city": "Barcelona", "country": "ES", "zone": "Eixample", "in_service_area": true, "availability": ["full_time"], "preferred_schedule": ["morning"], "experience_years": 2.0, "experience_months": 24, "experience_platforms": ["Glovo"], "start_date": "2026-10-26", "start_date_raw": "next monday"}`
