# ADR 0003: Client specifics are configuration, the screening schema is code

**Status:** accepted

## Context
A forward-deployed product gets deployed to many clients: a burger chain today, a hotel group hiring cleaners tomorrow. Grupo Sazón alone has 45 restaurants in 9 cities and two countries, and service areas, FAQ answers and wording will change weekly during a pilot.

## Decision
Everything a recruiter or client success manager would want to change lives in `config/clients/<client>/` (YAML, validated by Pydantic on load):
- `service_areas.yaml`: cities, zones, aliases, timezones
- `faq.yaml`: approved answers, with per-country overrides
- `copy.yaml`: greeting, recap, outcomes, fallback wording, per locale (es, es-ES, es-MX, en)
- `client.yaml`: agent persona, thresholds (message length, max attempts, late start), models, next steps

The **field schema** (name, licence, location, availability, schedule, experience, start date) and the policy stay in typed Python.

## Alternatives considered
| Option | Why not |
|---|---|
| Everything hardcoded | Fastest today. Every change to a zone or an FAQ becomes a deploy. |
| Fully dynamic schema (fields defined in YAML, Pydantic models generated at runtime) | A new client would need zero code. But it loses static typing, makes the policy generic and harder to read, and is premature with one client. |

## Trade-offs accepted
A client with different screening fields (say, "has own vehicle") needs a code change in `models.py` + `policy.py`. That is acceptable at one or two clients.

## Revisit when
The third client needs different fields. At that point, extract a field registry (type, validator, knock-out rule, order) and generate the schema from config.
