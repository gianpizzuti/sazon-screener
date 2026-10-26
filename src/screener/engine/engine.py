"""The screening engine: one candidate message in, the agent's replies out.

    message -> UNDERSTAND (LLM, structured)
            -> DECIDE     (policy, pure Python)
            -> SPEAK      (LLM, guarded; templates as fallback)
            -> PERSIST    (state + transcript + events, atomically)

Channels (CLI, web, WhatsApp, voice) only call `start()` and `handle()`.
"""

from __future__ import annotations

import logging
import threading
import uuid
from collections import defaultdict
from datetime import date, datetime
from zoneinfo import ZoneInfo

from pydantic import BaseModel, Field

from screener.config import ClientConfig
from screener.domain.models import TERMINAL_STAGES as TERMINAL
from screener.domain.models import Application, ConversationState, FieldName, InterviewState, InterviewStatus, ScreeningData, Stage, utcnow
from screener.engine import followups
from screener.engine.directive import Directive, Event
from screener.engine.policy import ScreeningPolicy
from screener.engine.recap import render_recap
from screener.engine.scheduling import candidate_slots, slot_label, slot_long
from screener.knowledge import KnowledgeIndex
from screener.llm.interfaces import (
    ChatMessage,
    LLMError,
    Responder,
    SpeakRequest,
    Summarizer,
    UnderstandRequest,
    Understander,
)
from screener.llm.schemas import TurnAnalysis
from screener.llm.templates import TemplateResponder
from screener.storage.repository import Repository, SlotTaken

log = logging.getLogger(__name__)

MAX_INBOUND_CHARS = 1000
COUNTRY_TIMEZONES = {"ES": "Europe/Madrid", "MX": "America/Mexico_City"}
QUICK_REPLIES_BY_FIELD = {
    FieldName.DRIVERS_LICENSE: "drivers_license",
    FieldName.AVAILABILITY: "availability",
    FieldName.SCHEDULE: "schedule",
}


class OutboundMessage(BaseModel):
    text: str
    quick_replies: list[str] = Field(default_factory=list)


class TurnResult(BaseModel):
    conversation_id: str
    stage: Stage
    messages: list[OutboundMessage]
    completed: bool
    data: ScreeningData
    analysis: TurnAnalysis | None = None  # exposed for debugging / the dashboard
    event_types: list[str] = Field(default_factory=list)
    locale: str = "es"  # how Sofía is speaking now (es-ES, es-MX, es, en): a voice client picks its language from it
    faq_topics: list[str] = Field(default_factory=list)  # the knowledge-base shortlist the model chose from (ADR 0007)


