"""The contract between the deterministic policy and whoever writes the message.

The policy decides WHAT to say (a Directive); the responder (LLM or templates) decides
only HOW to say it. That boundary is what makes the agent safe and testable.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from pydantic import BaseModel, Field

from screener.domain.models import FieldName

DirectiveKind = Literal[
    "ask",              # ask for a field (optionally acknowledging / answering first)
    "recap",            # deterministic recap follows; the responder only writes an interlude if needed
    "interlude",        # answer a question / notes only, ask nothing (precedes the recap)
    "ask_correction",   # candidate said the recap is wrong without saying what
    "outcome",          # final message of the screening
    "talent_pool_ack",  # answer to the talent-pool opt-in
    "closed_followup",  # message after the screening is over
    "postpone_ack",     # candidate wants to continue later
    "silent",           # say nothing (conversation terminated)
]

Outcome = Literal[
    "qualified",
    "needs_review",
    "no_license",
    "license_in_progress",
    "out_of_area",
    "withdrawn",
    "terminated",
]


class AnswerToQuestion(BaseModel):
    question: str
    answer: str | None = None  # None: not covered by the FAQ, must not be improvised
    faq_id: str | None = None


class Directive(BaseModel):
    kind: DirectiveKind
    locale: str
    candidate_name: str | None = None
    acknowledge: list[str] = Field(default_factory=list)
    answer: AnswerToQuestion | None = None
    notes: list[str] = Field(default_factory=list)  # abuse_warning | human_request | resume
    ask_field: FieldName | None = None
    ask_issue: str | None = None
    ask_options: list[str] = Field(default_factory=list)
    zone_city: str | None = None
    remaining_questions: int = 0
    unchanged: list[str] = Field(default_factory=list)  # restated values at the recap
    tone: Literal["normal", "simplify", "reassuring"] = "normal"
    outcome: Outcome | None = None
    outcome_place: str | None = None
    talent_pool_answer: bool | None = None


@dataclass
class Event:
    type: str
    payload: dict = field(default_factory=dict)


@dataclass
class Decision:
    directive: Directive
    events: list[Event] = field(default_factory=list)
