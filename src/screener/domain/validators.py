"""Business validation of extracted values.

The extraction model only says what the candidate *meant*. Whether that is acceptable
(a real name, a future date, a coherent availability) is decided here, in plain code,
so the rules are testable and identical in every channel.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Generic, TypeVar

from screener.config import Platform
from screener.domain.models import Availability, Schedule, StartDateExpr, StartDateKind
from screener.domain.text import contains_phrase, normalize

T = TypeVar("T")


@dataclass
class Validation(Generic[T]):
    value: T | None = None
    error: str | None = None  # machine code, mapped to a hint for the next question
    flag: str | None = None   # accepted, but worth a recruiter's attention

    @property
    def ok(self) -> bool:
        return self.error is None


PAST_DATE_ROLLOVER_DAYS = 60

_NAME_CHARS = re.compile(r"^[^\W\d_]+(?:[-'][^\W\d_]+)*$", re.UNICODE)


def validate_full_name(raw: str | None) -> Validation[str]:
    if not raw or not raw.strip():
        return Validation(error="name_invalid")
    words = raw.strip().split()
    if len(words) > 6 or not all(_NAME_CHARS.match(w) for w in words):
        return Validation(error="name_invalid")
    if len(words) < 2:
        return Validation(value=_title(raw), error="name_needs_surname")
    return Validation(value=_title(raw))


def _title(name: str) -> str:
    """Capitalise words typed in lowercase ('ana López' -> 'Ana López'), keeping particles
    ('María de la Cruz') and the candidate's own casing elsewhere ('McDonald')."""
    small = {"de", "del", "la", "las", "los", "y", "da", "van", "von"}
    words = name.lower().split() if name.isupper() else name.split()
    return " ".join(
        w if (i and w.lower() in small) or not w[0].islower() else w[0].upper() + w[1:]
        for i, w in enumerate(words)
    )


def validate_availability(values: list[str] | None) -> Validation[list[Availability]]:
    items = _dedupe([Availability(v) for v in values or []])
    if not items:
        return Validation(error="availability_unclear")
    if Availability.FULL_TIME in items and Availability.PART_TIME in items:
        return Validation(error="availability_contradiction")
    return Validation(value=items)


def validate_schedule(values: list[str] | None) -> Validation[list[Schedule]]:
    items = _dedupe([Schedule(v) for v in values or []])
    if not items:
        return Validation(error="schedule_unclear")
    concrete = {Schedule.MORNING, Schedule.AFTERNOON, Schedule.EVENING}
    if Schedule.FLEXIBLE in items or concrete.issubset(items):
        return Validation(value=[Schedule.FLEXIBLE])
    return Validation(value=items)


def validate_experience_months(months: int | None) -> Validation[int]:
    """The model reports total months ("año y medio" -> 18); years are derived by code."""
    if months is None:
        return Validation(error="experience_unclear")
    if months < 0 or months > 600:
        return Validation(error="experience_invalid")
    return Validation(value=int(months))


def normalize_platforms(raw: list[str] | None, known: list[Platform]) -> list[str]:
    """Map 'uber', 'UberEats' -> 'Uber Eats'; keep unknown employers as written."""
    result: list[str] = []
    for item in raw or []:
        norm = normalize(item)
        if not norm:
            continue
        match = next(
            (p.name for p in known if any(contains_phrase(norm, a) for a in p.aliases)), None
        )
        result.append(match or item.strip())
    return _dedupe(result)


def resolve_start_date(expr: StartDateExpr, today: date) -> Validation[date]:
    """Turn the model's structured reading of the answer into a date. Arithmetic is code's job."""
    kind = expr.kind
    if kind == StartDateKind.IMMEDIATE:
        return Validation(value=today)
    if kind == StartDateKind.IN_DAYS and expr.amount is not None:
        return Validation(value=today + timedelta(days=expr.amount))
    if kind == StartDateKind.IN_WEEKS and expr.amount is not None:
        return Validation(value=today + timedelta(weeks=expr.amount))
    if kind == StartDateKind.IN_MONTHS and expr.amount is not None:
        return Validation(value=_add_months(today, expr.amount))
    if kind == StartDateKind.NEXT_WEEKDAY and expr.weekday is not None and 0 <= expr.weekday <= 6:
        days_ahead = (expr.weekday - today.weekday()) % 7 or 7
        return Validation(value=today + timedelta(days=days_ahead))
    if kind == StartDateKind.EXACT_DATE and expr.exact_date:
        try:
            value = date.fromisoformat(expr.exact_date)
        except ValueError:
            return Validation(error="start_date_unclear")
        # "el 10 de enero" said in December means next year; "el 1 de octubre" said on
        # 21 October is a mistake to clarify, not a start date eleven months away.
        if value < today - timedelta(days=PAST_DATE_ROLLOVER_DAYS):
            try:
                value = value.replace(year=value.year + 1)
            except ValueError:  # 29 February
                value = value.replace(year=value.year + 1, day=28)
        return Validation(value=value)
    return Validation(error="start_date_unclear")


def validate_start_date(value: date, today: date, late_start_days: int) -> Validation[date]:
    if value < today:
        return Validation(error="start_date_past")
    if value > today + timedelta(days=late_start_days):
        return Validation(value=value, flag="late_start")
    return Validation(value=value)


def _add_months(d: date, months: int) -> date:
    month_index = d.month - 1 + months
    year, month = d.year + month_index // 12, month_index % 12 + 1
    for day in (d.day, 30, 29, 28):
        try:
            return date(year, month, day)
        except ValueError:
            continue
    raise ValueError("unreachable")


def _dedupe(items: list[T]) -> list[T]:
    seen: list[T] = []
    for item in items:
        if item not in seen:
            seen.append(item)
    return seen
