"""The voice channel (ADR 0010): the same engine and API, spoken."""

from __future__ import annotations

import httpx
from fastapi.testclient import TestClient

from conftest import analysis
from screener.api.app import create_app
from screener.channels.voice import ElevenLabsVoice, speakable
from screener.config import VoiceSettings
from screener.engine.scheduling import match_choice
from test_scheduling import MADRID, TestMatchChoice


# ------------------------------------------------------------------ what a voice reads
class TestSpeakable:
    def test_interview_times_are_said_as_people_say_them(self):
        text = "Elige día y hora:\n1) miércoles 21/10 a las 16:00\n2) jueves 22/10 a las 13:30"
        spoken = speakable(text, "es-ES")
        assert "opción 1: miércoles 21 de octubre a las cuatro de la tarde" in spoken
        assert "jueves 22 de octubre a la una y media de la tarde" in spoken

    def test_english(self):
        assert speakable("Wednesday 21/10 at 16:00", "en") == "Wednesday 21 October at 4 pm"

    def test_no_emojis_bullets_or_slashes(self):
        spoken = speakable("¡Hola! \U0001F44B Soy Sofía, para repartidor/a.\n• Nombre: Ana\n• Inicio: lunes 26/10", "es")
        assert "\U0001F44B" not in spoken and "•" not in spoken and "/" not in spoken
        assert "repartidor o repartidora" in spoken and "Nombre: Ana. Inicio: lunes 26 de octubre" in spoken

    def test_quarter_to(self):
        assert speakable("a las 21:45", "es-ES") == "a las diez menos cuarto de la noche"


# ------------------------------------------------------------------ the voice itself
class TestElevenLabsVoice:
    def test_without_a_key_nothing_is_sent(self, monkeypatch):
        monkeypatch.setattr(httpx, "post", lambda *a, **k: (_ for _ in ()).throw(AssertionError("no call expected")))
        voice = ElevenLabsVoice(VoiceSettings(voices={"default": "v"}), api_key="")
        assert not voice.available and voice.synthesize("hola", "es-ES") is None

    def test_a_failure_falls_back_instead_of_breaking(self, monkeypatch):
        def fail(*a, **k):
            raise httpx.ConnectError("down")
        monkeypatch.setattr(httpx, "post", fail)
        assert ElevenLabsVoice(VoiceSettings(voices={"default": "v"}), api_key="k").synthesize("hola", "es-ES") is None

    def test_the_voice_follows_the_locale(self):
        voice = ElevenLabsVoice(VoiceSettings(voices={"es-MX": "mx", "es": "es", "default": "d"}), api_key="k")
        assert (voice.voice_for("es-MX"), voice.voice_for("es-ES"), voice.voice_for("en")) == ("mx", "es", "d")


# ------------------------------------------------------------------ the same engine, spoken
def test_a_voice_conversation_tells_the_writer_it_is_spoken(make_engine):
    class Recorder:
        def __init__(self):
            self.directives = []

        def compose(self, request):
            self.directives.append(request.directive)
            return "Encantada. ¿Tienes carnet de conducir?"

    writer = Recorder()
    engine = make_engine([analysis("Ana López", full_name="Ana López")], responder=writer)
    cid = engine.start(channel="voice").conversation_id
    result = engine.handle(cid, "Ana López")
    assert writer.directives[-1].voice and result.locale == "es"


def test_a_time_chosen_by_voice():
    slots = TestMatchChoice.SLOTS
    assert match_choice("la uno", slots, MADRID, "es-ES", None) == 0
    assert match_choice("la dos", slots, MADRID, "es-ES", None) == 1


def test_the_speech_endpoint_falls_back_to_the_browser_voice(make_engine, monkeypatch):
    monkeypatch.delenv("ELEVENLABS_API_KEY", raising=False)
    engine = make_engine([])
    with TestClient(create_app(engine=engine, scheduler=False)) as client:
        cid = client.post("/api/conversations", json={"channel": "voice"}).json()["conversation_id"]
        assert client.get("/api/voice").json() == {"provider": "browser"}
        body = client.post("/api/voice/speech", json={"conversation_id": cid, "text": "¡Hola! \U0001F44B el 21/10"}).json()
        assert body == {"provider": "browser", "speech": "¡Hola! el 21 de octubre", "locale": "es"}
        assert client.post("/api/voice/speech", json={"conversation_id": "nope", "text": "hola"}).status_code == 404
