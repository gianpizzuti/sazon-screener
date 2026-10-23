"""Wiring: build the engine from configuration and environment."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

from screener.config import ClientConfig, load_client_config
from screener.domain.models import utcnow
from screener.engine.clock import DemoClock
from screener.engine.engine import ScreeningEngine
from screener.storage.repository import Repository

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CLIENT = ROOT / "config" / "clients" / "grupo_sazon"
DEFAULT_DB = f"sqlite:///{ROOT / 'data' / 'screener.db'}"


def load_config() -> ClientConfig:
    load_dotenv(ROOT / ".env")
    return load_client_config(os.getenv("SCREENER_CLIENT_CONFIG") or DEFAULT_CLIENT)


DEMO_CLOCK_FILE = ROOT / "data" / "demo_clock.json"


def demo_tools_enabled() -> bool:
    """Demo-only features (simulated clock). Never in production."""
    load_dotenv(ROOT / ".env")
    return os.getenv("SCREENER_DEMO_TOOLS", "0") == "1"


def build_engine(config: ClientConfig | None = None, database_url: str | None = None) -> ScreeningEngine:
    load_dotenv(ROOT / ".env")
    config = config or load_config()
    if not os.getenv("ANTHROPIC_API_KEY"):
        raise RuntimeError("ANTHROPIC_API_KEY is not set. Copy .env.example to .env and add your key.")

    from screener.knowledge import build_knowledge
    from screener.llm.claude import ClaudeResponder, ClaudeSummarizer, ClaudeUnderstander, make_client

    client = make_client()
    return ScreeningEngine(
        config=config,
        repository=Repository(database_url or os.getenv("SCREENER_DATABASE_URL") or DEFAULT_DB),
        understander=ClaudeUnderstander(client, config),
        responder=ClaudeResponder(client, config),
        summarizer=ClaudeSummarizer(client, config),
        clock=DemoClock(DEMO_CLOCK_FILE) if demo_tools_enabled() else utcnow,
        knowledge=build_knowledge(config),
    )
