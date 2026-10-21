"""Engine wiring: persistence, degraded modes, never crashing."""

from conftest import FailingResponder, LongResponder, analysis
from screener.domain.models import FieldName, Stage
from screener.llm.interfaces import LLMError


def test_start_sends_the_fixed_greeting_and_persists_it(make_engine):
    engine = make_engine([])
    result = engine.start(channel="test")
    assert "asistente virtual (IA)" in result.messages[0].text  # AI disclosure
    assert result.messages[0].quick_replies
    assert [m.role for m in engine.repo.transcript(result.conversation_id)] == ["agent"]


def test_a_turn_persists_messages_state_and_events(make_engine):
    engine = make_engine([analysis("sí", intents=("affirm",)), analysis("Ana López", full_name="Ana López")])
    cid = engine.start().conversation_id
    engine.handle(cid, "sí")
    result = engine.handle(cid, "Ana López")
    assert result.data.full_name == "Ana López"
    assert [m.role for m in engine.repo.transcript(cid)] == ["agent", "candidate", "agent", "candidate", "agent"]
    assert engine.repo.get_state(cid).current_field == FieldName.DRIVERS_LICENSE
    event_types = [e.type for e in engine.repo.events(cid)]
    assert "conversation_started" in event_types and "field_valid" in event_types
    candidate_msg = engine.repo.messages(cid)[3]
    assert candidate_msg.meta["analysis"]["extracted"]["full_name"] == "Ana López"  # the "why" is stored


def test_understanding_failure_apologises_and_does_not_count_an_attempt(make_engine):
    engine = make_engine([analysis("sí", intents=("affirm",)), LLMError("timeout")])
    cid = engine.start().conversation_id
    engine.handle(cid, "sí")
    result = engine.handle(cid, "Ana López")
    assert "problema técnico" in result.messages[0].text
    state = engine.repo.get_state(cid)
    assert state.field(FieldName.FULL_NAME).failed_attempts == 0
    assert any(e.type == "llm_error" for e in engine.repo.events(cid))


def test_responder_failure_falls_back_to_templates(make_engine):
    engine = make_engine([analysis("sí", intents=("affirm",))], responder=FailingResponder())
    cid = engine.start().conversation_id
    result = engine.handle(cid, "sí")
    assert "¿Cómo te llamas?" in result.messages[0].text
    assert engine.repo.messages(cid)[-1].meta["source"] == "template"


def test_overlong_draft_is_retried_then_replaced(make_engine):
    engine = make_engine([analysis("sí", intents=("affirm",))], responder=LongResponder())
    cid = engine.start().conversation_id
    result = engine.handle(cid, "sí")
    assert len(result.messages[0].text) <= 350
    rejections = [e for e in engine.repo.events(cid) if e.type == "guard_rejected"]
    assert len(rejections) == 2  # first draft + retry, then template


def test_recap_is_rendered_from_state_with_confirm_buttons(make_engine):
    from conftest import start_expr

    script = [
        analysis("Soy Ana López, tengo carnet y reparto en Getafe", full_name="Ana López", drivers_license="yes", location_text="Getafe"),
        analysis("media jornada", availability=["part_time"]),
        analysis("tardes", schedule=["afternoon"]),
        analysis("nunca", experience_months=0),
        analysis("ya", start_date=start_expr("immediate")),
    ]
    engine = make_engine(script)
    cid = engine.start().conversation_id
    for text in ["Soy Ana López, tengo carnet y reparto en Getafe", "media jornada", "tardes", "nunca"]:
        engine.handle(cid, text)
    result = engine.handle(cid, "ya")
    recap = result.messages[-1]
    assert result.stage == Stage.CONFIRMING
    assert "Madrid (Getafe)" in recap.text and "Sin experiencia previa" in recap.text
    assert "lo antes posible" in recap.text and recap.quick_replies


def test_recap_shows_months_exactly(make_engine, config):
    from screener.domain.models import ConversationState
    from screener.engine.recap import render_recap
    from conftest import TODAY

    state = ConversationState(id="r", client_id="x", channel="t")
    state.data.experience_months, state.data.experience_platforms = 8, ["Glovo"]
    assert "8 meses (Glovo)" in render_recap(state, config.copy_, TODAY)


def test_recap_says_tomorrow_next_to_tomorrows_date(config):
    from datetime import timedelta

    from screener.domain.models import ConversationState
    from screener.engine.recap import render_recap
    from conftest import TODAY

    state = ConversationState(id="r", client_id="x", channel="t")
    state.data.start_date = TODAY + timedelta(days=1)
    assert "mañana, miércoles 21/10" in render_recap(state, config.copy_, TODAY)


def test_recap_shows_the_licence_type_and_says_when_it_was_updated(config):
    from screener.domain.models import ConversationState, LicenseStatus, LicenseType
    from screener.engine.recap import render_recap
    from conftest import TODAY

    state = ConversationState(id="r", client_id="x", channel="t")
    state.data.has_drivers_license, state.data.license_status = True, LicenseStatus.YES
    state.data.license_type = LicenseType.MOTORBIKE
    text = render_recap(state, config.copy_, TODAY, updated=True)
    assert "Sí (moto)" in text and text.startswith("Listo, he actualizado tus datos")


def test_the_applications_country_sets_the_spanish_variant_from_the_first_message(make_engine):
    engine = make_engine([])
    result = engine.start(country="MX")
    assert engine.repo.get_state(result.conversation_id).locale == "es-MX"
    assert engine.repo.get_state(engine.start().conversation_id).locale == "es"  # unknown: neutral Spanish


def test_empty_messages_are_ignored(make_engine):
    engine = make_engine([])
    cid = engine.start().conversation_id
    assert engine.handle(cid, "   ").messages == []


def test_summary_failure_saves_a_fallback(make_engine):
    class BrokenSummarizer:
        def summarize(self, state, transcript):
            raise LLMError("down")

    engine = make_engine([analysis("no", intents=("deny",))], summarizer=BrokenSummarizer())
    cid = engine.start().conversation_id
    engine.handle(cid, "no")
    summary = engine.summarize(cid)
    assert summary["source"] == "template" and engine.repo.get_summary(cid) == summary



def test_recap_formats_years_and_decimals_for_the_locale(config):
    from datetime import date
    from screener.domain.models import ConversationState
    from screener.engine.recap import render_recap
    from conftest import TODAY

    state = ConversationState(id="r", client_id="x", channel="t")
    state.data.experience_months, state.data.start_date = 18, date(2027, 1, 11)
    text = render_recap(state, config.copy_, TODAY)
    assert "1,5 años" in text and "11/01/2027" in text
