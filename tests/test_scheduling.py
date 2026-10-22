"""Interview booking: the times offered, reading the candidate's choice, and the whole flow."""

from __future__ import annotations

from datetime import datetime

from conftest import NOW, analysis
from screener.domain.models import InterviewStatus, Schedule, Stage
from screener.engine.scheduling import candidate_slots, match_choice, slot_label, slot_long
from test_api import TEXTS, full_screening

MADRID = "Europe/Madrid"


def utc(y, m, d, h, mi=0):
    return datetime(y, m, d, h, mi)


# ------------------------------------------------------------------ which times
class TestCandidateSlots:
    def test_after_the_lead_time_one_per_day_earliest_first(self, config):
        # Tue 20/10 12:00 in Madrid + 18 h: the first window is Wednesday morning
        slots = candidate_slots(config.scheduling, MADRID, NOW, [], set())
        assert slots == [utc(2026, 10, 21, 8), utc(2026, 10, 22, 8), utc(2026, 10, 23, 8)]  # 10:00 CEST

    def test_the_preferred_shift_comes_first(self, config):
        slots = candidate_slots(config.scheduling, MADRID, NOW, [Schedule.AFTERNOON], set())
        assert [s.hour for s in slots] == [14, 14, 14]  # 16:00 in Madrid

    def test_taken_times_and_weekends_are_skipped(self, config):
        taken = {utc(2026, 10, 21, 8)}
        slots = candidate_slots(config.scheduling, MADRID, NOW, [], taken, count=5)
        assert utc(2026, 10, 21, 8) not in slots
        assert all(s.weekday() < 5 for s in slots)

    def test_local_time_survives_the_daylight_saving_change(self, config):
        # Spain leaves summer time on Sun 25/10: Monday 26/10 at 10:00 is 09:00 UTC, not 08:00
        friday_evening = utc(2026, 10, 23, 17)
        slots = candidate_slots(config.scheduling, MADRID, friday_evening, [], set())
        assert slots[0] == utc(2026, 10, 26, 9)

    def test_mexico_city_uses_its_own_clock(self, config):
        slots = candidate_slots(config.scheduling, "America/Mexico_City", NOW, [], set())
        assert slots[0] == utc(2026, 10, 21, 16)  # 10:00 in Mexico City (UTC-6)


# ------------------------------------------------------------------ showing them
def test_labels_are_exact_and_localised():
    slot = utc(2026, 10, 27, 15)  # Tuesday 16:00 in Madrid (winter time)
    assert slot_label(slot, MADRID, "es-ES") == "mar 27/10 · 16:00"
    assert slot_long(slot, MADRID, "es-ES") == "martes 27/10 a las 16:00"
    assert slot_label(slot, MADRID, "en") == "Tue 27 Oct · 16:00"
    assert slot_long(slot, MADRID, "en") == "Tuesday 27 Oct at 16:00"


# ------------------------------------------------------------------ reading the choice
class TestMatchChoice:
    SLOTS = [utc(2026, 10, 21, 14), utc(2026, 10, 22, 8), utc(2026, 10, 23, 14, 30)]  # Wed 16:00, Thu 10:00, Fri 16:30

    def pick(self, text, model=None):
        return match_choice(text, self.SLOTS, MADRID, "es-ES", model)

    def test_the_button_text(self):
        assert self.pick("jue 22/10 · 10:00") == 1

    def test_the_option_number_or_an_ordinal(self):
        assert self.pick("2") == 1 and self.pick("la 3") == 2
        assert self.pick("la primera") == 0 and self.pick("me quedo con la última") == 2

    def test_a_weekday_a_date_or_a_time(self):
        assert self.pick("el viernes") == 2
        assert self.pick("el 22/10 me va bien") == 1
        assert self.pick("a las 4") == 0             # "a las 4" for an interview means 16:00
        assert self.pick("16:30 perfecto") == 2

    def test_weekday_and_time_together(self):
        assert self.pick("el miércoles a las 16:00") == 0

    def test_no_guess_when_it_is_ambiguous_or_absent(self):
        assert self.pick("cualquiera") is None
        assert self.pick("a las 10 o a las 4") is None   # two different options

    def test_the_model_reading_is_only_a_fallback(self):
        assert self.pick("esa del medio me viene genial", model=2) == 1
        assert self.pick("el viernes", model=1) == 2      # the rules win when they are sure
        assert self.pick("vale", model=7) is None          # out of range: ignored


# ------------------------------------------------------------------ the whole flow
def qualify(engine):
    cid = engine.start().conversation_id
    for text in TEXTS:
        result = engine.handle(cid, text)
    return cid, result