class ScreeningEngine:
    def __init__(
        self,
        config: ClientConfig,
        repository: Repository,
        understander: Understander,
        responder: Responder,
        summarizer: Summarizer | None = None,
        clock=utcnow,
        knowledge: KnowledgeIndex | None = None,
    ):
        self.cfg = config
        self.repo = repository
        self.understander = understander
        self.responder = responder
        self.summarizer = summarizer
        self.knowledge = knowledge or KnowledgeIndex(config.faq)  # without embeddings: every topic
        self.templates = TemplateResponder(config)
        self.policy = ScreeningPolicy(config)
        self.clock = clock
        self._locks: defaultdict[str, threading.Lock] = defaultdict(threading.Lock)
        self._locks_guard = threading.Lock()

    # ------------------------------------------------------------------ public API
    def start(self, channel: str = "web", language: str | None = None, country: str | None = None,
              job: str | None = None, area_id: str | None = None) -> TurnResult:
        """Open a conversation. The first message is a fixed template (as WhatsApp requires
        for business-initiated messages) disclosing that the agent is an AI.

        The application (from the ATS: the job ad and its restaurant) tells the country before the
        candidate says a word. It only sets the timezone, so reminders never go out at night in
        Mexico; the wording is the same for everyone until the candidate names a city (D192)."""
        area = self.cfg.area(area_id)
        country = (country or (area.country if area else "") or "").upper() or None
        state = ConversationState(
            id=str(uuid.uuid4()),
            client_id=self.cfg.id,
            channel=channel,
            language=language or self.cfg.agent.default_language,
            application=Application(job=job, area_id=area.id if area else None, country=country),
            created_at=self.clock(),
        )
        greeting = OutboundMessage(
            text=self.cfg.copy_.text("greeting", state.locale),
            quick_replies=self.cfg.copy_.options("intro", state.locale),
        )
        self.repo.save_turn(
            state,
            [("agent", greeting.text, {"kind": "greeting", "source": "template"})],
            [Event("conversation_started", {"channel": channel})],
        )
        return TurnResult(conversation_id=state.id, locale=state.locale, stage=state.stage, messages=[greeting], completed=False, data=state.data)

    def handle(self, conversation_id: str, text: str) -> TurnResult:
        with self._lock_for(conversation_id):  # one turn at a time per conversation
            return self._handle(conversation_id, text)

    def summarize(self, conversation_id: str) -> dict | None:
        """Recruiter summary. Off the hot path: channels call it after the conversation ends."""
        if not self.summarizer:
            return None
        state = self.repo.get_state(conversation_id)
        try:
            summary = self.summarizer.summarize(state, self.repo.transcript(conversation_id)).model_dump()
            summary["source"] = "llm"
        except LLMError as exc:
            log.warning("summary failed for %s: %s", conversation_id, exc)
            summary = self._fallback_summary(state)
        self.repo.save_summary(conversation_id, summary)
        return summary

    def run_followups(self) -> list[dict]:
        """Send due follow-ups and mark abandoned conversations. Called periodically.

        Pilot: a loop inside the API. Production: one scheduled job (or delayed tasks), with
        a uniqueness constraint on (conversation, attempt) so several workers can't double-send.
        """
        now, settings, done = self.clock(), self.cfg.followups, []
        for row in self.repo.conversations():
            if row.stage in {s.value for s in TERMINAL}:
                continue
            with self._lock_for(row.id):
                state = self.repo.get_state(row.id)  # re-read under the lock
                timezone = self._timezone(state)
                action = followups.next_action(state, now, settings, timezone)
                if action is None:
                    continue
                if action.kind == "abandon":
                    state.abandoned_at = now
                    self.repo.save_turn(state, [], [Event("abandoned", {"field": state.current_field, "followups": state.followups_sent})])
                    done.append({"conversation_id": state.id, "action": "abandoned"})
                    continue
                text = followups.render(state, action, self.cfg.copy_, self._pending_question(state),
                                        self.policy.remaining_questions(state))
                state.followups_sent, state.last_followup_at = action.attempt, now
                meta = {"kind": "followup", "source": "template", "attempt": action.attempt,
                        "whatsapp_template_required": action.template_required}
                event = Event("followup_sent", {"attempt": action.attempt, "field": state.current_field,
                                                "stage": state.stage, "template_required": action.template_required})
                self.repo.save_turn(state, [("agent", text, meta)], [event])
                done.append({"conversation_id": state.id, "action": "followup", "attempt": action.attempt, "text": text})
        return done

    def next_followup_at(self, state: ConversationState):
        return None if state.is_terminal or state.abandoned_at else followups.due_at(state, self.cfg.followups)

    def _pending_question(self, state: ConversationState) -> str:
        copy, loc = self.cfg.copy_, state.locale
        if state.stage == Stage.INTRO or state.current_field is None:
            return ""
        return copy.text(f"ask.{state.current_field.value}", loc, city=state.data.city or "")

    def _timezone(self, state: ConversationState) -> str:
        """The candidate's timezone: their city, else the restaurant they applied to, else their country."""
        area = self.cfg.area(state.data.city_id) or self.cfg.area(state.application.area_id)
        if area:
            return area.timezone
        return COUNTRY_TIMEZONES.get(state.application.country or "", self.cfg.agent.default_timezone)

    # ------------------------------------------------------------------ turn
    def _handle(self, conversation_id: str, text: str) -> TurnResult:
        state = self.repo.get_state(conversation_id)
        text = (text or "").strip()[:MAX_INBOUND_CHARS]
        if not text:
            return TurnResult(conversation_id=state.id, locale=state.locale, stage=state.stage, messages=[], completed=state.is_terminal, data=state.data)

        history = self.repo.transcript(conversation_id)
        state.last_candidate_message_at = self.clock()
        today = self._today(state)
        events: list[Event] = []

        topics = self.knowledge.search(text)
        try:
            analysis = self.understander.analyze(
                UnderstandRequest(
                    message=text,
                    stage=state.stage,
                    current_field=state.current_field,
                    last_agent_message=next((m.text for m in reversed(history) if m.role == "agent"), None),
                    known=self._known(state),
                    today=today,
                    language=state.language,
                    faq_topics=topics,
                )
            )
        except LLMError as exc:
            # We could not understand: say so and ask again. The attempt is not counted.
            log.warning("understand failed: %s", exc)
            reply = OutboundMessage(text=self.cfg.copy_.text("misc.technical_issue", state.locale))
            self.repo.save_turn(
                state,
                [("candidate", text, {"error": "understand_failed"}), ("agent", reply.text, {"source": "template"})],
                [Event("llm_error", {"step": "understand", "error": str(exc)[:300]})],
            )
            return TurnResult(conversation_id=state.id, locale=state.locale, stage=state.stage, messages=[reply], completed=False, data=state.data)

        working = state.model_copy(deep=True)
        if working.followups_sent or working.abandoned_at:
            # They came back after our follow-ups: the metric that proves re-engagement works.
            events.append(Event("resumed", {
                "after_followups": working.followups_sent,
                "was_abandoned": working.abandoned_at is not None,
                "field": working.current_field,
            }))
            working.followups_sent, working.last_followup_at, working.abandoned_at = 0, None, None
        decision = self.policy.decide(working, analysis, text, today)
        events += decision.events
        if working.is_terminal and not state.is_terminal:
            working.completed_at = self.clock()  # one clock for the whole engine (testable, replayable)
        interview_changes = self._schedule(state, working, decision.directive, events)

        history.append(ChatMessage(role="candidate", text=text))
        outbound, metas = self._render(working, decision.directive, history, today, events)

        read = {"analysis": analysis.model_dump(mode="json")}
        if len(topics) < len(self.cfg.faq):
            read["faq_topics"] = [t.id for t in topics]  # what retrieval offered, to audit misses
        rows = [("candidate", text, read)]
        rows += [("agent", m.text, meta) for m, meta in zip(outbound, metas)]
        try:
            self.repo.save_turn(working, rows, events, interview_changes)
        except SlotTaken:
            # Two candidates picked the same time at once (found by the volume test): the database kept
            # one booking; the other candidate is offered the next free times, as when it was taken earlier.
            self._slot_taken(working, decision.directive, events)
            interview_changes = self._interview_changes(state.interview, working.interview)
            outbound, metas = self._render(working, decision.directive, history, today, events)
            rows = rows[:1] + [("agent", m.text, meta) for m, meta in zip(outbound, metas)]
            self.repo.save_turn(working, rows, events, interview_changes)
        return TurnResult(
            conversation_id=working.id,
            locale=working.locale,
            stage=working.stage,
            messages=outbound,
            completed=working.is_terminal,
            data=working.data,
            analysis=analysis,
            event_types=[e.type for e in events],
            faq_topics=read.get("faq_topics", []),
        )

    # ------------------------------------------------------------------ interview booking
    def _schedule(self, before: ConversationState, state: ConversationState, directive: Directive, events) -> list:
        """Pick interview times for the policy's decision and work out the bookings to store.
        Times depend on bookings already taken (the database), so they are chosen here; which
        one the candidate chose, and what happens next, is the policy's decision."""
        if not self.cfg.scheduling.enabled:
            return []
        if directive.kind == "outcome" and directive.outcome == "qualified":
            self._offer_interview(state, directive, events)
        elif directive.kind == "interview_offer" and "same_slots" not in directive.notes:
            self._offer_interview(state, directive, events)
        elif directive.kind == "interview_booked":
            iv = state.interview
            if iv.slot in self.repo.taken_interview_slots(iv.area_id):  # taken by someone else meanwhile
                self._slot_taken(state, directive, events)
        return self._interview_changes(before.interview, state.interview)

    def _slot_taken(self, state: ConversationState, directive: Directive, events) -> None:
        iv = state.interview
        events.append(Event("interview_slot_taken", {"slot": iv.slot.isoformat()}))
        iv.status, iv.slot = InterviewStatus.OFFERED, None
        directive.kind = "interview_offer"
        directive.notes.append("taken")
        self._offer_interview(state, directive, events, count_round=False)

    @staticmethod
    def _interview_changes(old: InterviewState | None, new: InterviewState | None) -> list:
        """The bookings to store: cancel the old time, book the new one."""
        changes = []
        old_slot = old.slot if old and old.status == InterviewStatus.BOOKED else None
        new_slot = new.slot if new and new.status == InterviewStatus.BOOKED else None
        if old_slot and old_slot != new_slot:
            changes.append(("cancel", old.area_id, old_slot))
        if new_slot and new_slot != old_slot:
            changes.append(("book", new.area_id, new_slot))
        return changes

    def _offer_interview(self, state: ConversationState, directive: Directive, events, count_round: bool = True) -> None:
        area = self.cfg.area(state.interview.area_id if state.interview else state.data.city_id)
        if area is None:
            return  # a qualified candidate always has a configured area; never crash on it
        iv = state.interview or InterviewState(status=InterviewStatus.OFFERED, area_id=area.id,
                                               place=area.interview_place or area.name, timezone=area.timezone)
        state.interview = iv
        unavailable = self.repo.taken_interview_slots(area.id) | set(iv.history)
        slots = candidate_slots(self.cfg.scheduling, area.timezone, self.clock(), state.data.preferred_schedule, unavailable)
        if not slots:  # nothing free in the horizon: a person finds a time
            iv.status = InterviewStatus.HANDED_OFF
            state.add_flag("scheduling_needed")
            events.append(Event("interview_handoff", {"reason": "no_free_slots"}))
            if directive.kind == "outcome":
                directive.interview_offer = False  # the final message gives the recruiter-contact next step
            else:
                directive.kind = "interview_handoff"
            return
        iv.status, iv.offered, iv.reminded = InterviewStatus.OFFERED, slots, False
        iv.history = iv.history + slots
        if count_round:
            iv.offers += 1
        events.append(Event("interview_offered", {"slots": [s.isoformat() for s in slots], "round": iv.offers}))
        if directive.kind == "outcome":
            directive.interview_offer = True

    def _interview_message(self, state: ConversationState, directive: Directive) -> OutboundMessage:
        """Times and places are exact, so these messages are templates (like the recap)."""
        iv, loc, copy = state.interview, state.locale, self.cfg.copy_
        area = self.cfg.area(iv.area_id)
        tz = area.timezone if area else self.cfg.agent.default_timezone
        if directive.kind == "interview_booked":
            return OutboundMessage(text=copy.text("interview.booked", loc, when=slot_long(iv.slot, tz, loc), place=iv.place))
        if directive.kind == "interview_handoff":
            return OutboundMessage(text=copy.text("interview.handoff", loc))
        options = "\n".join(f"{i}) {slot_long(slot, tz, loc)}" for i, slot in enumerate(iv.offered, 1))
        key = ("interview.taken" if "taken" in directive.notes else "interview.reminder" if "same_slots" in directive.notes
               else "interview.offer_again" if iv.offers > 1 else "interview.offer")
        return OutboundMessage(
            text=copy.text(key, loc, place=iv.place, options=options),
            quick_replies=[slot_label(slot, tz, loc) for slot in iv.offered] + [copy.text("interview.none_option", loc)],
        )

    # ------------------------------------------------------------------ speaking
    def _render(self, state, directive: Directive, history, today, events):
        if directive.kind == "silent":
            return [], []
        directive.voice = state.channel == "voice"  # same decisions, spoken wording (ADR 0010)
        if directive.kind in ("interview_offer", "interview_booked", "interview_handoff"):
            meta = {"kind": directive.kind, "source": "template", "directive": directive.model_dump(mode="json")}
            return [self._interview_message(state, directive)], [meta]
        if directive.kind == "outcome" and directive.interview_offer:
            text, meta = self._speak(directive, history, events)
            offer = self._interview_message(state, directive.model_copy(update={"kind": "interview_offer"}))
            offer_meta = {"kind": "interview_offer", "source": "template", "directive": directive.model_dump(mode="json")}
            return [OutboundMessage(text=text), offer], [meta, offer_meta]
        if directive.kind == "recap":
            out, metas = [], []
            if directive.answer or directive.notes:
                interlude = directive.model_copy(update={"kind": "interlude"})
                text, meta = self._speak(interlude, history, events)
                out.append(OutboundMessage(text=text))
                metas.append(meta)
            out.append(
                OutboundMessage(
                    text=render_recap(state, self.cfg.copy_, today, updated=directive.recap_updated),
                    quick_replies=self.cfg.copy_.options("confirm", state.locale),
                )
            )
            metas.append({"kind": "recap", "source": "template", "directive": directive.model_dump(mode="json")})
            return out, metas

        text, meta = self._speak(directive, history, events)
        return [OutboundMessage(text=text, quick_replies=self._quick_replies(directive))], [meta]

    def _speak(self, directive: Directive, history, events) -> tuple[str, dict]:
        """LLM draft -> output guard -> one retry with feedback -> template fallback."""
        limit = self._char_limit(directive)
        feedback = None
        for _ in range(2):
            try:
                text = self.responder.compose(SpeakRequest(directive=directive, history=history, feedback=feedback))
            except LLMError as exc:
                events.append(Event("llm_error", {"step": "speak", "error": str(exc)[:300]}))
                break
            problem = self._guard(text, limit)
            if problem is None:
                return text, {"kind": directive.kind, "source": "llm", "directive": directive.model_dump(mode="json")}
            events.append(Event("guard_rejected", {"problem": problem}))
            feedback = problem
        text = self.templates.compose(SpeakRequest(directive=directive, history=history))
        return text, {"kind": directive.kind, "source": "template", "directive": directive.model_dump(mode="json")}

    @staticmethod
    def _guard(text: str, limit: int) -> str | None:
        """Cheap deterministic output checks; the prompt is the first line of defence, not the only one."""
        if len(text) > limit:
            return f"{len(text)} characters, the limit is {limit}"
        if any(marker in text for marker in ("**", "##", "TURN INSTRUCTIONS", "\n- ")):
            return "it contains markdown or leaked instructions"
        return None

    def _char_limit(self, directive: Directive) -> int:
        base = self.cfg.agent.max_message_chars
        limit = int(base * 1.4) if directive.kind == "outcome" or directive.answer else base
        return int(limit * 0.8) if directive.voice else limit  # listening is slower than reading

    def _quick_replies(self, directive: Directive) -> list[str]:
        copy, loc = self.cfg.copy_, directive.locale
        if directive.kind == "ask" and directive.ask_issue == "license_type":  # before the licence's own Sí/No
            return copy.options("license_type", loc)
        if (directive.kind == "ask" and directive.ask_field == FieldName.ZONE and directive.ask_options
                and directive.ask_issue in (None, "zone_unlisted")):
            return directive.ask_options + copy.options("zone_any", loc)
        if directive.kind == "ask" and directive.ask_field in QUICK_REPLIES_BY_FIELD:
            return copy.options(QUICK_REPLIES_BY_FIELD[directive.ask_field], loc)
        if directive.kind == "outcome" and directive.outcome in ("no_license", "license_in_progress", "out_of_area", "license_type_not_accepted"):
            return copy.options("talent_pool", loc)
        return []

    # ------------------------------------------------------------------ helpers
    def _today(self, state: ConversationState) -> date:
        """'Today' in the candidate's timezone: Spain and Mexico can be on different dates."""
        tz = ZoneInfo(self._timezone(state))
        now: datetime = self.clock()
        return now.replace(tzinfo=ZoneInfo("UTC")).astimezone(tz).date()

    @staticmethod
    def _known(state: ConversationState) -> dict[str, str]:
        d = state.data
        details = ", ".join(v for v in (d.license_type and d.license_type.value, d.license_country) if v)
        known = {
            "name": d.full_name,
            "licence": (f"{d.license_status.value} ({details})" if details else d.license_status.value)
            if d.license_status else None,
            "city": d.city,
            "zone": d.zone,
            "availability": ",".join(a.value for a in d.availability) or None,
            "schedule": ",".join(s.value for s in d.preferred_schedule) or None,
            "experience_months": str(d.experience_months) if d.experience_months is not None else None,
            "platforms": ",".join(d.experience_platforms) or None,
            "start_date": d.start_date.isoformat() if d.start_date else None,
        }
        return {k: v for k, v in known.items() if v}

    def _fallback_summary(self, state: ConversationState) -> dict:
        d = state.data
        parts = [d.full_name or "?", d.city or d.location_raw or "?", ", ".join(a.value for a in d.availability) or "?"]
        return {
            "headline": " · ".join(parts),
            "summary": f"Outcome: {state.stage.value}.",
            "strengths": [],
            "concerns": [f.code for f in state.flags],
            "candidate_questions": state.pending_questions,
            "recommended_action": "Review manually (automatic summary unavailable).",
            "source": "template",
        }

    def _lock_for(self, conversation_id: str) -> threading.Lock:
        with self._locks_guard:
            return self._locks[conversation_id]
