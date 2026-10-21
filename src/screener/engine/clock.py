"""Clocks. The engine never calls datetime.now() directly, so time can be controlled.

`DemoClock` lets a demo move time forward for the whole system ("+1 day") instead of
rewriting history: follow-ups, abandonment and dates then behave exactly as they would.
Its offset is persisted, so restarting the API doesn't send time backwards. Never enabled
in production (SCREENER_DEMO_TOOLS).
"""

from __future__ import annotations

import json
from collections.abc import Callable
from datetime import datetime, timedelta
from pathlib import Path

from screener.domain.models import utcnow


class DemoClock:
    def __init__(self, path: Path, base: Callable[[], datetime] = utcnow):
        self.path = path
        self.base = base
        self.offset = timedelta(hours=self._load())

    def __call__(self) -> datetime:
        return self.base() + self.offset

    @property
    def offset_hours(self) -> float:
        return self.offset.total_seconds() / 3600

    def advance(self, hours: float) -> None:
        self.offset += timedelta(hours=hours)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps({"offset_hours": self.offset_hours}))

    def _load(self) -> float:
        try:
            return float(json.loads(self.path.read_text())["offset_hours"])
        except (FileNotFoundError, ValueError, KeyError):
            return 0.0
