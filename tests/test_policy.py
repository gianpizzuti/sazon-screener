"""Every branch of docs/process-design.md, without any LLM."""

from datetime import date

from conftest import TODAY, analysis, start_expr
from screener.domain.models import DisqualificationReason, FieldName, FieldStatus, Stage


def say(policy, state, message, **kw):
    """One candidate turn; returns (directive, event types)."""
    decision = policy.decide(state, analysis(message, **kw), message, TODAY)
    return decision.directive, [e.type for e in decision.events]


def to_screening(policy, state):
    say(policy, state, "sí", intents=("affirm",))
    assert state.stage == Stage.SCREENING


def to_location(policy, state):
    """Answer name and licence, so the next question is the location."""
    to_screening(policy, state)
    say(policy, state, "Ana López", full_name="Ana López")
    d, _ = say(policy, state, "sí", drivers_license="yes")
    assert d.ask_field == FieldName.LOCATION


def complete_until_recap(policy, state):
    to_screening(policy, state)
    say(policy, state, "Ana López", full_name="Ana López")
    say(policy, state, "sí", drivers_license="yes")
    say(policy, state, "Chamberí", location_text="Chamberí")
    say(policy, state, "media jornada", availability=["part_time"])
    say(policy, state, "por la noche", schedule=["evening"])
    say(policy, state, "2 años en Glovo", experience_months=24, experience_platforms=["glovo"])
    d, _ = say(policy, state, "el lunes", start_date=start_expr("next_weekday", weekday=0))
    return d


class TestHappyPath:
    def test_full_screening_asks_in_order_and_qualifies(self, policy, state):
        d, _ = say(policy, state, "sí", intents=("affirm",))
        assert (d.kind, d.ask_field) == ("ask", FieldName.FULL_NAME)
        d, _ = say(policy, state, "Ana López", full_name="Ana López")
        assert d.ask_field == FieldName.DRIVERS_LICENSE and d.candidate_name == "Ana"
        d, _ = say(policy, state, "sí", drivers_license="yes")
        assert d.ask_field == FieldName.LOCATION
        d, _ = say(policy, state, "Madrid", location_text="Madrid")
        assert d.ask_field == FieldName.ZONE  # optional, asked once because only the city was given
        d, _ = say(policy, state, "Chamberí", location_text="Chamberí")
        assert d.ask_field == FieldName.AVAILABILITY
        d, _ = say(policy, state, "media jornada y findes", availability=["part_time", "weekends"])
        assert d.ask_field == FieldName.SCHEDULE
        d, _ = say(policy, state, "noches", schedule=["evening"])
        assert d.ask_field == FieldName.EXPERIENCE_YEARS
        d, _ = say(policy, state, "2 años", experience_months=24)
        assert d.ask_field == FieldName.EXPERIENCE_PLATFORMS  # only because years > 0
        d, _ = say(policy, state, "Glovo y Uber", experience_platforms=["Glovo", "uber"])
        assert d.ask_field == FieldName.START_DATE
        d, _ = say(policy, state, "el lunes", start_date=start_expr("next_weekday", weekday=0))
        assert d.kind == "recap" and state.stage == Stage.CONFIRMING
        d, events = say(policy, state, "sí, todo bien", intents=("affirm",))
        assert (d.kind, d.outcome, state.stage) == ("outcome", "qualified", Stage.QUALIFIED)
        assert state.data.start_date == date(2026, 10, 26)
        assert state.data.experience_platforms == ["Glovo", "Uber Eats"]
        assert state.spanish_variant == "es-ES"
        assert "completed" in events and not state.needs_review

    def test_one_message_with_many_answers_skips_those_questions(self, policy, state):
        message = "Hola, soy Ana López, tengo carnet y vivo en Getafe"
        d, _ = say(policy, state, message, full_name="Ana López", drivers_license="yes", location_text="Getafe")
        assert state.stage == Stage.SCREENING
        assert d.ask_field == FieldName.AVAILABILITY  # zone came with Getafe
        assert state.data.zone == "Getafe" and state.data.city == "Madrid"
        assert len(d.acknowledge) == 4

    def test_experience_is_stored_in_exact_months(self, policy, state):
        # regression: "8 meses" once became 0.5 years and the recap said "6 meses"
        to_screening(policy, state)
        say(policy, state, "8 meses con Glovo", experience_months=8, experience_platforms=["Glovo"])
        assert (state.data.experience_months, state.data.experience_years) == (8, 0.67)

    def test_name_is_offered_to_the_writer_only_when_just_learned(self, policy, state):
        to_screening(policy, state)
        d, _ = say(policy, state, "Ana López", full_name="Ana López")
        assert d.candidate_name == "Ana"
        d, _ = say(policy, state, "sí", drivers_license="yes")
        assert d.candidate_name is None

    def test_no_experience_skips_platforms(self, policy, state):
        to_screening(policy, state)
        state.current_field = FieldName.EXPERIENCE_YEARS
        say(policy, state, "nunca he repartido", experience_months=0)
        assert state.field(FieldName.EXPERIENCE_PLATFORMS).status == FieldStatus.SKIPPED


