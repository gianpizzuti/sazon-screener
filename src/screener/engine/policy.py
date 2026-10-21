"""The screening policy: deterministic decisions, one candidate message at a time.

Input: the conversation state + what the model understood from the latest message.
Output: the updated state + a Directive (what to say next) + events (audit trail).

Nothing here calls an LLM. Eligibility, validation, ordering and loop-prevention are
plain Python, which is why a prompt injection cannot "qualify" anyone, and why every
rule in docs/process-design.md has a unit test.
"""

from __future__ import annotations

from datetime import date

from screener.config import ClientConfig
from screener.domain.locations import LocationMatcher
from screener.domain.models import (
    LicenseType,
    FIELD_ORDER,
    KNOCKOUT_FIELDS,
    OPTIONAL_FIELDS,
    ConversationState,
    DisqualificationReason,
    FieldName,
    FieldStatus,
    LicenseStatus,
    ScreeningData,
    Stage,
    utcnow,
)
from screener.domain.text import function_word_language, is_grounded
from screener.domain.validators import (
    Validation,
    normalize_platforms,
    resolve_start_date,
    validate_availability,
    validate_experience_months,
    validate_full_name,
    validate_schedule,
    validate_start_date,
)
from screener.engine.directive import AnswerToQuestion, Decision, Directive, Event
from screener.llm.schemas import Extracted, TurnAnalysis

DONE = {FieldStatus.VALID, FieldStatus.SKIPPED, FieldStatus.UNCLEAR}
MIN_WORDS_WITHOUT_SIGNAL = 4
# Intents that mean "I did not try to answer your question" (no failed attempt counted).
# Replies to the recap that don't confirm it before a person takes over (needs review).
MAX_RECAP_ROUNDS = 3
NON_ATTEMPT_INTENTS = {"question", "smalltalk", "human_request", "postpone", "abuse"}
TONE_BY_SENTIMENT = {"confused": "simplify", "frustrated": "reassuring"}

# Which ScreeningData attributes belong to each field (to detect corrections).
FIELD_ATTRS: dict[FieldName, tuple[str, ...]] = {
    FieldName.FULL_NAME: ("full_name",),
    FieldName.DRIVERS_LICENSE: ("license_status", "license_type"),
    FieldName.LOCATION: ("city_id", "in_service_area"),
    FieldName.ZONE: ("zone",),
    FieldName.AVAILABILITY: ("availability",),
    FieldName.SCHEDULE: ("preferred_schedule",),
    FieldName.EXPERIENCE_YEARS: ("experience_years",),
    FieldName.EXPERIENCE_PLATFORMS: ("experience_platforms",),
    FieldName.START_DATE: ("start_date",),
}


CORRECTION_GROUPS: dict[str, list[FieldName]] = {
    "full_name": [FieldName.FULL_NAME],
    "drivers_license": [FieldName.DRIVERS_LICENSE],
    "location": [FieldName.LOCATION, FieldName.ZONE],
    "availability": [FieldName.AVAILABILITY],
    "schedule": [FieldName.SCHEDULE],
    "experience": [FieldName.EXPERIENCE_YEARS, FieldName.EXPERIENCE_PLATFORMS],
    "start_date": [FieldName.START_DATE],
}


