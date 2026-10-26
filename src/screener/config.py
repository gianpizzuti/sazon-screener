"""Client configuration.

Everything that changes between clients (service areas, FAQ, copy, models, thresholds)
is data loaded from `config/clients/<client>/`. The screening logic itself is generic.
"""

from __future__ import annotations

from pathlib import Path
from typing import ClassVar, Literal

import yaml
from pydantic import BaseModel, Field, model_validator

from screener.domain.countries import COUNTRIES
from screener.domain.text import contains_phrase, normalize

Country = Literal["ES", "MX"]
Language = Literal["es", "en"]


class Zone(BaseModel):
    name: str
    aliases: list[str] = Field(default_factory=list)
    group: str | None = None  # part of the city ("Norte"), for cities with many zones


class ServiceArea(BaseModel):
    id: str
    name: str
    country: Country
    timezone: str
    restaurants: int
    aliases: list[str]
    zones: list[Zone] = Field(default_factory=list)
    interview_place: str | None = None  # where qualified candidates are interviewed
    # Neighbourhoods with no delivery zone of their own -> the closest zones, suggested instead
    nearby: dict[str, list[str]] = Field(default_factory=dict)

    MAX_ZONE_BUTTONS: ClassVar[int] = 6  # beyond this, offer parts of the city instead of every zone

    @model_validator(mode="after")
    def _nearby_names_real_zones(self) -> ServiceArea:
        names = {z.name for z in self.zones}
        if unknown := {z for zones in self.nearby.values() for z in zones} - names:
            raise ValueError(f"{self.id}: 'nearby' lists zones that don't exist: {sorted(unknown)}")
        return self

    def unlisted_place(self, text: str | None) -> str | None:
        """A neighbourhood of `nearby` named in `text` ("Madrid, Usera" -> "Usera")."""
        norm = normalize(text or "")
        return next((place for place in self.nearby if contains_phrase(norm, place)), None)

    def closest_zones(self, place: str | None) -> list[str]:
        key = self.unlisted_place(place)
        return list(self.nearby[key]) if key else []

    def zone_choices(self) -> list[str]:
        """What the candidate can tap when asked for the zone: the zones themselves, or for a
        city with many zones its parts ("Centro", "Norte"...)."""
        if len(self.zones) <= self.MAX_ZONE_BUTTONS:
            return [z.name for z in self.zones]
        return list(dict.fromkeys(z.group for z in self.zones if z.group))

    def describe_zones(self) -> str:
        """For answering "which zones are there?": every zone, grouped by part of the city."""
        groups = list(dict.fromkeys(z.group for z in self.zones if z.group))
        if not groups:
            return ", ".join(z.name for z in self.zones)
        return "; ".join(f"{g}: {', '.join(z.name for z in self.zones if z.group == g)}" for g in groups)


class Platform(BaseModel):
    name: str
    aliases: list[str]


class FaqEntry(BaseModel):
    id: str
    question: str
    examples: list[str] = Field(default_factory=list)  # other ways candidates ask it (retrieval only)
    answer: dict[str, str]  # "default", or a country code overriding it

    def answer_for(self, country: str | None) -> str:
        if country and country in self.answer:
            return self.answer[country]
        return self.answer.get("default") or next(iter(self.answer.values()))


class AgentSettings(BaseModel):
    name: str
    default_language: Language = "es"
    recruiter_language: Language = "es"
    max_message_chars: int = 350
    max_failed_attempts: int = 2
    max_times_asked: int = 3  # a question still unanswered after this, while they answer others: a person decides
    late_start_days: int = 90
    history_window: int = 30
    default_timezone: str = "Europe/Madrid"


class FollowUpSettings(BaseModel):
    """Re-engagement of silent candidates (all times in the candidate's timezone)."""

    schedule_hours: list[float] = Field(default_factory=lambda: [2, 24, 72])  # after their last message
    quiet_hours_start: int = 21            # no messages from 21:00...
    quiet_hours_end: int = 9               # ...to 09:00 local time
    abandon_after_hours: float = 24        # silence after the last follow-up => abandoned
    whatsapp_window_hours: float = 24      # after this, WhatsApp only allows pre-approved templates
    scheduler_interval_seconds: int = 60


class LicenseSettings(BaseModel):
    """Which driving licences the client accepts (a knock-out) and whether recruiters need the type."""

    accepted_types: list[Literal["car", "motorbike"]] = Field(default_factory=lambda: ["car", "motorbike"])
    ask_type: bool = True  # "sí" alone: ask once whether it is for car, motorbike or both

    def accepts(self, license_type: str | None) -> bool:
        if license_type is None or license_type == "both":
            return True
        return license_type in self.accepted_types

    def describe(self) -> str:
        return " or ".join({"car": "car", "motorbike": "motorbike"}[t] for t in self.accepted_types)


