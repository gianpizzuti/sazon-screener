"""Re-engagement: timing, quiet hours per timezone, spacing, abandonment, recovery."""

from datetime import datetime, timedelta

import pytest

from conftest import analysis
from screener.analytics import compute
from screener.views import build_rows

T0 = datetime(2026, 10, 20, 10, 0)  # UTC: 12:00 in Madrid, 04:00 in Mexico City


@pytest.fixture
def timed(make_engine):
    """An engine whose clock the test moves."""
    def _make(script):
        engine = make_engine(script)
        clock = {"now": T0}
        engine.clock = lambda: clock["now"]
        return engine, clock
    return _make


def screening_until_licence(timed):
    engine, clock = timed([analysis("sí", intents=("affirm",)), analysis("Ana López", full_name="Ana López")])
    cid = engine.start().conversation_id
    engine.handle(cid, "sí")
    engine.handle(cid, "Ana López")  # asked about the licence, then silence
    return engine, clock, cid


def run_hourly(engine, clock, hours):
    sent = []
    for _ in range(hours):
        clock["now"] += timedelta(hours=1)
        sent += [(clock["now"], a) for a in engine.run_followups()]
    return sent


def test_first_followup_after_two_hours_repeats_the_pending_question(timed):
    engine, clock, cid = screening_until_licence(timed)
    clock["now"] = T0 + timedelta(hours=1, minutes=59)
    assert engine.run_followups() == []
    clock["now"] = T0 + timedelta(hours=2)
    [sent] = engine.run_followups()
    assert sent["attempt"] == 1 and sent["text"].startswith("¿Seguimos, Ana? Solo quedan 6 preguntas.") and "carnet de conducir" in sent["text"]
    last = engine.repo.messages(cid)[-1]
    assert last.meta["kind"] == "followup" and last.meta["whatsapp_template_required"] is False  # within 24 h


def test_three_spaced_followups_then_abandoned_at_the_pending_question(timed):
    engine, clock, cid = screening_until_licence(timed)
    sent = run_hourly(engine, clock, 100)
    followups = [(t, a) for t, a in sent if a["action"] == "followup"]
    assert [t - T0 for t, _ in followups] == [timedelta(hours=2), timedelta(hours=24), timedelta(hours=72)]
    assert [a["attempt"] for _, a in followups] == [1, 2, 3]
    assert [t - T0 for t, a in sent if a["action"] == "abandoned"] == [timedelta(hours=96)]
    assert build_rows(engine.repo, now=clock["now"])[0].status == "abandoned"
    stats = compute(engine.repo, now=clock["now"])
    assert stats.drop_off == {"License": 1} and stats.followups_sent == 3
    later = [m for m in engine.repo.messages(cid) if m.meta.get("kind") == "followup"]
    assert later[1].meta["whatsapp_template_required"] is True  # > 24 h since the candidate wrote


def test_no_followups_during_the_candidates_night(timed):
    engine, clock, cid = screening_until_licence(timed)
    state = engine.repo.get_state(cid)
    state.last_candidate_message_at = datetime(2026, 10, 20, 18, 30)  # 20:30 in Madrid
    engine.repo.save_turn(state, [], [])
    clock["now"] = datetime(2026, 10, 20, 20, 30)  # due, but 22:30 in Madrid
    assert engine.run_followups() == []
    clock["now"] = datetime(2026, 10, 21, 7, 0)  # 09:00 in Madrid
    assert len(engine.run_followups()) == 1


def test_quiet_hours_follow_the_candidates_timezone(timed):
    engine, clock = timed([analysis("CDMX", location_text="CDMX")])
    cid = engine.start().conversation_id
    clock["now"] = datetime(2026, 10, 20, 19, 0)
    engine.handle(cid, "CDMX")  # city known: Mexico City
    clock["now"] = datetime(2026, 10, 20, 21, 0)  # 23:00 in Madrid, but 15:00 in Mexico City
    assert len(engine.run_followups()) == 1


def test_a_reply_after_a_followup_resumes_and_counts_as_recovered(timed):
    engine, clock, cid = screening_until_licence(timed)
    engine.understander.script.append(analysis("sí, tengo", drivers_license="yes"))
    run_hourly(engine, clock, 30)  # two follow-ups
    result = engine.handle(cid, "sí, tengo")
    assert "resumed" in result.event_types and result.data.has_drivers_license
    state = engine.repo.get_state(cid)
    assert (state.followups_sent, state.abandoned_at) == (0, None)
    stats = compute(engine.repo, now=clock["now"])
    assert (stats.candidates_nudged, stats.candidates_recovered, stats.recovery_rate) == (1, 1, 1.0)
    assert stats.recovered_by_followup == {"After follow-up 2": 1}


def test_candidates_who_never_answered_get_the_intro_followup(timed):
    engine, clock = timed([])
    engine.start()
    clock["now"] = T0 + timedelta(hours=2)
    [sent] = engine.run_followups()
    assert "Tu solicitud como repartidor/a" in sent["text"]


def test_finished_conversations_are_never_nudged(timed):
    engine, clock = timed([analysis("no", intents=("deny",))])
    cid = engine.start().conversation_id
    engine.handle(cid, "no")  # withdrawn at the intro
    run_hourly(engine, clock, 100)
    assert not any(m.meta.get("kind") == "followup" for m in engine.repo.messages(cid))