class ScreeningPolicy:
    def __init__(self, config: ClientConfig):
        self.cfg = config
        self.matcher = LocationMatcher(config.service_areas)

    # ------------------------------------------------------------------ entry point
    def decide(
        self, state: ConversationState, analysis: TurnAnalysis, message: str, today: date
    ) -> Decision:
        """Mutates `state` (callers pass a copy) and returns what to say next."""
        events: list[Event] = []
        intents = set(analysis.intents)
        notes: list[str] = []

        # A candidate who withdrew can come back: re-open where they left.
        if state.stage == Stage.WITHDRAWN and intents & {"affirm", "provide_info"} and "opt_out" not in intents:
            self._set_stage(state, Stage.SCREENING, events)
            state.completed_at = None
            notes.append("resume")

        self._update_language(state, analysis, message, events)
        directive = Directive(kind="ask", locale=state.locale, notes=notes)

        if "abuse" in intents:
            state.abuse_strikes += 1
            state.add_flag("abuse")
            events.append(Event("abuse_strike", {"strikes": state.abuse_strikes}))
            if state.abuse_strikes >= 2:
                return self._finish(state, Stage.TERMINATED, "terminated", events)
            directive.notes.append("abuse_warning")

        if "question" in intents or analysis.question:
            directive.answer = self._answer_question(state, analysis, events)

        if state.is_terminal:
            return self._after_end(state, intents, directive, events, analysis)

        if "opt_out" in intents:
            return self._finish(state, Stage.WITHDRAWN, "withdrawn", events)

        if "human_request" in intents:
            state.add_flag("human_requested")
            directive.notes.append("human_request")
            events.append(Event("human_requested"))

        directive.tone = TONE_BY_SENTIMENT.get(analysis.sentiment, "normal")
        if analysis.sentiment in TONE_BY_SENTIMENT:
            events.append(Event("sentiment", {"value": analysis.sentiment, "field": state.current_field}))

        captured = self._apply_extraction(state, analysis.extracted, analysis, message, today, events)
        if analysis.correction_target:
            self._reopen(state, analysis.correction_target, captured, events)

        if not captured and "postpone" in intents:
            directive.kind = "postpone_ack"
            return self._done(state, directive, events)

        if state.stage == Stage.INTRO:
            if not captured and "deny" in intents and directive.answer is None:
                return self._finish(state, Stage.WITHDRAWN, "withdrawn", events)
            self._set_stage(state, Stage.SCREENING, events)

        reason = self._knockout(state)
        if reason:
            return self._finish(state, Stage.DISQUALIFIED, reason.value, events, reason=reason, answer=directive.answer)

        if state.stage == Stage.CONFIRMING:
            if handoff := self._recap_round(state, analysis, captured, directive, events, message):
                return handoff

        if state.stage == Stage.CONFIRMING and not captured:
            if self.next_field(state) is not None:  # a correction reopened a field
                return self._next_step(state, directive, events, captured)
            if "affirm" in intents and "deny" not in intents:
                return self._complete(state, events, directive.answer)
            if intents & {"deny", "correction"}:
                directive.kind = "ask_correction"
                return self._done(state, directive, events)
            directive.kind = "recap"
            return self._done(state, directive, events, captured)

        self._account_attempt(state, intents, captured, events)
        return self._next_step(state, directive, events, captured)

    # ------------------------------------------------------------------ flow
    def _next_step(self, state, directive, events, captured) -> Decision:
        nxt = self.next_field(state)
        if nxt is None:
            self._set_stage(state, Stage.CONFIRMING, events)
            state.current_field = None
            directive.kind = "recap"
            return self._done(state, directive, events, captured)

        if state.stage == Stage.CONFIRMING:  # a correction made a field invalid
            self._set_stage(state, Stage.SCREENING, events)
        fs = state.field(nxt)
        directive.kind = "ask"
        directive.ask_field = nxt
        directive.ask_issue = fs.last_error if fs.status == FieldStatus.INVALID else None
        directive.ask_options = list(fs.hint_options)
        directive.zone_city = state.data.city
        state.current_field = nxt
        fs.times_asked += 1
        directive.remaining_questions = self.remaining_questions(state)
        return self._done(state, directive, events, captured)

    def next_field(self, state: ConversationState) -> FieldName | None:
        for name in FIELD_ORDER:
            fs = state.field(name)
            if fs.status in DONE:
                continue
            if name == FieldName.ZONE:
                if state.data.in_service_area is not True or fs.times_asked >= 2:
                    continue
            if name == FieldName.EXPERIENCE_PLATFORMS:
                if state.field(FieldName.EXPERIENCE_YEARS).status != FieldStatus.VALID:
                    continue
                if not state.data.experience_years:
                    continue
            return name
        return None

    def remaining_questions(self, state: ConversationState) -> int:
        """Questions still to answer, the current one included (shown to frustrated candidates)."""
        return sum(
            1
            for name in FIELD_ORDER
            if name not in OPTIONAL_FIELDS
            and name != FieldName.EXPERIENCE_PLATFORMS
            and state.field(name).status not in DONE
        )

    def _account_attempt(self, state, intents, captured, events) -> None:
        """Count a failed attempt on the field we asked; give up after the limit (no loops)."""
        current = state.current_field
        if current is None or state.stage != Stage.SCREENING:
            return
        fs = state.field(current)
        if fs.status in DONE:
            return
        if intents and intents <= NON_ATTEMPT_INTENTS:
            return  # they asked something / greeted: not a failed answer
        if current in OPTIONAL_FIELDS:
            fs.status = FieldStatus.SKIPPED  # an optional question is never repeated
            events.append(Event("field_skipped", {"field": current}))
            return
        if captured:
            return  # they answered something else: cooperative, just ask again
        fs.failed_attempts += 1
        if fs.status == FieldStatus.MISSING:
            fs.status = FieldStatus.INVALID
            fs.last_error = "no_answer"
        if fs.failed_attempts >= self.cfg.agent.max_failed_attempts:
            fs.status = FieldStatus.UNCLEAR
            state.add_flag("unclear_field", current.value)
            events.append(Event("field_unclear", {"field": current, "error": fs.last_error}))

    def _knockout(self, state: ConversationState) -> DisqualificationReason | None:
        data = state.data
        if data.license_status == LicenseStatus.NO:
            return DisqualificationReason.NO_LICENSE
        if data.license_status == LicenseStatus.IN_PROGRESS:
            return DisqualificationReason.LICENSE_IN_PROGRESS
        if data.in_service_area is False:
            return DisqualificationReason.OUT_OF_AREA
        return None

    def _recap_round(self, state, analysis, captured, directive, events, message) -> Decision | None:
        """The recap always ends: confirmed, corrected, or handed to a person.

        Found by the conversation eval: candidates "corrected" a date by restating it ("mañana"
        for "miércoles 21/10") and got the same recap five times, then gave up.
        """
        intents = set(analysis.intents)
        if "affirm" in intents and "deny" not in intents and not captured:
            return None  # confirmed: the normal path completes the screening
        state.recap_rounds += 1
        if state.recap_rounds >= MAX_RECAP_ROUNDS:
            state.add_flag("recap_not_confirmed", message[:160])
            events.append(Event("recap_not_confirmed", {"rounds": state.recap_rounds}))
            return self._finish(state, Stage.NEEDS_REVIEW, "needs_review", events)
        changed = {e.payload.get("field") for e in events if e.type == "field_corrected"}
        restated = [f for f in captured if f not in changed]
        directive.recap_updated = bool(changed)
        if captured and len(restated) == len(captured):
            if "affirm" in intents and not intents & {"deny", "correction"}:
                return self._complete(state, events, directive.answer)  # confirmed, restating a detail
            # What they "corrected" is what the summary already says: explain, then show it again.
            directive.kind = "recap"
            directive.notes.append("unchanged")
            directive.unchanged = [self.describe(state, f) + f' (they said: "{state.field(f).evidence}")' for f in restated]
            return self._done(state, directive, events)
        return None

    def _complete(self, state, events, answer=None) -> Decision:
        if any(state.field(f).status == FieldStatus.UNCLEAR for f in KNOCKOUT_FIELDS):
            return self._finish(state, Stage.NEEDS_REVIEW, "needs_review", events, answer=answer)
        return self._finish(state, Stage.QUALIFIED, "qualified", events, answer=answer)

    def _finish(self, state, stage, outcome, events, reason=None, answer=None) -> Decision:
        self._set_stage(state, stage, events)
        state.current_field = None
        state.completed_at = utcnow()
        state.disqualification_reason = reason
        if reason:
            events.append(Event("knockout", {"reason": reason.value}))
        events.append(Event("completed", {"outcome": outcome}))
        directive = Directive(
            kind="silent" if stage == Stage.TERMINATED else "outcome",
            locale=state.locale,
            candidate_name=_first_name(state.data),
            outcome=outcome,
            outcome_place=state.data.location_raw,
            answer=answer,  # "sí, todo correcto, ¿hay parking?": the question is still answered
        )
        return Decision(directive, events)

    def _after_end(self, state, intents, directive, events, analysis: TurnAnalysis) -> Decision:
        """Messages after the screening ended.

        Questions are always answered; new information is flagged for a recruiter; small
        talk ("ok", "gracias", "bye") gets at most one courtesy reply, then silence, so
        the bot never ping-pongs forever.
        """
        silent = Decision(Directive(kind="silent", locale=state.locale), events)
        if state.stage == Stage.TERMINATED:
            return silent
        if (
            state.stage == Stage.DISQUALIFIED
            and state.talent_pool_opt_in is None
            and intents & {"affirm", "deny"}
        ):
            state.talent_pool_opt_in = "affirm" in intents and "deny" not in intents
            events.append(Event("talent_pool", {"opt_in": state.talent_pool_opt_in}))
            directive.kind = "talent_pool_ack"
            directive.talent_pool_answer = state.talent_pool_opt_in
            directive.candidate_name = _first_name(state.data)
            return Decision(directive, events)
        directive.kind = "closed_followup"
        if directive.answer:
            return Decision(directive, events)
        if intents & {"provide_info", "correction"} and _has_values(analysis):
            state.add_flag("update_after_close", ", ".join(e.field for e in analysis.evidence))
            events.append(Event("update_after_close", {"fields": [e.field for e in analysis.evidence]}))
            directive.notes.append("update_after_close")
            return Decision(directive, events)
        if state.post_close_replies >= 1:
            events.append(Event("ignored_after_close"))
            return silent
        state.post_close_replies += 1
        return Decision(directive, events)

    def _done(self, state, directive, events, captured=()) -> Decision:
        directive.locale = state.locale
        # The name is offered to the writer only right after we learn it (and in the final
        # message): otherwise models put it in every single message.
        directive.candidate_name = _first_name(state.data) if FieldName.FULL_NAME in captured else None
        directive.acknowledge = [self.describe(state, f) for f in captured]
        return Decision(directive, events)

    # ------------------------------------------------------------------ understanding -> state
    def _update_language(self, state, analysis: TurnAnalysis, message: str, events) -> None:
        # Hysteresis: the model must see a clear new language AND the deterministic check must
        # confirm it, or (for long mixed messages with no function-word signal) at least not
        # contradict it. Short loanword answers ("full time", "flexible") never switch.
        second_opinion = function_word_language(message)
        confirmed = second_opinion == analysis.language or (
            second_opinion is None and len(message.split()) >= MIN_WORDS_WITHOUT_SIGNAL
        )
        if analysis.language_is_clear and analysis.language != state.language and confirmed:
            events.append(Event("language_switched", {"from": state.language, "to": analysis.language}))
            state.language = analysis.language
        if state.data.country is None and analysis.spanish_variant != "unknown":
            state.spanish_variant = analysis.spanish_variant

    def _answer_question(self, state, analysis: TurnAnalysis, events) -> AnswerToQuestion:
        question = analysis.question or "(question)"
        entry = self.cfg.faq_entry(analysis.faq_id)
        if entry:
            events.append(Event("question_answered", {"faq_id": entry.id, "question": question}))
            return AnswerToQuestion(question=question, answer=entry.answer_for(state.data.country), faq_id=entry.id)
        state.pending_questions.append(question)
        events.append(Event("question_unanswered", {"question": question}))
        return AnswerToQuestion(question=question)

    def _apply_extraction(
        self, state, x: Extracted, analysis: TurnAnalysis, message: str, today: date, events
    ) -> list[FieldName]:
        """Validate and store every grounded value. Returns the fields that became valid."""
        before = state.data.model_copy(deep=True)
        quotes = {e.field: e.quote for e in analysis.evidence if is_grounded(e.quote, message)}
        captured: list[FieldName] = []

        def grounded(group: str) -> str | None:
            if group in quotes:
                return quotes[group]
            events.append(Event("ungrounded_value", {"field": group}))
            return None

        # A knock-out ends the screening, so it needs an answer to the knock-out question, the
        # recap or an explicit correction: a place or a licence mentioned in passing never ends it
        # (the extraction eval read "6 months with Deliveroo in Berlin" as where the candidate lives).
        def may_knock_out(*fields: FieldName) -> bool:
            return state.current_field in fields or state.stage == Stage.CONFIRMING or "correction" in analysis.intents

        data = state.data
        if x.full_name and (q := grounded("full_name")):
            self._record(state, FieldName.FULL_NAME, validate_full_name(x.full_name), q,
                         lambda v: setattr(data, "full_name", v), captured, events)

        # "es de moto" at the recap only adds the type to a licence they already have.
        licence = x.drivers_license or ("yes" if x.license_type and data.license_status == LicenseStatus.YES else None)
        if licence and (q := grounded("drivers_license")):
            status = LicenseStatus(licence)

            def set_license(v: LicenseStatus) -> None:
                data.license_status = v
                data.has_drivers_license = v == LicenseStatus.YES
                if v != LicenseStatus.YES:
                    data.license_type = None
                elif x.license_type:
                    data.license_type = LicenseType(x.license_type)

            if status != LicenseStatus.YES and not may_knock_out(FieldName.DRIVERS_LICENSE):
                events.append(Event("knockout_deferred", {"field": FieldName.DRIVERS_LICENSE, "value": status.value}))
            else:
                self._record(state, FieldName.DRIVERS_LICENSE, Validation(value=status), q, set_license, captured, events)

        if (x.location_text or x.location_city_id or x.location_outside_service_area) and (q := grounded("location")):
            self._apply_location(state, x, q, captured, events, solicited=may_knock_out(FieldName.LOCATION, FieldName.ZONE))

        if x.availability is not None and (q := grounded("availability")):
            self._record(state, FieldName.AVAILABILITY, validate_availability(x.availability), q,
                         lambda v: setattr(data, "availability", v), captured, events)

        if x.schedule is not None and (q := grounded("schedule")):
            self._record(state, FieldName.SCHEDULE, validate_schedule(x.schedule), q,
                         lambda v: setattr(data, "preferred_schedule", v), captured, events)

        if (x.experience_months is not None or x.experience_platforms) and (q := grounded("experience")):
            if x.experience_months is not None:
                result = validate_experience_months(x.experience_months)

                def set_experience(months: int) -> None:
                    data.experience_months = months
                    data.experience_years = round(months / 12, 2)

                self._record(state, FieldName.EXPERIENCE_YEARS, result, q, set_experience, captured, events)
                if result.ok and result.value == 0:
                    data.experience_platforms = []
                    state.field(FieldName.EXPERIENCE_PLATFORMS).status = FieldStatus.SKIPPED
            if x.experience_platforms:
                platforms = normalize_platforms(x.experience_platforms, self.cfg.platforms)
                self._record(state, FieldName.EXPERIENCE_PLATFORMS, Validation(value=platforms), q,
                             lambda v: setattr(data, "experience_platforms", v), captured, events)

        if x.start_date and (q := grounded("start_date")):
            resolved = resolve_start_date(x.start_date, today)
            result = validate_start_date(resolved.value, today, self.cfg.agent.late_start_days) if resolved.ok else resolved

            def set_start(v) -> None:
                data.start_date = v
                data.start_date_raw = q

            self._record(state, FieldName.START_DATE, result, q, set_start, captured, events)

        self._detect_corrections(state, before, captured, events)
        return captured

    def _apply_location(self, state, x: Extracted, quote: str, captured, events, solicited: bool = True) -> None:
        data = state.data
        raw = x.location_text or quote
        if not solicited and state.field(FieldName.LOCATION).status == FieldStatus.VALID:
            # Another place mentioned in passing does not move a location the candidate already gave.
            events.append(Event("unsolicited_value_ignored", {"field": FieldName.LOCATION, "text": raw}))
            return
        match = self.matcher.match(raw)
        city_id, zone = None, None
        if match.status == "resolved":
            city_id, zone = match.city_id, match.zone
        elif match.status == "ambiguous" and x.location_city_id in match.option_city_ids:
            city_id = x.location_city_id  # the model breaks the tie, among options rules found
        elif match.status == "no_match" and self.cfg.area(x.location_city_id):
            city_id = x.location_city_id  # place not in our aliases but the model knows it is inside
        fs = state.field(FieldName.LOCATION)
        if city_id and not zone:
            zone = (
                self.matcher.zone_in_city(city_id, x.location_zone or raw)
                or _zone_from_options(fs.hint_options, self.cfg.area(city_id).name)  # "centro" -> "Madrid"
                or _clean_zone(x.location_zone)
            )
        if city_id:
            area = self.cfg.area(city_id)
            if data.city_id and data.city_id != area.id:
                data.zone = None  # new city: the old zone no longer applies
                state.field(FieldName.ZONE).status = FieldStatus.MISSING
            data.location_raw, data.city_id, data.city = raw, area.id, area.name
            data.country, data.in_service_area = area.country, True
            state.spanish_variant = "es-ES" if area.country == "ES" else "es-MX"
            self._mark_valid(state, FieldName.LOCATION, quote, captured, events)
            if zone:
                data.zone = zone
                self._mark_valid(state, FieldName.ZONE, quote, captured, events)
            return
        if match.status == "no_match" and x.location_outside_service_area is True:
            if not solicited:
                events.append(Event("knockout_deferred", {"field": FieldName.LOCATION, "text": raw}))
                return  # asked in its turn: the answer to the location question decides
            data.location_raw, data.city_id, data.city, data.zone = raw, None, raw, None
            data.country, data.in_service_area = None, False
            self._mark_valid(state, FieldName.LOCATION, quote, captured, events)
            return
        if fs.status != FieldStatus.VALID:
            fs.status = FieldStatus.INVALID
            fs.last_error = "location_ambiguous" if match.status == "ambiguous" else "location_unknown"
            fs.hint_options = match.options
        events.append(Event("field_invalid", {"field": FieldName.LOCATION, "error": fs.last_error, "text": raw}))

    def _reopen(self, state, group: str, captured, events) -> None:
        """The candidate says a detail is wrong without giving the new value: ask it again."""
        for name in CORRECTION_GROUPS[group]:
            if name in captured:
                return
        for name in CORRECTION_GROUPS[group]:
            fs = state.field(name)
            fs.status, fs.failed_attempts, fs.times_asked, fs.last_error = FieldStatus.MISSING, 0, 0, None
        events.append(Event("field_reopened", {"field": group}))

    def _record(self, state, name: FieldName, result: Validation, quote: str, apply, captured, events) -> None:
        fs = state.field(name)
        if result.value is not None:
            apply(result.value)  # keep partial values too (a first name is still useful)
        if result.ok:
            self._mark_valid(state, name, quote, captured, events)
            if result.flag:
                state.add_flag(result.flag, name.value)
        else:
            # During screening a bad side remark never erases a good answer; at the recap
            # the candidate is explicitly correcting, so the field is reopened.
            if fs.status != FieldStatus.VALID or state.stage == Stage.CONFIRMING:
                fs.status = FieldStatus.INVALID
                fs.last_error = result.error
            events.append(Event("field_invalid", {"field": name, "error": result.error}))

    def _mark_valid(self, state, name: FieldName, quote: str, captured, events) -> None:
        fs = state.field(name)
        fs.status, fs.last_error, fs.hint_options, fs.evidence = FieldStatus.VALID, None, [], quote
        if name not in captured:
            captured.append(name)
        events.append(Event("field_valid", {"field": name}))

    def _detect_corrections(self, state, before: ScreeningData, captured, events) -> None:
        for name in captured:
            old = tuple(getattr(before, a) for a in FIELD_ATTRS[name])
            new = tuple(getattr(state.data, a) for a in FIELD_ATTRS[name])
            if any(v not in (None, []) for v in old) and old != new:
                events.append(Event("field_corrected", {"field": name}))

    @staticmethod
    def _set_stage(state, stage: Stage, events) -> None:
        if state.stage != stage:
            events.append(Event("stage_changed", {"from": state.stage, "to": stage}))
            state.stage = stage

    # ------------------------------------------------------------------ descriptions
    def describe(self, state: ConversationState, name: FieldName) -> str:
        """English description of a captured value, for the responder's acknowledgement."""
        d = state.data
        match name:
            case FieldName.FULL_NAME:
                return f"their name is {d.full_name}"
            case FieldName.DRIVERS_LICENSE:
                if not d.has_drivers_license:
                    return "they don't have a valid license"
                return "they have a valid driver's license" + (f" ({d.license_type.value})" if d.license_type else "")
            case FieldName.LOCATION:
                return f"they would deliver in {d.city}" if d.in_service_area else f"they are in {d.location_raw}"
            case FieldName.ZONE:
                return f"area: {d.zone}"
            case FieldName.AVAILABILITY:
                return "availability: " + ", ".join(a.value.replace("_", "-") for a in d.availability)
            case FieldName.SCHEDULE:
                return "preferred shift: " + ", ".join(s.value for s in d.preferred_schedule)
            case FieldName.EXPERIENCE_YEARS:
                if not d.experience_months:
                    return "no previous delivery experience"
                return f"{d.experience_months} months of delivery experience"
            case FieldName.EXPERIENCE_PLATFORMS:
                return "worked with " + ", ".join(d.experience_platforms)
            case FieldName.START_DATE:
                return f"can start on {d.start_date.strftime('%A %d/%m')}"
        return name.value


def _has_values(analysis: TurnAnalysis) -> bool:
    return bool(analysis.evidence) and any(
        v not in (None, []) for v in analysis.extracted.model_dump().values()
    )


def _first_name(data: ScreeningData) -> str | None:
    return data.full_name.split()[0] if data.full_name else None


def _zone_from_options(options: list[str], city_name: str) -> str | None:
    """Options look like 'Centro (Madrid)': pick the zone offered for the city they chose."""
    suffix = f" ({city_name})"
    return next((o.removesuffix(suffix) for o in options if o.endswith(suffix)), None)


def _clean_zone(zone: str | None) -> str | None:
    zone = (zone or "").strip()
    return zone.title() if zone.islower() else zone or None
