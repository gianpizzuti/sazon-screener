"""Read models for the recruiter side: a pipeline row and a candidate detail page.

Kept separate from the engine: the same views feed the dashboard, the API and,
eventually, an ATS export.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta

from pydantic import BaseModel

from screener.domain.models import ConversationState, Flag, ScreeningData, Stage, utcnow
from screener.storage.repository import ConversationNotFound, Repository, is_override

# A conversation silent for longer than this is "awaiting reply" (follow-ups under way);
# it becomes "abandoned" only when the follow-up scheduler gives up (state.abandoned_at).
AWAITING_AFTER = timedelta(hours=2)

# Recruiter queue order: who should a recruiter look at first?
PRIORITY = {
    "qualified": 0,
    "needs_review": 1,
    "in_progress": 2,
    "awaiting_reply": 3,
    "abandoned": 3,
    "disqualified": 4,
    "withdrawn": 5,
    "terminated": 6,
}


class CandidateRow(BaseModel):
    id: str
    status: str            # qualified | needs_review | in_progress | awaiting_reply | abandoned | disqualified | withdrawn | terminated
    needs_review: bool
    review_status: str     # what the recruiter did: new | contacted | interview | hired | rejected
    overridden: bool       # the recruiter's decision contradicts the bot's outcome
    name: str | None
    city: str | None
    zone: str | None
    country: str | None
    availability: list[str]
    schedule: list[str]
    experience_months: int | None
    platforms: list[str]
    start_date: date | None
    language: str
    channel: str
    disqualification_reason: str | None
    flags: list[str]
    open_questions: int
    headline: str | None
    followups_sent: int
    next_followup_at: datetime | None
    created_at: datetime
    last_activity: datetime
    priority: int


class FieldView(BaseModel):
    field: str
    status: str
    evidence: str | None
    failed_attempts: int


class MessageView(BaseModel):
    role: str
    text: str
    created_at: datetime
    meta: dict


class EventView(BaseModel):
    type: str
    payload: dict
    created_at: datetime


class CandidateDetail(BaseModel):
    row: CandidateRow
    data: ScreeningData
    fields: list[FieldView]
    flags: list[Flag]
    pending_questions: list[str]
    talent_pool_opt_in: bool | None
    summary: dict | None
    review: dict
    transcript: list[MessageView]
    events: list[EventView]


def display_status(state: ConversationState, now: datetime, awaiting_after: timedelta = AWAITING_AFTER) -> str:
    if state.is_terminal:
        return state.stage.value
    if state.abandoned_at is not None:
        return "abandoned"
    last = state.last_candidate_message_at or state.created_at
    return "awaiting_reply" if state.followups_sent or now - last > awaiting_after else "in_progress"


def build_row(state: ConversationState, summary: dict | None, review: dict, now: datetime,
              next_followup_at: datetime | None = None) -> CandidateRow:
    d = state.data
    status = display_status(state, now)
    return CandidateRow(
        id=state.id,
        status=status,
        needs_review=state.needs_review,
        review_status=review.get("status", "new"),
        overridden=is_override(state.stage.value, review.get("status", "new")),
        name=d.full_name,
        city=d.city or d.location_raw,
        zone=d.zone,
        country=d.country,
        availability=[a.value for a in d.availability],
        schedule=[s.value for s in d.preferred_schedule],
        experience_months=d.experience_months,
        platforms=d.experience_platforms,
        start_date=d.start_date,
        language=state.language,
        channel=state.channel,
        disqualification_reason=state.disqualification_reason.value if state.disqualification_reason else None,
        flags=sorted({f.code for f in state.flags}),
        open_questions=len(state.pending_questions),
        headline=(summary or {}).get("headline"),
        followups_sent=state.followups_sent,
        next_followup_at=next_followup_at,
        created_at=state.created_at,
        last_activity=state.last_candidate_message_at or state.created_at,
        priority=PRIORITY.get(status, 9) * 10 + (0 if review.get("status", "new") == "new" else 5),
    )


def build_rows(repo: Repository, now: datetime | None = None, next_followup=lambda state: None) -> list[CandidateRow]:
    now = now or utcnow()
    reviews = repo.reviews()
    rows = []
    for c in repo.conversations():
        state = ConversationState.model_validate(c.state)
        rows.append(build_row(state, c.summary, reviews.get(c.id, {}), now, next_followup(state)))
    # Queue order: status priority, then the soonest available start date, then most recent.
    return sorted(rows, key=lambda r: (r.priority, r.start_date or date.max, -r.last_activity.timestamp()))


def build_detail(repo: Repository, conversation_id: str, now: datetime | None = None,
                 next_followup=lambda state: None) -> CandidateDetail:
    now = now or utcnow()
    state = repo.get_state(conversation_id)  # raises ConversationNotFound
    summary = repo.get_summary(conversation_id)
    review = repo.get_review(conversation_id)
    return CandidateDetail(
        row=build_row(state, summary, review, now, next_followup(state)),
        data=state.data,
        fields=[
            FieldView(field=name.value, status=fs.status.value, evidence=fs.evidence, failed_attempts=fs.failed_attempts)
            for name, fs in state.fields.items()
        ],
        flags=state.flags,
        pending_questions=state.pending_questions,
        talent_pool_opt_in=state.talent_pool_opt_in,
        summary=summary,
        review=review,
        transcript=[MessageView(role=m.role, text=m.text, created_at=m.created_at, meta=m.meta) for m in repo.messages(conversation_id)],
        events=[EventView(type=e.type, payload=e.payload, created_at=e.created_at) for e in repo.events(conversation_id)],
    )


__all__ = ["CandidateRow", "CandidateDetail", "build_rows", "build_detail", "ConversationNotFound", "Stage"]