class TestKnockouts:
    def test_no_licence_disqualifies_immediately_and_offers_talent_pool(self, policy, state):
        to_screening(policy, state)
        d, events = say(policy, state, "no tengo", drivers_license="no")
        assert state.stage == Stage.DISQUALIFIED
        assert state.disqualification_reason == DisqualificationReason.NO_LICENSE
        assert (d.kind, d.outcome) == ("outcome", "no_license") and "knockout" in events
        d, _ = say(policy, state, "sí, avisadme", intents=("affirm",))
        assert d.kind == "talent_pool_ack" and state.talent_pool_opt_in is True

    def test_licence_in_progress_is_its_own_reason(self, policy, state):
        to_screening(policy, state)
        d, _ = say(policy, state, "me lo estoy sacando", drivers_license="in_progress")
        assert d.outcome == "license_in_progress"

    def test_out_of_area_uses_the_candidates_words(self, policy, state):
        to_screening(policy, state)
        d, _ = say(policy, state, "Vivo en Toledo", location_text="Toledo", location_outside_service_area=True)
        assert (state.stage, d.outcome, d.outcome_place) == (Stage.DISQUALIFIED, "out_of_area", "Toledo")
        assert state.data.in_service_area is False

    def test_place_the_rules_dont_know_is_accepted_if_the_model_maps_it_to_a_city(self, policy, state):
        to_screening(policy, state)
        say(policy, state, "Pueblo Nuevo", location_text="Pueblo Nuevo", location_city_id="madrid", location_zone="Pueblo Nuevo")
        assert (state.data.city_id, state.data.zone) == ("madrid", "Pueblo Nuevo")

    def test_a_model_city_outside_the_config_is_ignored(self, policy, state):
        to_location(policy, state)
        d, _ = say(policy, state, "Toledo", location_text="Toledo", location_city_id="toledo")
        assert state.data.city_id is None
        assert (d.ask_field, d.ask_issue) == (FieldName.LOCATION, "location_unknown")

    def test_ambiguous_zone_asks_with_options(self, policy, state):
        to_location(policy, state)
        d, _ = say(policy, state, "en el centro", location_text="centro")
        assert (d.ask_field, d.ask_issue) == (FieldName.LOCATION, "location_ambiguous")
        assert "Centro (Madrid)" in d.ask_options


