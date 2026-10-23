"""The voice channel: Sofía's messages made speakable, and the voice that says them (ADR 0011).

Voice is one more channel on the same API (ADR 0008). The engine decides and writes as it does for
chat, told only that the conversation is spoken (no emojis, options said in words). This module turns
a chat message into text a voice can read ("21/10 a las 16:00" -> "21 de octubre a las cuatro de la
tarde", no bullets or emojis) and synthesises it with ElevenLabs when a key is configured. Without a
key, or if ElevenLabs fails, the browser's own voice reads the same text, so a demo never goes silent.

Only Sofía's words are sent to ElevenLabs: the candidate's voice is transcribed in their browser.
"""

from __future__ import annotations

import logging
import os
import re

import httpx

from screener.config import VoiceSettings

log = logging.getLogger(__name__)

TTS_URL = "https://api.elevenlabs.io/v1/text-to-speech/{voice}"
MAX_CHARS = 2000

_EMOJI = re.compile("[\U0001F000-\U0001FAFF☀-➿️‍]")
_DATE = re.compile(r"\b(\d{1,2})/(\d{1,2})\b")
_TIME = re.compile(r"\b(?:(las|la)\s+)?(\d{1,2}):(\d{2})\b", re.IGNORECASE)
_OPTION = re.compile(r"^\s*(\d)\)\s*", re.MULTILINE)
_BULLET = re.compile(r"\n\s*[•·-]\s*")
_SLASH_GENDER = re.compile(r"\b(\w+)/a\b")  # "repartidor/a", "interesado/a"

MONTHS = {
    "es": ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre",
           "noviembre", "diciembre"],
    "en": ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
           "November", "December"],
}
HOURS_ES = ["doce", "una", "dos", "tres", "cuatro", "cinco", "seis", "siete", "ocho", "nueve", "diez", "once"]


def _spoken_time(article: str | None, hour: int, minute: int, lang: str) -> str:
    h12 = hour % 12
    if lang == "en":
        suffix = "am" if hour < 12 else "pm"
        return f"{h12 or 12}{f':{minute:02d}' if minute else ''} {suffix}"
    if minute == 45:  # 16:45 is "las cinco menos cuarto"
        hour, h12 = hour + 1, (h12 + 1) % 12
    words = HOURS_ES[h12] + {0: "", 15: " y cuarto", 30: " y media", 45: " menos cuarto"}.get(minute, f" y {minute}")
    part = "de la mañana" if hour < 12 else "del mediodía" if hour == 12 else "de la tarde" if hour < 20 else "de la noche"
    lead = "la" if words.startswith("una") else "las"
    return f"{lead if article else ''} {words} {part}".strip()


def speakable(text: str, locale: str) -> str:
    """A chat message as a voice should read it. Display text is never changed: only what is spoken."""
    lang = "en" if locale.startswith("en") else "es"
    out = _EMOJI.sub("", text)
    out = _OPTION.sub("opción \\1: " if lang == "es" else "option \\1: ", out)
    out = _BULLET.sub(". ", out)
    out = out.replace("·", ",")
    out = _DATE.sub(lambda m: (f"{int(m[1])} de {MONTHS['es'][int(m[2]) - 1]}" if lang == "es"
                               else f"{int(m[1])} {MONTHS['en'][int(m[2]) - 1]}") if 1 <= int(m[2]) <= 12 else m[0], out)
    out = _TIME.sub(lambda m: _spoken_time(m[1], int(m[2]), int(m[3]), lang) if int(m[2]) < 24 else m[0], out)
    out = _SLASH_GENDER.sub(lambda m: f"{m[1]} o {m[1][:-1] if m[1].endswith('o') else m[1]}a", out)
    out = re.sub(r"\s*\n+\s*", ". ", out)
    out = re.sub(r"([.?!:])\s*\.", r"\1", out)  # no ". ." left by joined lines
    return re.sub(r"\s{2,}", " ", out).strip()


class ElevenLabsVoice:
    """Text-to-speech with ElevenLabs. `synthesize` returns None on any problem: the caller falls back."""

    def __init__(self, settings: VoiceSettings, api_key: str | None = None):
        self.settings = settings
        self.api_key = api_key if api_key is not None else os.getenv("ELEVENLABS_API_KEY")

    @property
    def available(self) -> bool:
        return bool(self.api_key)

    def voice_for(self, locale: str) -> str | None:
        v = self.settings.voices
        return v.get(locale) or v.get(locale.split("-")[0]) or v.get("default")

    def synthesize(self, text: str, locale: str) -> bytes | None:
        voice = self.voice_for(locale)
        if not (self.available and voice and text):
            return None
        try:
            response = httpx.post(
                TTS_URL.format(voice=voice),
                params={"output_format": "mp3_44100_64"},
                headers={"xi-api-key": self.api_key, "accept": "audio/mpeg"},
                json={"text": text[:MAX_CHARS], "model_id": self.settings.model, "language_code": locale.split("-")[0]},
                timeout=15,
            )
            response.raise_for_status()
            return response.content
        except httpx.HTTPError as exc:
            detail = getattr(getattr(exc, "response", None), "status_code", "")
            log.warning("ElevenLabs text-to-speech failed (%s): the browser voice is used", detail or exc.__class__.__name__)
            return None
