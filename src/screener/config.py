"""Client configuration.

Everything that changes between clients (service areas, FAQ, copy, models, thresholds)
is data loaded from `config/clients/<client>/`. The screening logic itself is generic.
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field

Country = Literal["ES", "MX"]
Language = Literal["es", "en"]


class Zone(BaseModel):
    name: str
    aliases: list[str] = Field(default_factory=list)


class ServiceArea(BaseModel):
    id: str
    name: str
    country: Country
    timezone: str
    restaurants: int
    aliases: list[str]
    zones: list[Zone] = Field(default_factory=list)


class Platform(BaseModel):
    name: str
    aliases: list[str]


class FaqEntry(BaseModel):
    id: str
    question: str
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


class ModelSettings(BaseModel):
    understand: str
    speak: str
    summary: str


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
