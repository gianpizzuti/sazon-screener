from __future__ import annotations

from datetime import date, datetime
from pathlib import Path

import pytest

from screener.config import load_client_config
from screener.domain.models import ConversationState, StartDateExpr
from screener.engine.engine import ScreeningEngine
from screener.engine.policy import ScreeningPolicy
from screener.llm.interfaces import LLMError
from screener.llm.schemas import Evidence, Extracted, TurnAnalysis
from screener.llm.templates import TemplateResponder
from screener.storage.repository import Repository

ROOT = Path(__file__).resolve().parents[1]
TODAY = date(2026, 10, 20)  # a Tuesday
NOW = datetime(2026, 10, 20, 10, 0)

EVIDENCE_GROUP = {
    "full_name": "full_name",
    "drivers_license": "drivers_license",
    "location_text": "location",
    "location_city_id": "location",
    "location_zone": "location",
    "location_outside_service_area": "location",
    "availability": "availability",
    "schedule": "schedule",
    "experience_years": "experience",
    "experience_platforms": "experience",
    "start_date": "start_date",
}


def analysis(message: str, intents=("provide_info",), quotes: dict | None = None, **fields) -> TurnAnalysis:
    """Build what the model would return for `message`.

    Evidence defaults to the whole message for every extracted field (so grounding
    passes); pass `quotes` to simulate the model citing something else.
    """
    overrides = {k: fields.pop(k) for k in list(fields) if k not in EVIDENCE_GROUP}
    extracted = Extracted.model_validate({**Extracted.empty().model_dump(), **fields})
    groups = {EVIDENCE_GROUP[k] for k, v in fields.items() if v is not None}
    quotes = quotes or {}
    evidence = [Evidence(field=g, quote=quotes.get(g, message)) for g in sorted(groups)]
    return TurnAnalysis.blank(intents=list(intents), extracted=extracted, evidence=evidence, **overrides)


def start_expr(kind: str, **kw) -> StartDateExpr:
    return StartDateExpr(kind=kind, **kw)


@pytest.fixture(scope="session")
def config():
    return load_client_config(ROOT / "config" / "clients" / "grupo_sazon")


@pytest.fixture
def policy(config):
    return ScreeningPolicy(config)


@pytest.fixture
def state():
    return ConversationState(id="c1", client_id="grupo_sazon", channel="test")


class ScriptedUnderstander:
    """Returns pre-built analyses in order; an Exception in the script is raised."""

    def __init__(self, script: list):
        self.script = list(script)
        self.requests = []

    def analyze(self, request):
        self.requests.append(request)
        item = self.script.pop(0)
        if isinstance(item, Exception):
            raise item
        return item


class FailingResponder:
    def compose(self, request):
        raise LLMError("down")


class LongResponder:
    def compose(self, request):
        return "x" * 2000


@pytest.fixture
def make_engine(config):
    def _make(script, responder=None, summarizer=None):
        return ScreeningEngine(
            config=config,
            repository=Repository("sqlite://"),
            understander=ScriptedUnderstander(script),
            responder=responder or TemplateResponder(config),
            summarizer=summarizer,
            clock=lambda: NOW,
        )

    return _make
