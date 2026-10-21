"""Conversation analytics, computed from states, messages and the event log.

The questions they answer are the client's: are candidates finishing (the 60% problem),
where do they drop off or get frustrated, why are they knocked out, what do they ask that
we can't answer (FAQ gaps), and is the AI healthy (fallbacks, errors, human overrides).

At pilot scale this runs in Python over the whole table; in production the same metrics
would be SQL views over the events table or a warehouse.
"""

from __future__ import annotations

import statistics
from collections import Counter
from datetime import datetime

from pydantic import BaseModel

from screener.domain.models import FIELD_ORDER, OPTIONAL_FIELDS, ConversationState, FieldName, FieldStatus, utcnow
from screener.storage.repository import Repository
from screener.views import display_status

DONE = {FieldStatus.VALID, FieldStatus.UNCLEAR, FieldStatus.SKIPPED}
FUNNEL_FIELDS = [f for f in FIELD_ORDER if f not in OPTIONAL_FIELDS and f != FieldName.EXPERIENCE_PLATFORMS]
FINISHED = {"qualified", "needs_review", "disqualified", "withdrawn", "terminated"}


class FunnelStep(BaseModel):
    step: str
    count: int


class Analytics(BaseModel):
    totals: dict[str, int]
    completion_rate: float | None      # finished / (everyone not still active)
    qualified_rate: float | None       # qualified / finished
    funnel: list[FunnelStep]
    drop_off: dict[str, int]           # last question asked to abandoned candidates
    knockout_reasons: dict[str, int]
    median_minutes_to_finish: float | None
    median_candidate_messages: float | None
    languages: dict[str, int]
    countries: dict[str, int]
    frustration_by_field: dict[str, int]
    faq_usage: dict[str, int]
    unanswered_questions: list[str]
    template_fallback_rate: float | None
    llm_errors: int
    guard_rejections: int
    human_overrides: int
    followups_sent: int
    candidates_nudged: int             # received at least one follow-up
    candidates_recovered: int          # replied after a follow-up
    recovery_rate: float | None        # recovered / nudged: does re-engagement work?
    recovered_by_followup: dict[str, int]


def compute(repo: Repository, now: datetime | None = None) -> Analytics:
    now = now or utcnow()
    rows = repo.conversations()
    states = [ConversationState.model_validate(r.state) for r in rows]
    statuses = {s.id: display_status(s, now) for s in states}
    events = repo.events()
    messages = repo.all_messages()

    totals = Counter(statuses.values())
    totals["started"] = len(states)
    finished = sum(totals[s] for s in FINISHED)

    candidate_msgs = Counter(m.conversation_id for m in messages if m.role == "candidate")
    funnel = [FunnelStep(step="Started", count=len(states)),
              FunnelStep(step="Replied", count=sum(1 for s in states if candidate_msgs[s.id] > 0))]
    for name in FUNNEL_FIELDS:
        funnel.append(FunnelStep(step=_label(name), count=sum(1 for s in states if s.field(name).status in DONE)))
    funnel.append(FunnelStep(step="Qualified", count=totals["qualified"]))

    drop_off = Counter(
        _label(s.current_field) if s.current_field else "Intro"
        for s in states
        if statuses[s.id] == "abandoned"
    )

    durations = [
        (s.completed_at - s.created_at).total_seconds() / 60
        for s in states
        if s.completed_at and statuses[s.id] in FINISHED
    ]

    agent_sources = [m.meta.get("source") for m in messages if m.role == "agent" and m.meta.get("kind") not in ("greeting", "recap", "followup")]  # templates by design are not fallbacks
    by_type = Counter(e.type for e in events)
    nudged = {e.conversation_id for e in events if e.type == "followup_sent"}
    recovered = [e for e in events if e.type == "resumed" and e.payload.get("after_followups", 0) > 0]
    unanswered = [q for s in sorted(states, key=lambda s: s.updated_at, reverse=True) for q in s.pending_questions]

    return Analytics(
        totals={k: totals[k] for k in ["started", "in_progress", "awaiting_reply", "abandoned", *sorted(FINISHED)]},
        completion_rate=_ratio(finished, finished + totals["abandoned"]),
        qualified_rate=_ratio(totals["qualified"], finished),
        funnel=funnel,
        drop_off=dict(drop_off.most_common()),
        knockout_reasons=dict(Counter(s.disqualification_reason.value for s in states if s.disqualification_reason).most_common()),
        median_minutes_to_finish=round(statistics.median(durations), 1) if durations else None,
        median_candidate_messages=statistics.median([candidate_msgs[s.id] for s in states if statuses[s.id] in FINISHED]) if finished else None,
        languages=dict(Counter(s.language for s in states)),
        countries=dict(Counter(s.data.country or "unknown" for s in states)),
        frustration_by_field=dict(Counter(
            _label(FieldName(e.payload["field"])) if e.payload.get("field") else "Intro"
            for e in events if e.type == "sentiment" and e.payload.get("value") == "frustrated"
        ).most_common()),
        faq_usage=dict(Counter(e.payload.get("faq_id") for e in events if e.type == "question_answered").most_common()),
        unanswered_questions=unanswered[:20],
        template_fallback_rate=_ratio(sum(1 for s in agent_sources if s == "template"), len(agent_sources)),
        llm_errors=by_type["llm_error"],
        guard_rejections=by_type["guard_rejected"],
        human_overrides=by_type["human_override"],
        followups_sent=by_type["followup_sent"],
        candidates_nudged=len(nudged),
        candidates_recovered=len({e.conversation_id for e in recovered}),
        recovery_rate=_ratio(len({e.conversation_id for e in recovered}), len(nudged)),
        recovered_by_followup=dict(sorted(Counter(f"After follow-up {e.payload['after_followups']}" for e in recovered).items())),
    )


LABELS = {
    FieldName.FULL_NAME: "Name",
    FieldName.DRIVERS_LICENSE: "License",
    FieldName.LOCATION: "City / zone",
    FieldName.ZONE: "Zone",
    FieldName.AVAILABILITY: "Availability",
    FieldName.SCHEDULE: "Schedule",
    FieldName.EXPERIENCE_YEARS: "Experience",
    FieldName.EXPERIENCE_PLATFORMS: "Platforms",
    FieldName.START_DATE: "Start date",
}


def _label(field: FieldName) -> str:
    return LABELS[FieldName(field)]


def _ratio(part: int, whole: int) -> float | None:
    return round(part / whole, 3) if whole else None
