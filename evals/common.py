"""Shared eval helpers: fixed dates, metered Anthropic clients and prices.

Every eval talks to the real API through a client whose HTTP responses are metered,
so each report states what it cost and how many tokens each model used.
"""

from __future__ import annotations

import statistics
import threading
from datetime import date, datetime
from pathlib import Path

import anthropic
import httpx
from dotenv import load_dotenv

from screener.config import ClientConfig, load_client_config

ROOT = Path(__file__).resolve().parents[1]
EVALS = ROOT / "evals"
RESULTS = EVALS / "results"

# Fixed "today" so date expectations ("el lunes que viene") are reproducible.
TODAY = date(2026, 10, 20)  # a Tuesday
NOW = datetime(2026, 10, 20, 16, 0)  # UTC: 18:00 in Madrid, 10:00 in Mexico City, same date in both

MODELS = {"haiku": "claude-haiku-5-5", "sonnet": "claude-sonnet-5-5", "opus": "claude-opus-5-5"}

# USD per million tokens: input, 5-minute cache write, cache read, output.
# Source: platform.claude.com/docs/en/about-claude/pricing (read 2026-10-21).
PRICES = {
    "claude-haiku-5-5": (0.10, 0.125, 0.01, 0.50),
    "claude-sonnet-5-5": (2.00, 2.50, 0.10, 10.00),
    "claude-opus-5-5": (4.00, 5.00, 0.20, 20.00),
}


def load_config(**model_overrides: str) -> ClientConfig:
    """The real client configuration, optionally with other models for some tasks."""
    load_dotenv(ROOT / ".env")
    cfg = load_client_config(ROOT / "config" / "clients" / "grupo_sazon")
    if model_overrides:
        cfg = cfg.model_copy(update={"models": cfg.models.model_copy(update=model_overrides)})
    return cfg


def price_of(model: str, usage: dict) -> float:
    key = next((k for k in PRICES if model.startswith(k)), None)
    if key is None:
        return 0.0
    p_in, p_write, p_read, p_out = PRICES[key]
    return (
        usage.get("input_tokens", 0) * p_in
        + (usage.get("cache_creation_input_tokens") or 0) * p_write
        + (usage.get("cache_read_input_tokens") or 0) * p_read
        + usage.get("output_tokens", 0) * p_out
    ) / 1_000_000


class UsageMeter:
    """Collects the `usage` block of every successful Messages API response."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self.calls: list[tuple[str, dict]] = []  # (model, usage)

    def hook(self, response: httpx.Response) -> None:
        if response.status_code != 200 or not response.request.url.path.endswith("/messages"):
            return
        response.read()  # httpx allows reading the body inside a response hook
        body = response.json()
        with self._lock:
            self.calls.append((body.get("model", "?"), body.get("usage") or {}))

    def client(self, timeout: float = 90.0) -> anthropic.Anthropic:
        load_dotenv(ROOT / ".env")
        http = anthropic.DefaultHttpxClient(event_hooks={"response": [self.hook]})
        return anthropic.Anthropic(timeout=timeout, max_retries=4, http_client=http)

    def by_model(self) -> dict[str, dict]:
        out: dict[str, dict] = {}
        with self._lock:
            for model, usage in self.calls:
                row = out.setdefault(model, {"calls": 0, "input": 0, "cache_write": 0, "cache_read": 0, "output": 0, "usd": 0.0})
                row["calls"] += 1
                row["input"] += usage.get("input_tokens", 0)
                row["cache_write"] += usage.get("cache_creation_input_tokens") or 0
                row["cache_read"] += usage.get("cache_read_input_tokens") or 0
                row["output"] += usage.get("output_tokens", 0)
                row["usd"] += price_of(model, usage)
        return out

    def total_usd(self) -> float:
        return sum(row["usd"] for row in self.by_model().values())


def percentile(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    if len(values) == 1:
        return values[0]
    return statistics.quantiles(values, n=100, method="inclusive")[int(q) - 1]


def pct(n: int, d: int) -> str:
    return f"{100 * n / d:.0f}%" if d else "n/a"