class ForeignLicenceRules(BaseModel):
    """What one hiring country's law says about licences issued abroad (`foreign_licences.yaml`, D222)."""

    valid: list[str] = Field(default_factory=list)     # works like a local licence while in force
    exchange: list[str] = Field(default_factory=list)  # valid for the first months of residence, then exchanged
    answers: dict[str, str]                             # valid / exchange / review / unknown

    @model_validator(mode="after")
    def _known_countries(self) -> ForeignLicenceRules:
        if unknown := set(self.valid + self.exchange) - COUNTRIES.keys():
            raise ValueError(f"foreign_licences: unknown country codes {sorted(unknown)}")
        if missing := {"review", "unknown"} - self.answers.keys():
            raise ValueError(f"foreign_licences: answers missing {sorted(missing)}")
        return self

    def rule(self, country: str | None) -> Literal["valid", "exchange", "review"]:
        """A country not listed, or not recognised, is `review`: a person decides."""
        if country in self.valid:
            return "valid"
        if country in self.exchange:
            return "exchange"
        return "review"


class VoiceSettings(BaseModel):
    """The voice channel (ADR 0010): ElevenLabs voices per locale. Without ELEVENLABS_API_KEY the browser's voice is used."""

    model: str = "eleven_flash_v2_5"                       # low latency, multilingual, half the credits per character
    voices: dict[str, str] = Field(default_factory=dict)   # es-ES / es-MX / en / default -> ElevenLabs voice id


class SchedulingSettings(BaseModel):
    """Interview booking in the chat, in each area's local time."""

    enabled: bool = False
    slot_minutes: int = 30
    weekdays: list[int] = Field(default_factory=lambda: [0, 1, 2, 3, 4])  # 0 = Monday
    windows: list[str] = Field(default_factory=lambda: ["10:00-13:00", "16:00-19:00"])
    min_lead_hours: float = 18      # never tomorrow at 9 for someone who qualified at midnight
    horizon_days: int = 7
    offer_count: int = 3
    max_offers: int = 2             # rounds of options before a recruiter takes over


class ModelSettings(BaseModel):
    understand: str
    speak: str
    summary: str


class RetrievalSettings(BaseModel):
    """Which knowledge-base topics the understanding model chooses from (ADR 0007)."""

    embedding_model: str | None = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    method: Literal["semantic", "hybrid"] = "semantic"  # hybrid adds keyword search (BM25)
    shortlist: int = 5  # topics shown per message


class Copy:
    """Localized fixed copy. Lookup order: exact locale, base language, then Spanish."""

    def __init__(self, tree: dict):
        self._tree = tree

    def _node(self, key: str):
        node = self._tree
        for part in key.split("."):
            node = node[part]
        return node

    @staticmethod
    def _pick(node: dict, locale: str):
        for candidate in (locale, locale.split("-")[0], "es"):
            if candidate in node:
                return node[candidate]
        raise KeyError(f"no copy for locale {locale!r}")

    def text(self, key: str, locale: str, **fmt: str) -> str:
        template: str = self._pick(self._node(key), locale)
        return fill(template, **fmt)

    def options(self, key: str, locale: str) -> list[str]:
        try:
            return list(self._pick(self._node(f"options.{key}"), locale))
        except KeyError:
            return []


def fill(template: str, **fmt: str | None) -> str:
    """Format a template, dropping the name gracefully when it is unknown."""
    if not fmt.get("name"):
        template = template.replace(", {name}", "").replace(" {name}", "").replace("{name}", "")
    values = {k: ("" if v is None else v) for k, v in fmt.items()}
    return template.format_map(_Default(values)).strip()


class _Default(dict):
    def __missing__(self, key: str) -> str:
        return ""


class ClientConfig(BaseModel):
    id: str
    name: str
    description: str
    role: dict[str, str]
    agent: AgentSettings
    models: ModelSettings
    followups: FollowUpSettings = Field(default_factory=FollowUpSettings)
    scheduling: SchedulingSettings = Field(default_factory=SchedulingSettings)
    license: LicenseSettings = Field(default_factory=LicenseSettings)
    retrieval: RetrievalSettings = Field(default_factory=RetrievalSettings)
    foreign_licences: dict[Country, ForeignLicenceRules] = Field(default_factory=dict)
    voice: VoiceSettings = Field(default_factory=VoiceSettings)
    next_steps: dict[str, str]
    platforms: list[Platform]
    service_areas: list[ServiceArea]
    faq: list[FaqEntry]
    texts: dict

    @property
    def copy_(self) -> Copy:
        return Copy(self.texts)

    def area(self, city_id: str | None) -> ServiceArea | None:
        return next((a for a in self.service_areas if a.id == city_id), None)

    def faq_entry(self, faq_id: str | None) -> FaqEntry | None:
        return next((f for f in self.faq if f.id == faq_id), None)

    def localized(self, mapping: dict[str, str], locale: str) -> str:
        return mapping.get(locale) or mapping.get(locale.split("-")[0]) or mapping["es"]


def load_client_config(path: str | Path) -> ClientConfig:
    """Load and merge every YAML file of a client folder. `copy.yaml` becomes `texts`."""
    folder = Path(path)
    if not folder.is_dir():
        raise FileNotFoundError(f"client config folder not found: {folder}")
    merged: dict = {}
    for file in sorted(folder.glob("*.yaml")):
        content = yaml.safe_load(file.read_text(encoding="utf-8")) or {}
        if file.stem == "copy":
            merged["texts"] = content
        else:
            merged.update(content)
    return ClientConfig.model_validate(merged)