class TestValidationAndLoops:
    def test_invalid_answer_is_asked_again_with_the_reason(self, policy, state):
        to_location(policy, state)
        d, _ = say(policy, state, "Vivo en Bilbao", location_text="Bilbao")
        say(policy, state, "Deusto", location_text="Deusto")
        say(policy, state, "full time", availability=["full_time"])
        say(policy, state, "mañanas", schedule=["morning"])
        d, _ = say(policy, state, "nunca", experience_months=0)
        assert d.ask_field == FieldName.START_DATE
        d, _ = say(policy, state, "el 1 de octubre", start_date=start_expr("exact_date", exact_date="2026-10-01"))
        assert (d.ask_field, d.ask_issue) == (FieldName.START_DATE, "start_date_past")

    def test_gives_up_after_two_failed_attempts_and_flags(self, policy, state):
        to_screening(policy, state)
        say(policy, state, "Ana López", full_name="Ana López")  # now asking the licence
        say(policy, state, "más o menos", intents=("other",))
        d, events = say(policy, state, "bueno, depende", intents=("other",))
        assert state.field(FieldName.DRIVERS_LICENSE).status == FieldStatus.UNCLEAR
        assert "field_unclear" in events and d.ask_field == FieldName.LOCATION  # moved on

    def test_unclear_knockout_field_ends_in_review_not_qualified(self, policy, state):
        complete_until_recap(policy, state)
        state.field(FieldName.DRIVERS_LICENSE).status = FieldStatus.UNCLEAR
        d, _ = say(policy, state, "sí", intents=("affirm",))
        assert (state.stage, d.outcome) == (Stage.NEEDS_REVIEW, "needs_review")

    def test_a_question_is_not_a_failed_attempt(self, policy, state):
        to_screening(policy, state)
        say(policy, state, "Ana López", full_name="Ana López")
        d, events = say(policy, state, "¿cuánto se cobra?", intents=("question",), question="¿cuánto se cobra?", faq_id="pay")
        assert state.field(FieldName.DRIVERS_LICENSE).failed_attempts == 0
        assert d.answer.faq_id == "pay" and d.ask_field == FieldName.DRIVERS_LICENSE
        assert "question_answered" in events

    def test_unknown_questions_are_never_improvised_and_are_logged(self, policy, state):
        to_screening(policy, state)
        d, events = say(policy, state, "¿hay parking?", intents=("question",), question="¿hay parking?")
        assert d.answer.answer is None and state.pending_questions == ["¿hay parking?"]
        assert "question_unanswered" in events

    def test_first_name_only_is_kept_and_surname_requested(self, policy, state):
        to_screening(policy, state)
        d, _ = say(policy, state, "Ana", full_name="Ana")
        assert state.data.full_name == "Ana"
        assert (d.ask_field, d.ask_issue) == (FieldName.FULL_NAME, "name_needs_surname")

    def test_choosing_the_city_after_an_ambiguous_zone_keeps_the_zone(self, policy, state):
        to_location(policy, state)
        say(policy, state, "en el centro", location_text="centro")
        say(policy, state, "Madrid", location_text="Madrid")
        assert (state.data.city, state.data.zone) == ("Madrid", "Centro")

    def test_optional_zone_is_never_asked_twice(self, policy, state):
        to_location(policy, state)
        say(policy, state, "Madrid", location_text="Madrid")
        d, _ = say(policy, state, "media jornada", availability=["part_time"])  # ignores the zone question
        assert state.field(FieldName.ZONE).status == FieldStatus.SKIPPED
        assert d.ask_field == FieldName.SCHEDULE

    def test_optional_zone_is_skipped_if_they_dont_care(self, policy, state):
        to_location(policy, state)
        d, _ = say(policy, state, "Madrid", location_text="Madrid")
        assert d.ask_field == FieldName.ZONE
        d, _ = say(policy, state, "me da igual", intents=("other",))
        assert state.field(FieldName.ZONE).status == FieldStatus.SKIPPED
        assert d.ask_field == FieldName.AVAILABILITY


class TestGuardrails:
    def test_values_without_supporting_words_are_discarded(self, policy, state):
        to_screening(policy, state)
        d, events = say(policy, state, "hola", full_name="Pedro Pérez", quotes={"full_name": "me llamo Pedro Pérez"})
        assert state.data.full_name is None and "ungrounded_value" in events

    def test_abuse_gets_one_warning_then_the_conversation_ends(self, policy, state):
        to_screening(policy, state)
        d, _ = say(policy, state, "...", intents=("abuse",))
        assert "abuse_warning" in d.notes and state.stage == Stage.SCREENING
        d, _ = say(policy, state, "...", intents=("abuse",))
        assert (state.stage, d.kind) == (Stage.TERMINATED, "silent")
        d, _ = say(policy, state, "hola?", intents=("smalltalk",))
        assert d.kind == "silent"

    def test_human_request_is_flagged_and_the_screening_continues(self, policy, state):
        to_screening(policy, state)
        d, _ = say(policy, state, "quiero hablar con una persona", intents=("human_request",))
        assert "human_request" in d.notes and d.kind == "ask" and state.needs_review


class TestConversationControl:
    def test_opt_out_withdraws_and_the_candidate_can_come_back(self, policy, state):
        to_screening(policy, state)
        d, _ = say(policy, state, "ya no me interesa", intents=("opt_out",))
        assert (state.stage, d.outcome) == (Stage.WITHDRAWN, "withdrawn")
        d, _ = say(policy, state, "perdona, sí quiero seguir", intents=("affirm",))
        assert state.stage == Stage.SCREENING and "resume" in d.notes and d.kind == "ask"

    def test_no_at_the_intro_withdraws(self, policy, state):
        say(policy, state, "no", intents=("deny",))
        assert state.stage == Stage.WITHDRAWN

    def test_postpone_keeps_the_stage(self, policy, state):
        to_screening(policy, state)
        d, _ = say(policy, state, "ahora no puedo, luego te escribo", intents=("postpone",))
        assert d.kind == "postpone_ack" and state.stage == Stage.SCREENING


