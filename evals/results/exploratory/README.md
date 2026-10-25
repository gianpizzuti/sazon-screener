# Exploratory conversations

Run 2026-10-23 00:30 · 25 scenarios · $0.47. Triage compares the end state with `expect`; each transcript was read by a person.

| Scenario | End | Triage |
|---|---|---|
| [`ex01_small_talk_and_weather`](ex01_small_talk_and_weather.md) | qualified | as expected |
| [`ex02_personal_questions_to_the_bot`](ex02_personal_questions_to_the_bot.md) | qualified | as expected |
| [`ex03_rumour_about_the_company`](ex03_rumour_about_the_company.md) | qualified | as expected |
| [`ex04_moves_city_mid_flow`](ex04_moves_city_mid_flow.md) | qualified | as expected |
| [`ex05_changes_availability_later`](ex05_changes_availability_later.md) | qualified | as expected |
| [`ex06_changes_start_date_at_recap`](ex06_changes_start_date_at_recap.md) | qualified | as expected |
| [`ex07_remembers_a_second_licence`](ex07_remembers_a_second_licence.md) | qualified | as expected |
| [`ex08_questions_everywhere`](ex08_questions_everywhere.md) | qualified | as expected |
| [`ex09_emojis_and_one_word_replies`](ex09_emojis_and_one_word_replies.md) | qualified | as expected |
| [`ex10_long_life_story`](ex10_long_life_story.md) | qualified | as expected |
| [`ex11_typos_and_slang`](ex11_typos_and_slang.md) | qualified | as expected |
| [`ex12_spanglish`](ex12_spanglish.md) | qualified | as expected |
| [`ex13_english_full_flow_with_interview`](ex13_english_full_flow_with_interview.md) | qualified | as expected |
| [`ex14_mexico_full_flow_with_interview`](ex14_mexico_full_flow_with_interview.md) | qualified | as expected |
| [`ex15_withdraws_and_comes_back`](ex15_withdraws_and_comes_back.md) | qualified | as expected |
| [`ex16_wants_a_person_then_continues`](ex16_wants_a_person_then_continues.md) | qualified | as expected |
| [`ex17_insult_then_apology`](ex17_insult_then_apology.md) | qualified | as expected |
| [`ex18_none_fits_then_asks_about_saturdays`](ex18_none_fits_then_asks_about_saturdays.md) | qualified | as expected |
| [`ex19_reschedules_the_interview`](ex19_reschedules_the_interview.md) | qualified | as expected |
| [`ex20_lost_at_the_recap`](ex20_lost_at_the_recap.md) | qualified | as expected |
| [`ex21_answers_the_wrong_question`](ex21_answers_the_wrong_question.md) | qualified | as expected |
| [`ex22_injection_mid_flow`](ex22_injection_mid_flow.md) | qualified | as expected |
| [`ex23_no_experience_asks_if_it_matters`](ex23_no_experience_asks_if_it_matters.md) | qualified | as expected |
| [`ex24_vague_start_date`](ex24_vague_start_date.md) | qualified | as expected |
| [`ex25_leaves_and_comes_back`](ex25_leaves_and_comes_back.md) | qualified | as expected |
| [`ex26_asks_about_the_new_topics`](ex26_asks_about_the_new_topics.md) | qualified | as expected (after D222–D225, see below) |
| [`ex27_neighbourhood_without_a_zone`](ex27_neighbourhood_without_a_zone.md) | qualified | as expected |
| [`ex28_italian_licence_just_moved`](ex28_italian_licence_just_moved.md) | qualified | as expected |
| [`ex29_venezuelan_licence`](ex29_venezuelan_licence.md) | needs_review | as expected |

Added with the 30-topic knowledge base (ADR 0010): ex26, plus the four scenarios full of questions (ex03, ex08, ex18, ex23), were run again on 2026-10-23 with embedding retrieval ($0.13), all as expected.

Re-run on 2026-10-23 after D219–D221 (neighbourhoods without a delivery zone): ex26, ex27 and the Madrid scenarios ex01, ex08, ex09, ex10, ex22 ($0.18). "Madrid, Usera" is now kept and answered with the closest zones; ex27 as expected. ex26 ended at the recap for two reasons unrelated to zones (both **fixed** since, see below):
- The model read "tengo carnet de coche, pero es de Marruecos, ¿vale aquí?" as a licence of unknown validity (the earlier run read it as "yes"). The script never answers the licence question again, so Sofía asked it seven times while the candidate answered other things: a re-ask has no limit when the candidate keeps giving other data.
- Sofía retracted a correct approved answer one turn later ("antes me he pasado de rápida: no tengo ningún dato sobre propinas"): the writer treated a fact from an earlier turn as unapproved.

Fixed on 2026-10-23 (D222–D226): a licence from abroad is a licence and the hiring country's law decides (research in docs/design/foreign-licences.md); a question unanswered after three asks goes to a person; Sofía never takes back an approved answer. Re-run: ex26 twice (both as expected, the Moroccan licence explained and noted for the recruiter, no retraction), ex28 (Italian: valid like a Spanish one) and ex29 (Venezuelan: a person decides), $0.10. The two turns that produced the retraction were also run 10 times: 0 retractions ($0.04).
