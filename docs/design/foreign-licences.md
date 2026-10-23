# Driving licences issued abroad

Research note behind [`foreign_licences.yaml`](../../config/clients/grupo_sazon/foreign_licences.yaml) (D222–D223), written on 2026-10-23. It is not legal advice: the client's legal or HR team should confirm it before the pilot, and someone should own it, because the lists change.

## Why it matters
Many delivery-driver applicants in Spain moved there recently. Testing found two failures:
- An Italian or Moroccan licence was read as "no answer", so Sofía asked the licence question again and again.
- When a candidate asked "¿vale aquí?", the answer was "it depends", even though the law gives a clear answer for most countries.

## Spain

| Licence issued in | Can they drive in Spain? | What the agent does |
|---|---|---|
| **EU or EEA** (Italy, France, Romania, Portugal…; Iceland, Liechtenstein, Norway) | Yes, while it is in force, like a Spanish one. If it was issued without an expiry date, it is renewed in Spain after two years of residence | Nothing: qualified as usual |
| **A country with an exchange agreement** (33 on the DGT list, updated 26/06/2026: Morocco, Algeria, Tunisia, Colombia, Peru, Ecuador, Bolivia, Argentina, Chile, Paraguay, Uruguay, Brazil, Dominican Republic, Honduras, El Salvador, Guatemala, Nicaragua, Costa Rica, Panama, United Kingdom, Switzerland, Andorra, Monaco, Ukraine, Moldova, Serbia, North Macedonia, Georgia, Turkey, Japan, South Korea, Philippines, New Zealand) | Yes, for the first **6 months** after becoming resident. Then it is exchanged for a Spanish licence at the DGT, with **no test for car or motorbike**, provided it was obtained before becoming resident | Qualified, with a note for the recruiter: "exchange it within 6 months of residence" (check at the interview) |
| **Any other country** (Venezuela, Mexico, United States, China, India, Senegal…) | Only for the first **6 months** after becoming resident. After that a Spanish licence is needed, with the exams. The exchange without an agreement is reserved for professional drivers | **A person decides** (*needs review*): the candidate may already be past the 6 months |

Other conditions, not checked in the chat:
- The licence must be in Spanish or come with an official translation (or an international permit).
- The holder must meet the Spanish minimum age for that licence.

## Mexico
- There is no national exchange: each state issues licences.
- A resident is normally expected to hold one from their state: CDMX requires an online theory exam (SEMOVI); Jalisco and Nuevo León require theory and practical tests.
- No official source was found that settles which foreign licences a resident may use to work.
- So in Mexico every foreign licence goes to a person.

## Design choices
- **Sofía never asks where the licence is from.** It is too close to nationality (bias, GDPR). The country is used only when the candidate says it. The summary writer is already told never to mention or infer nationality.
- **A licence from abroad is a licence.** The understanding model reports "yes" and the country as written. Whether it is valid here is the rules' call.
- **The rule comes from where they would work**: the city's country, or before the city, the application's country from the ATS (D189).
- **Unknown country, or one not in the lists: a person decides.** It is the safe default.
- **When asked "¿vale aquí?"**, the answer is built from the configuration with the country they named, like the zones (D198) and interview times (D207).

## Sources
- DGT, [Permisos válidos para conducir en España](https://www.dgt.es/nuestros-servicios/permisos-de-conducir/permisos-extranjeros-y-de-fuerzas-y-cuerpos-de-seguridad/permisos-validos-para-conducir-en-espana/)
- DGT, [Países con los que existe tratado o convenio de canjes](https://www.dgt.es/nuestros-servicios/permisos-de-conducir/permisos-extranjeros-y-de-fuerzas-y-cuerpos-de-seguridad/canjes-de-permisos/paises-con-convenio-de-canjes/) (updated 26/06/2026)
- DGT sede, [Renovación de permisos de la UE y EEE](https://sede.dgt.gob.es/en/permisos-de-conducir/canjes-de-permisos/canjes-de-permisos-extranjeros/canjes-inscripcion-renovacion-y-sustitucion-de-permisos-de-la-ue-y-eee/renovacion-de-permisos-de-la-ue-y-eee/) and [Países sin convenio](https://sede.dgt.gob.es/en/permisos-de-conducir/canjes-de-permisos/canjes-de-permisos-extranjeros/canjes-de-paises-sin-convenio/)
- Reglamento General de Conductores, arts. 21–22 (text via [Papelea](https://papelea.com/es/leyes/reglamento-general-de-conductores/titulo-i_capitulo-ii_seccion-2-de-los-permisos-expedidos-en-terceros-paises))
- Mexico, secondary guides only: [Expat Focus](https://www.expatfocus.com/mexico/guide/mexico-driving-licenses), [Translayte](https://translayte.com/de/blog/how-to-convert-a-foreign-driving-license-in-mexico). To confirm with each state's mobility authority.