class TestBookingFlow:
    def test_qualifying_offers_times_with_buttons(self, make_engine):
        engine = make_engine(full_screening())
        cid, result = qualify(engine)
        assert result.stage == Stage.QUALIFIED and len(result.messages) == 2
        offer = result.messages[1]
        assert "1) miércoles 21/10 a las 16:00" in offer.text  # "tardes": afternoon times first
        assert offer.quick_replies[-1] == "Ninguno me va bien" and len(offer.quick_replies) == 4
        state = engine.repo.get_state(cid)
        assert state.interview.status == InterviewStatus.OFFERED and state.interview.place.startswith("Grupo Sazón")

    def test_choosing_a_time_books_it(self, make_engine):
        engine = make_engine(full_screening() + [analysis("el jueves", intents=("provide_info",))])
        cid, _ = qualify(engine)
        result = engine.handle(cid, "el jueves")
        state = engine.repo.get_state(cid)
        assert state.interview.status == InterviewStatus.BOOKED and state.interview.slot == utc(2026, 10, 22, 14)
        assert "jueves 22/10 a las 16:00" in result.messages[0].text and "Trae tu" in result.messages[0].text
        assert engine.repo.taken_interview_slots("madrid") == {utc(2026, 10, 22, 14)}
        assert "interview_booked" in result.event_types

    def test_none_fits_twice_hands_over_to_a_recruiter(self, make_engine):
        engine = make_engine(full_screening() + [analysis("ninguno", intents=("deny",))] * 2)
        cid, _ = qualify(engine)
        second = engine.handle(cid, "Ninguno me va bien")
        state = engine.repo.get_state(cid)
        assert state.interview.offers == 2 and "otras opciones" in second.messages[0].text
        assert not set(state.interview.offered) & set(state.interview.history[:3])  # new times, not the same ones
        third = engine.handle(cid, "Ninguno me va bien")
        state = engine.repo.get_state(cid)
        assert state.interview.status == InterviewStatus.HANDED_OFF and "interview_handoff" in third.event_types
        assert any(f.code == "scheduling_needed" for f in state.flags) and state.needs_review

    def test_a_booked_interview_can_be_moved(self, make_engine):
        engine = make_engine(full_screening() + [analysis("1"), analysis("no puedo ir, ¿lo cambiamos?")])
        cid, _ = qualify(engine)
        engine.handle(cid, "1")
        result = engine.handle(cid, "no puedo ir, ¿lo cambiamos?")
        state = engine.repo.get_state(cid)
        assert "interview_cancelled" in result.event_types and state.interview.status == InterviewStatus.OFFERED
        assert engine.repo.taken_interview_slots("madrid") == set()  # the old time is free again

    def test_a_time_taken_by_someone_else_meanwhile_is_offered_again(self, make_engine):
        script = full_screening() + full_screening() + [analysis("2"), analysis("2")]
        engine = make_engine(script)
        first, _ = qualify(engine)
        second, _ = qualify(engine)          # both were offered the same three times
        engine.handle(first, "2")            # Thursday 16:00 goes to the first candidate
        result = engine.handle(second, "2")  # the second picks it too
        state = engine.repo.get_state(second)
        assert "interview_slot_taken" in result.event_types and "acaba de ocupar" in result.messages[0].text
        assert utc(2026, 10, 22, 14) not in state.interview.offered
        assert engine.repo.taken_interview_slots("madrid") == {utc(2026, 10, 22, 14)}  # never double-booked

    def test_an_unclear_reply_shows_the_same_times_once(self, make_engine):
        engine = make_engine(full_screening() + [analysis("ok", intents=("affirm",))] * 2)
        cid, first = qualify(engine)
        result = engine.handle(cid, "ok")
        assert "¿Cuál de estos horarios" in result.messages[0].text
        assert result.messages[0].quick_replies == first.messages[1].quick_replies
        again = engine.handle(cid, "ok")
        assert all("¿Cuál de estos horarios" not in m.text for m in again.messages)  # no ping-pong

    def test_the_model_choice_is_used_when_the_rules_cannot_tell(self, make_engine):
        engine = make_engine(full_screening() + [analysis("esa del medio me viene genial", chosen_option=2)])
        cid, _ = qualify(engine)
        engine.handle(cid, "esa del medio me viene genial")
        assert engine.repo.get_state(cid).interview.slot == utc(2026, 10, 22, 14)

    def test_erasing_the_candidate_frees_the_time(self, make_engine):
        engine = make_engine(full_screening() + [analysis("1")])
        cid, _ = qualify(engine)
        engine.handle(cid, "1")
        engine.repo.delete_conversation(cid)
        assert engine.repo.taken_interview_slots("madrid") == set()

def test_recruiters_see_the_booking_and_analytics_count_it(make_engine):
    from screener.analytics import compute
    from screener.views import build_rows

    engine = make_engine(full_screening() + [analysis("1")])
    cid, _ = qualify(engine)
    engine.handle(cid, "1")
    row = build_rows(engine.repo, now=NOW)[0]
    assert (row.interview_status, row.interview_at, row.interview_timezone) == ("booked", utc(2026, 10, 21, 14), MADRID)
    stats = compute(engine.repo, now=NOW)
    assert (stats.interviews_offered, stats.interviews_booked, stats.booking_rate) == (1, 1, 1.0)
    assert stats.funnel[-1].step == "Interview booked"
    assert stats.template_fallback_rate == 0  # booking messages are templates by design, not fallbacks

