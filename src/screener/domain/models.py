"""Domain model: what a screening collects and the state of a conversation.

`ScreeningData` is the structured output recruiters (and an ATS) consume.
`ConversationState` is the agent's memory: the source of truth between turns,
so the LLM never has to "remember" anything from the transcript.
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from enum import StrEnum

from pydantic import BaseModel, Field


def utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Availability(StrEnum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    WEEKENDS = "weekends"


class Schedule(StrEnum):
    MORNING = "morning"
    AFTERNOON = "afternoon"
    EVENING = "evening"
    FLEXIBLE = "flexible"


class LicenseStatus(StrEnum):
    YES = "yes"
    NO = "no"
    IN_PROGRESS = "in_progress"


class StartDateKind(StrEnum):
    IMMEDIATE = "immediate"
    IN_DAYS = "in_days"
    IN_WEEKS = "in_weeks"
    IN_MONTHS = "in_months"
    NEXT_WEEKDAY = "next_weekday"
    EXACT_DATE = "exact_date"
    UNCLEAR = "unclear"


class StartDateExpr(BaseModel):
    """How the candidate expressed the start date. The model reads it, code computes the date."""

    kind: StartDateKind
    amount: int | None = None        # for in_days / in_weeks / in_months
    weekday: int | None = None       # for next_weekday, 0 = Monday ... 6 = Sunday
    exact_date: str | None = None    # for exact_date, YYYY-MM-DD


class FieldName(StrEnum):
    FULL_NAME = "full_name"
    DRIVERS_LICENSE = "drivers_license"
    LOCATION = "location"
    ZONE = "zone"
    AVAILABILITY = "availability"
    SCHEDULE = "schedule"
    EXPERIENCE_YEARS = "experience_years"
    EXPERIENCE_PLATFORMS = "experience_platforms"
    START_DATE = "start_date"


# Order in which fields are asked: knock-outs right after the name.
FIELD_ORDER: list[FieldName] = list(FieldName)
KNOCKOUT_FIELDS = {FieldName.DRIVERS_LICENSE, FieldName.LOCATION}
OPTIONAL_FIELDS = {FieldName.ZONE}


class FieldStatus(StrEnum):
    MISSING = "missing"
    VALID = "valid"
    INVALID = "invalid"   # an answer was given but failed validation
    UNCLEAR = "unclear"   # gave up after max attempts: flagged for a recruiter
    SKIPPED = "skipped"   # not applicable (e.g. platforms with 0 years) or optional and declined


class Stage(StrEnum):
    INTRO = "intro"
    SCREENING = "screening"
    CONFIRMING = "confirming"
    QUALIFIED = "qualified"
    NEEDS_REVIEW = "needs_review"
    DISQUALIFIED = "disqualified"
    WITHDRAWN = "withdrawn"
    TERMINATED = "terminated"


TERMINAL_STAGES = {
    Stage.QUALIFIED,
    Stage.NEEDS_REVIEW,
    Stage.DISQUALIFIED,
    Stage.WITHDRAWN,
    Stage.TERMINATED,
}


class DisqualificationReason(StrEnum):
    NO_LICENSE = "no_license"
    LICENSE_IN_PROGRESS = "license_in_progress"
    OUT_OF_AREA = "out_of_area"


class ScreeningData(BaseModel):
    """The structured screening result. Every field is optional until collected."""

    full_name: str | None = None
    has_drivers_license: bool | None = None
    license_status: LicenseStatus | None = None
    location_raw: str | None = None
    city_id: str | None = None
    city: str | None = None
    country: str | None = None
    zone: str | None = None
    in_service_area: bool | None = None
    availability: list[Availability] = Field(default_factory=list)
    preferred_schedule: list[Schedule] = Field(default_factory=list)
    experience_years: float | None = None   # derived from months
    experience_months: int | None = None    # as the candidate said it ("8 meses" -> 8)
    experience_platforms: list[str] = Field(default_factory=list)
    start_date: date | None = None
    start_date_raw: str | None = None


class FieldState(BaseModel):
    status: FieldStatus = FieldStatus.MISSING
    times_asked: int = 0
    failed_attempts: int = 0
    last_error: str | None = None
    hint_options: list[str] = Field(default_factory=list)  # e.g. ambiguous places to choose from
    evidence: str | None = None  # the candidate's own words the value came from


class Flag(BaseModel):
    code: str
    detail: str = ""
    at: datetime = Field(default_factory=utcnow)


class ConversationState(BaseModel):
    id: str
    client_id: str
    channel: str
    stage: Stage = Stage.INTRO
    language: str = "es"
    spanish_variant: str | None = None  # "es-ES" / "es-MX" once known
    current_field: FieldName | None = None
    data: ScreeningData = Field(default_factory=ScreeningData)
    fields: dict[FieldName, FieldState] = Field(
        default_factory=lambda: {name: FieldState() for name in FieldName}
    )
    disqualification_reason: DisqualificationReason | None = None
    talent_pool_opt_in: bool | None = None
    flags: list[Flag] = Field(default_factory=list)
    pending_questions: list[str] = Field(default_factory=list)
    abuse_strikes: int = 0
    recap_rounds: int = 0  # replies to the recap that did not confirm it
    post_close_replies: int = 0  # courtesy replies sent after the screening ended
    followups_sent: int = 0          # follow-ups since the candidate's last message
    last_followup_at: datetime | None = None
    abandoned_at: datetime | None = None  # set after the last follow-up goes unanswered
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)
    last_candidate_message_at: datetime | None = None
    completed_at: datetime | None = None

    @property
    def locale(self) -> str:
        """Reply locale: 'en', or the Spanish variant ('es' while unknown)."""
        if self.language == "en":
            return "en"
        return self.spanish_variant or "es"

    @property
    def is_terminal(self) -> bool:
        return self.stage in TERMINAL_STAGES

    @property
    def needs_review(self) -> bool:
        return self.stage == Stage.NEEDS_REVIEW or any(
            f.status == FieldStatus.UNCLEAR for f in self.fields.values()
        ) or any(flag.code in REVIEW_FLAGS for flag in self.flags)

    def add_flag(self, code: str, detail: str = "") -> None:
        if not any(f.code == code and f.detail == detail for f in self.flags):
            self.flags.append(Flag(code=code, detail=detail))

    def field(self, name: FieldName) -> FieldState:
        return self.fields[name]


# Flags that put a candidate in the recruiter's review queue.
REVIEW_FLAGS = {"human_requested", "late_start", "abuse", "update_after_close", "recap_not_confirmed"}
