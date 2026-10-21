"""Schemas the LLM must fill (enforced through structured outputs).

These describe what the model *read*, never what the system *decides*:
there is deliberately no `is_qualified` field anywhere.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from screener.domain.models import Availability, LicenseStatus, Schedule, StartDateExpr

Intent = Literal[
    "provide_info",
    "affirm",
    "deny",
    "question",
    "correction",
    "postpone",
    "opt_out",
    "human_request",
    "smalltalk",
    "abuse",
    "other",
]

EvidenceField = Literal[
    "full_name",
    "drivers_license",
    "location",
    "availability",
    "schedule",
    "experience",
    "start_date",
]


class Evidence(BaseModel):
    field: EvidenceField
    quote: str = Field(description="The candidate's exact words supporting the value, copied verbatim.")


class Extracted(BaseModel):
    full_name: str | None
    drivers_license: LicenseStatus | None
    location_text: str | None
    location_city_id: str | None
    location_zone: str | None
    location_outside_service_area: bool | None
    availability: list[Availability] | None
    schedule: list[Schedule] | None
    experience_months: int | None
    experience_platforms: list[str] | None
    start_date: StartDateExpr | None

    @classmethod
    def empty(cls) -> "Extracted":
        return cls(**{name: None for name in cls.model_fields})


class TurnAnalysis(BaseModel):
    """The understanding of ONE candidate message."""

    language: Literal["es", "en"]
    language_is_clear: bool = Field(
        description="True if the message has ordinary words of its language (a phrase or sentence). "
        "False only if it is just names, numbers, sí/no/ok, a single word, emojis or proper nouns."
    )
    spanish_variant: Literal["es-ES", "es-MX", "unknown"]
    intents: list[Intent]
    sentiment: Literal["neutral", "positive", "confused", "frustrated"]
    question: str | None
    faq_id: str | None
    correction_target: EvidenceField | None
    extracted: Extracted
    evidence: list[Evidence]

    @classmethod
    def blank(cls, **overrides) -> "TurnAnalysis":
        """Convenience constructor (tests, degraded mode)."""
        base = dict(
            language="es",
            language_is_clear=False,
            spanish_variant="unknown",
            intents=[],
            sentiment="neutral",
            question=None,
            faq_id=None,
            correction_target=None,
            extracted=Extracted.empty(),
            evidence=[],
        )
        base.update(overrides)
        return cls(**base)


class CandidateSummary(BaseModel):
    """Post-conversation summary for the recruiter."""

    headline: str = Field(description="One line: name · city/zone · availability · experience · start.")
    summary: str = Field(description="2-3 sentences a recruiter can read in ten seconds.")
    strengths: list[str]
    concerns: list[str]
    candidate_questions: list[str] = Field(description="Questions the candidate asked that a human should follow up on.")
    recommended_action: str
