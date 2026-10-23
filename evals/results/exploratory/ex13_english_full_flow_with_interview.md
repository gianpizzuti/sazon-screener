# ex13_english_full_flow_with_interview

**End:** qualified · interview booked · triage: as expected

- **Sofía:** Hi! 👋 I'm Sofía, Grupo Sazón's virtual (AI) assistant. I'm writing about your delivery driver application: 7 quick questions, about 3 minutes. Your data is only used for this hiring process. Shall we start?  
  `[Let's start! | I have a question]`
- *Candidate:* Hi! Sure  
  <sub>smalltalk, affirm · events: stage_changed</sub>
- **Sofía:** Great, let's get started! What's your full name (first name and surname)?
- *Candidate:* My name is Sarah Collins  
  <sub>provide_info · {"full_name": "Sarah Collins"} · events: field_valid</sub>
- **Sofía:** Thanks, Sarah! Next question: do you have a valid driver's license (car or motorbike)?  
  `[Yes | No]`
- *Candidate:* Yes, I have a car licence  
  <sub>provide_info, affirm · {"drivers_license": "yes", "license_type": "car"} · events: field_valid</sub>
- **Sofía:** Perfect, a car licence works. Which city and area would you like to deliver in?
- *Candidate:* Valencia, El Cabanyal  
  <sub>provide_info · {"location_text": "Valencia, El Cabanyal", "location_city_id": "valencia", "location_zone": "El Cabanyal", "location_outside_service_area": false} · events: field_valid, field_valid</sub>
- **Sofía:** Great, Valencia and El Cabanyal noted. What's your availability: full-time, part-time or weekends?  
  `[Full-time | Part-time | Weekends]`
- *Candidate:* part time and weekends  
  <sub>provide_info · {"availability": ["part_time", "weekends"]} · events: field_valid</sub>
- **Sofía:** Part-time and weekends, got it. Which shift do you prefer: morning, afternoon, evening or flexible?  
  `[Morning | Afternoon | Evening | Flexible]`
- *Candidate:* afternoons  
  <sub>provide_info · {"schedule": ["afternoon"]} · events: field_valid</sub>
- **Sofía:** Afternoons, noted. Do you have any delivery experience? If so, for how long and on which platforms?
- *Candidate:* 8 months with Deliveroo in Lisbon  
  <sub>provide_info · {"experience_months": 8, "experience_platforms": ["Deliveroo"]} · events: field_valid, field_valid</sub>
- **Sofía:** 8 months with Deliveroo, that's solid experience. When could you start?
- *Candidate:* in two weeks  
  <sub>provide_info · {"start_date": {"kind": "in_weeks", "amount": 2, "weekday": null, "exact_date": null}} · events: field_valid, stage_changed</sub>
- **Sofía:** Before we finish, please check your details:
• Name: Sarah Collins
• Driver's license: Yes (car)
• Area: Valencia (El Cabanyal)
• Availability: part-time, weekends
• Shift: afternoon
• Experience: 8 months (Deliveroo)
• Start: Tuesday 3 Nov

Is everything correct?  
  `[Yes, all correct | I want to fix something]`
- *Candidate:* yes, all correct  
  <sub>affirm · events: stage_changed, completed, interview_offered</sub>
- **Sofía:** Thanks for confirming, Sarah, that's everything I needed. You meet the requirements to move on to an interview, and you can pick the time that suits you best right now. The options are coming right after this message. 😊
- **Sofía:** Pick a day and time for your interview (about 20 minutes) at Grupo Sazón Ruzafa (Valencia):
1) Wednesday 21 Oct at 16:00
2) Thursday 22 Oct at 16:00
3) Friday 23 Oct at 16:00  
  `[Wed 21 Oct · 16:00 | Thu 22 Oct · 16:00 | Fri 23 Oct · 16:00 | None of these work]`
- *Candidate:* Thursday works for me  
  <sub>provide_info · option=2 · events: interview_booked</sub>
- **Sofía:** Done! Your interview is on Thursday 22 Oct at 16:00 at Grupo Sazón Ruzafa (Valencia). Please bring your driving licence. If you can't make it, message me and we'll find another time.

**Data:** `{"full_name": "Sarah Collins", "has_drivers_license": true, "license_status": "yes", "license_type": "car", "location_raw": "Valencia, El Cabanyal", "city_id": "valencia", "city": "Valencia", "country": "ES", "zone": "El Cabanyal", "in_service_area": true, "availability": ["part_time", "weekends"], "preferred_schedule": ["afternoon"], "experience_years": 0.67, "experience_months": 8, "experience_platforms": ["Deliveroo"], "start_date": "2026-11-03", "start_date_raw": "in two weeks"}`
