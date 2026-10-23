# Knowledge-base retrieval

Run 2026-10-23T14:12 · 127 questions (112 answered by a topic, 15 by none; 8 asked by simulated candidates) · 30 topics. Method and limits: [README](../README.md#knowledge-base-retrieval).

## Retrieval: is the right topic in the shortlist?

| Embedding model | Method | Recall@1 | Recall@3 | Recall@5 | MRR | Observed R@5 | Median ms |
|---|---|---|---|---|---|---|---|
| minilm | keyword | 55% | 67% | 75% | 0.63 | 80% | 0.0 |
| minilm | semantic | 84% | 97% | 98% | 0.91 | 100% | 3.7 |
| minilm | hybrid | 77% | 96% | 97% | 0.86 | 100% | 3.7 |
| mpnet | keyword | 55% | 67% | 75% | 0.63 | 80% | 0.0 |
| mpnet | semantic | 88% | 98% | 99% | 0.93 | 100% | 10.9 |
| mpnet | hybrid | 78% | 96% | 98% | 0.87 | 100% | 11.1 |

Keyword search does not use the embedding model, so its rows are the same for every model.

- **minilm** (`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`): 205 phrasings indexed; model load 0.77 s, index 0.94 s.
  - semantic miss `documents_2` "¿necesito el número de la seguridad social?" → expected `documents` (rank 13), top 3: insurance, payday, accident
  - semantic miss `privacy_2` "¿vais a pasar mi teléfono a otras empresas?" → expected `privacy` (rank 9), top 3: phone_app, delivery_radius, studies_other_job
  - hybrid miss `requirements_1` "¿qué hace falta para entrar?" → expected `requirements` (rank 7), top 3: training, work_permit, vehicle
  - hybrid miss `requirements_3` "what do I need to apply?" → expected `requirements` (rank 7), top 3: documents, training, work_permit
  - hybrid miss `privacy_2` "¿vais a pasar mi teléfono a otras empresas?" → expected `privacy` (rank 10), top 3: vehicle, phone_app, delivery_radius
- **mpnet** (`sentence-transformers/paraphrase-multilingual-mpnet-base-v2`): 205 phrasings indexed; model load 1.58 s, index 3.02 s.
  - semantic miss `documents_2` "¿necesito el número de la seguridad social?" → expected `documents` (rank 8), top 3: insurance, payday, tips
  - hybrid miss `requirements_1` "¿qué hace falta para entrar?" → expected `requirements` (rank 7), top 3: work_permit, training, vehicle
  - hybrid miss `requirements_3` "what do I need to apply?" → expected `requirements` (rank 7), top 3: documents, work_permit, training

## Routing: which topic does the understanding model choose?

2 run(s) per question.

| Topics shown | Right topic | Wrong topic | None (missed) | None when nothing answers | Topic when nothing answers | Written after run 1 | Cost |
|---|---|---|---|---|---|---|---|
| shortlist + answers | 208/224 (93%) | 0 | 16 | 30/30 | 0 | 48/48 (100%) | $0.067 |
| shortlist | 204/224 (91%) | 4 | 16 | 28/30 | 2 | 42/48 (88%) | $0.054 |
| every topic + answers | 211/224 (94%) | 4 | 9 | 30/30 | 0 | 46/48 (96%) | $0.125 |
| every topic | 204/224 (91%) | 4 | 16 | 30/30 | 0 | 42/48 (88%) | $0.076 |

A wrong topic is the error that matters: the writer receives an approved answer to another question (it still checks the fit, D145). A missed topic is safe: "the team will confirm". "Written after run 1": the right outcome (the topic, or none) on the 24 questions written before the change they would judge was run (D213).

- shortlist + answers · `trial_2` "¿el contrato sería indefinido?" → expected `trial_period`, got `None` · shown: trial_period, contract, documents, delivery_radius, work_permit
- shortlist + answers · `trial_2` "¿el contrato sería indefinido?" → expected `trial_period`, got `None` · shown: trial_period, contract, documents, delivery_radius, work_permit
- shortlist + answers · `trial_3` "is the contract permanent?" → expected `trial_period`, got `None` · shown: trial_period, contract, documents, insurance, delivery_radius
- shortlist + answers · `trial_3` "is the contract permanent?" → expected `trial_period`, got `None` · shown: trial_period, contract, documents, insurance, delivery_radius
- shortlist + answers · `zones_2` "¿qué colonias cubren en Guadalajara?" → expected `zones`, got `None` · shown: zones, company, foreign_licence, delivery_radius, language
- shortlist + answers · `zones_2` "¿qué colonias cubren en Guadalajara?" → expected `zones`, got `None` · shown: zones, company, foreign_licence, delivery_radius, language
- shortlist + answers · `radius_2` "¿cuántos kilómetros se hacen en un turno?" → expected `delivery_radius`, got `None` · shown: delivery_radius, expenses, shifts, payday, time_off
- shortlist + answers · `radius_2` "¿cuántos kilómetros se hacen en un turno?" → expected `delivery_radius`, got `None` · shown: delivery_radius, expenses, shifts, payday, time_off
- shortlist + answers · `interviews_1` "¿la entrevista es por teléfono o en persona?" → expected `interviews`, got `None` · shown: interviews, language, phone_app, is_bot, requirements
- shortlist + answers · `interviews_1` "¿la entrevista es por teléfono o en persona?" → expected `interviews`, got `None` · shown: interviews, language, phone_app, is_bot, requirements
- shortlist + answers · `documents_2` "¿necesito el número de la seguridad social?" → expected `documents`, got `None` · shown: insurance, payday, accident, work_permit, requirements
- shortlist + answers · `documents_2` "¿necesito el número de la seguridad social?" → expected `documents`, got `None` · shown: insurance, payday, accident, work_permit, requirements
- shortlist + answers · `language_2` "mi español no es muy bueno, ¿pasa algo?" → expected `language`, got `None` · shown: language, is_bot, tips, contract, training
- shortlist + answers · `language_2` "mi español no es muy bueno, ¿pasa algo?" → expected `language`, got `None` · shown: language, is_bot, tips, contract, training
- shortlist + answers · `privacy_2` "¿vais a pasar mi teléfono a otras empresas?" → expected `privacy`, got `None` · shown: phone_app, delivery_radius, studies_other_job, company, accident
- shortlist + answers · `privacy_2` "¿vais a pasar mi teléfono a otras empresas?" → expected `privacy`, got `None` · shown: phone_app, delivery_radius, studies_other_job, company, accident
- shortlist · `trial_2` "¿el contrato sería indefinido?" → expected `trial_period`, got `contract` · shown: trial_period, contract, documents, delivery_radius, work_permit
- shortlist · `trial_2` "¿el contrato sería indefinido?" → expected `trial_period`, got `contract` · shown: trial_period, contract, documents, delivery_radius, work_permit
- shortlist · `trial_3` "is the contract permanent?" → expected `trial_period`, got `contract` · shown: trial_period, contract, documents, insurance, delivery_radius
- shortlist · `trial_3` "is the contract permanent?" → expected `trial_period`, got `contract` · shown: trial_period, contract, documents, insurance, delivery_radius
- shortlist · `interviews_1` "¿la entrevista es por teléfono o en persona?" → expected `interviews`, got `None` · shown: interviews, language, phone_app, is_bot, requirements
- shortlist · `interviews_1` "¿la entrevista es por teléfono o en persona?" → expected `interviews`, got `None` · shown: interviews, language, phone_app, is_bot, requirements
- shortlist · `time_off_1` "¿libro algún fin de semana?" → expected `time_off`, got `None` · shown: time_off, payday, interviews, process, weather
- shortlist · `time_off_1` "¿libro algún fin de semana?" → expected `time_off`, got `None` · shown: time_off, payday, interviews, process, weather
- shortlist · `accident_2` "¿las multas de tráfico las cubre la empresa?" → expected `accident`, got `None` · shown: foreign_licence, expenses, accident, contract, parking
- shortlist · `accident_2` "¿las multas de tráfico las cubre la empresa?" → expected `accident`, got `None` · shown: foreign_licence, expenses, accident, contract, parking
- shortlist · `documents_2` "¿necesito el número de la seguridad social?" → expected `documents`, got `None` · shown: insurance, payday, accident, work_permit, requirements
- shortlist · `documents_2` "¿necesito el número de la seguridad social?" → expected `documents`, got `None` · shown: insurance, payday, accident, work_permit, requirements
- shortlist · `language_2` "mi español no es muy bueno, ¿pasa algo?" → expected `language`, got `None` · shown: language, is_bot, tips, contract, training
- shortlist · `language_2` "mi español no es muy bueno, ¿pasa algo?" → expected `language`, got `None` · shown: language, is_bot, tips, contract, training
- shortlist · `privacy_2` "¿vais a pasar mi teléfono a otras empresas?" → expected `privacy`, got `None` · shown: phone_app, delivery_radius, studies_other_job, company, accident
- shortlist · `privacy_2` "¿vais a pasar mi teléfono a otras empresas?" → expected `privacy`, got `None` · shown: phone_app, delivery_radius, studies_other_job, company, accident
- shortlist · `r2_equipment` "¿me prestáis una caja para llevar la comida?" → expected `equipment`, got `None` · shown: equipment, staff_meal, contract, tips, delivery_radius
- shortlist · `r2_equipment` "¿me prestáis una caja para llevar la comida?" → expected `equipment`, got `None` · shown: equipment, staff_meal, contract, tips, delivery_radius
- shortlist · `r2_accident` "si me para la policía y me multan, ¿quién la paga?" → expected `accident`, got `None` · shown: accident, pay, expenses, payday, contract
- shortlist · `r2_accident` "si me para la policía y me multan, ¿quién la paga?" → expected `accident`, got `None` · shown: accident, pay, expenses, payday, contract
- shortlist · `r2_none_bonus` "¿dais algún extra por trabajar en Navidad?" → expected `None`, got `pay` · shown: studies_other_job, shifts, time_off, work_permit, pay
- shortlist · `r2_none_bonus` "¿dais algún extra por trabajar en Navidad?" → expected `None`, got `pay` · shown: studies_other_job, shifts, time_off, work_permit, pay
- every topic + answers · `trial_2` "¿el contrato sería indefinido?" → expected `trial_period`, got `contract`
- every topic + answers · `trial_2` "¿el contrato sería indefinido?" → expected `trial_period`, got `contract`
- every topic + answers · `trial_3` "is the contract permanent?" → expected `trial_period`, got `contract`
- every topic + answers · `zones_2` "¿qué colonias cubren en Guadalajara?" → expected `zones`, got `None`
- every topic + answers · `zones_2` "¿qué colonias cubren en Guadalajara?" → expected `zones`, got `None`
- every topic + answers · `vehicle_1` "no tengo coche, ¿me dejáis uno?" → expected `vehicle`, got `None`
- every topic + answers · `time_off_1` "¿libro algún fin de semana?" → expected `time_off`, got `None`
- every topic + answers · `time_off_1` "¿libro algún fin de semana?" → expected `time_off`, got `None`
- every topic + answers · `training_2` "nunca he hecho repartos, ¿es un problema?" → expected `training`, got `requirements`
- every topic + answers · `language_2` "mi español no es muy bueno, ¿pasa algo?" → expected `language`, got `None`
- every topic + answers · `language_2` "mi español no es muy bueno, ¿pasa algo?" → expected `language`, got `None`
- every topic + answers · `r2_equipment` "¿me prestáis una caja para llevar la comida?" → expected `equipment`, got `None`
- every topic + answers · `r2_equipment` "¿me prestáis una caja para llevar la comida?" → expected `equipment`, got `None`
- every topic · `trial_2` "¿el contrato sería indefinido?" → expected `trial_period`, got `contract`
- every topic · `trial_2` "¿el contrato sería indefinido?" → expected `trial_period`, got `contract`
- every topic · `trial_3` "is the contract permanent?" → expected `trial_period`, got `contract`
- every topic · `trial_3` "is the contract permanent?" → expected `trial_period`, got `contract`
- every topic · `zones_2` "¿qué colonias cubren en Guadalajara?" → expected `zones`, got `None`
- every topic · `zones_2` "¿qué colonias cubren en Guadalajara?" → expected `zones`, got `None`
- every topic · `interviews_1` "¿la entrevista es por teléfono o en persona?" → expected `interviews`, got `None`
- every topic · `interviews_1` "¿la entrevista es por teléfono o en persona?" → expected `interviews`, got `None`
- every topic · `vehicle_2` "¿vale con una bici eléctrica?" → expected `vehicle`, got `None`
- every topic · `accident_2` "¿las multas de tráfico las cubre la empresa?" → expected `accident`, got `None`
- every topic · `accident_2` "¿las multas de tráfico las cubre la empresa?" → expected `accident`, got `None`
- every topic · `documents_2` "¿necesito el número de la seguridad social?" → expected `documents`, got `None`
- every topic · `language_2` "mi español no es muy bueno, ¿pasa algo?" → expected `language`, got `None`
- every topic · `language_2` "mi español no es muy bueno, ¿pasa algo?" → expected `language`, got `None`
- every topic · `r2_equipment` "¿me prestáis una caja para llevar la comida?" → expected `equipment`, got `None`
- every topic · `r2_equipment` "¿me prestáis una caja para llevar la comida?" → expected `equipment`, got `None`
- every topic · `r2_accident` "si me para la policía y me multan, ¿quién la paga?" → expected `accident`, got `None`
- every topic · `r2_accident` "si me para la policía y me multan, ¿quién la paga?" → expected `accident`, got `None`
- every topic · `r2_language` "do I have to speak good Spanish for the job?" → expected `language`, got `None`
- every topic · `r2_language` "do I have to speak good Spanish for the job?" → expected `language`, got `None`