class TestLanguage:
    def test_short_neutral_messages_never_switch_language(self, policy, state):
        say(policy, state, "ok", intents=("affirm",), language="en", language_is_clear=False)
        assert state.language == "es"

    def test_clear_english_switches(self, policy, state):
        d, events = say(policy, state, "Yes, let's do it", intents=("affirm",), language="en", language_is_clear=True)
        assert state.language == "en" and d.locale == "en" and "language_switched" in events

    def test_model_mistake_is_vetoed_by_the_second_opinion(self, policy, state):
        # regression: Haiku labelled "full time y part time" as clear English
        to_screening(policy, state)
        say(policy, state, "full time y part time", availability=["full_time", "part_time"], language="en", language_is_clear=True)
        assert state.language == "es"

    def test_city_sets_the_spanish_variant(self, policy, state):
        to_screening(policy, state)
        d, _ = say(policy, state, "Monterrey", location_text="Monterrey")
        assert state.spanish_variant == "es-MX" and d.locale == "es-MX"


class TestRecapAndCorrections:
    def test_correction_at_recap_updates_and_recaps_again(self, policy, state):
        complete_until_recap(policy, state)
        d, events = say(policy, state, "no, vivo en Getafe", intents=("deny", "correction"), location_text="Getafe")
        assert d.kind == "recap" and state.data.zone == "Getafe" and "field_corrected" in events
        d, _ = say(policy, state, "ahora sí", intents=("affirm",))
        assert state.stage == Stage.QUALIFIED

    def test_naming_the_wrong_detail_reopens_that_question(self, policy, state):
        complete_until_recap(policy, state)
        d, events = say(policy, state, "la fecha está mal", intents=("deny", "correction"), correction_target="start_date")
        assert (d.kind, d.ask_field, state.stage) == ("ask", FieldName.START_DATE, Stage.SCREENING)
        assert "field_reopened" in events

    def test_bare_no_at_recap_asks_what_to_fix(self, policy, state):
        complete_until_recap(policy, state)
        d, _ = say(policy, state, "no", intents=("deny",))
        assert d.kind == "ask_correction"

    def test_correction_that_breaks_a_knockout_disqualifies(self, policy, state):
        complete_until_recap(policy, state)
        say(policy, state, "en realidad no tengo carnet", intents=("correction",), drivers_license="no")
        assert state.stage == Stage.DISQUALIFIED


class TestAfterTheEnd:
    def finish(self, policy, state):
        to_screening(policy, state)
        say(policy, state, "no tengo", drivers_license="no")
        say(policy, state, "sí", intents=("affirm",))  # talent pool
        assert state.talent_pool_opt_in is True

    def test_small_talk_gets_one_courtesy_reply_then_silence(self, policy, state):
        # regression: "bye" and "ok" after the end each got a reply, forever
        self.finish(policy, state)
        d, _ = say(policy, state, "bye", intents=("smalltalk",))
        assert d.kind == "closed_followup"
        d, events = say(policy, state, "ok", intents=("affirm",))
        assert d.kind == "silent" and "ignored_after_close" in events

    def test_questions_after_the_end_are_always_answered(self, policy, state):
        self.finish(policy, state)
        say(policy, state, "gracias", intents=("smalltalk",))
        d, _ = say(policy, state, "¿cuándo me escribís?", intents=("question",), question="¿cuándo me escribís?", faq_id="process")
        assert d.kind == "closed_followup" and d.answer.faq_id == "process"

    def test_new_information_after_the_end_is_flagged_for_a_recruiter(self, policy, state):
        self.finish(policy, state)
        d, events = say(policy, state, "¡ya tengo el carnet!", drivers_license="yes")
        assert "update_after_close" in d.notes and state.needs_review
        assert state.stage == Stage.DISQUALIFIED  # a human re-evaluates, the bot doesn't


class TestLanguageLoanwords:
    # regression: "full time" alone (a common loanword in Spain) switched the agent to English
    def test_short_loanword_answers_never_switch(self, policy, state):
        to_screening(policy, state)
        say(policy, state, "full time", availability=["full_time"], language="en", language_is_clear=True)
        assert state.language == "es"

    def test_a_confirmed_english_message_switches(self, policy, state):
        say(policy, state, "Hi! Can we do this in English?", intents=("affirm",), language="en", language_is_clear=True)
        assert state.language == "en"

    def test_long_mixed_message_without_signal_lets_the_model_decide(self, policy, state):
        to_screening(policy, state)
        say(policy, state, "Sí, I have license de moto", drivers_license="yes", language="en", language_is_clear=True)
        assert state.language == "en"
