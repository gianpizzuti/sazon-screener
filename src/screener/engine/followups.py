"""Re-engagement of silent candidates: the direct answer to "60% don't answer".

Pure decision logic (what to do with a conversation at a given time) kept apart from the
sending, so the rules are unit-tested with any clock:

- follow-ups at +2 h, +24 h, +72 h after the candidate's last message (configurable);
- at most one per run, and spaced as scheduled even if the scheduler was down;
- never during the candidate's night (quiet hours in THEIR timezone: Spain and Mexico
  are 7-8 hours apart);
- after the last one, a grace period, then the conversation is marked abandoned at the
  question where the candidate stopped; any reply resumes it.

Follow-ups are fixed templates: on WhatsApp, a business-initiated message more than 24 h
after the candidate's last message must be a template pre-approved by Meta.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Literal
from zoneinfo import ZoneInfo

from screener.config import Copy, FollowUpSettings
from screener.domain.models import ConversationState, Stage

ORDINALS = ["first", "second", "last"]


@dataclass
class FollowUpAction:
    kind: Literal["followup", "abandon"]
    attempt: int = 0               # 1-based follow-up number
    is_last: bool = False
    template_required: bool = True  # outside WhatsApp's 24 h customer-service window


def waiting_since(state: ConversationState) -> datetime:
    return state.last_candidate_message_at or state.created_at


def due_at(state: ConversationState, settings: FollowUpSettings) -> datetime | None:
    """When the next follow-up becomes due (before quiet-hours adjustment), or None if no more."""
    n = state.followups_sent
    if n >= len(settings.schedule_hours):
        return None
    due = waiting_since(state) + timedelta(hours=settings.schedule_hours[n])
    if n > 0 and state.last_followup_at:
        gap = settings.schedule_hours[n] - settings.schedule_hours[n - 1]
        due = max(due, state.last_followup_at + timedelta(hours=gap))
    return due


def in_quiet_hours(local: datetime, settings: FollowUpSettings) -> bool:
    start, end = settings.quiet_hours_start, settings.quiet_hours_end
    hour = local.hour
    return hour >= start or hour < end if start > end else start <= hour < end


def next_action(state: ConversationState, now: datetime, settings: FollowUpSettings, timezone: str) -> FollowUpAction | None:
    if state.is_terminal or state.abandoned_at is not None:
        return None
    n = state.followups_sent
    if n >= len(settings.schedule_hours):
        if state.last_followup_at and now - state.last_followup_at >= timedelta(hours=settings.abandon_after_hours):
            return FollowUpAction(kind="abandon")
        return None
    due = due_at(state, settings)
    if due is None or now < due:
        return None
    local = now.replace(tzinfo=ZoneInfo("UTC")).astimezone(ZoneInfo(timezone))
    if in_quiet_hours(local, settings):
        return None  # retried on a later run, after the quiet hours
    last_inbound = state.last_candidate_message_at
    window_open = last_inbound is not None and now - last_inbound < timedelta(hours=settings.whatsapp_window_hours)
    return FollowUpAction(
        kind="followup",
        attempt=n + 1,
        is_last=n + 1 == len(settings.schedule_hours),
        template_required=not window_open,
    )


def render(state: ConversationState, action: FollowUpAction, copy: Copy, question: str, remaining: int) -> str:
    """The follow-up text: one template per stage and attempt, with the pending question."""
    variant = "intro" if state.stage == Stage.INTRO else "confirming" if state.stage == Stage.CONFIRMING else "screening"
    ordinal = "last" if action.is_last else ORDINALS[min(action.attempt - 1, 1)]
    first_name = state.data.full_name.split()[0] if state.data.full_name else None
    return copy.text(f"followup.{variant}.{ordinal}", state.locale, name=first_name, remaining=str(remaining), question=question)
