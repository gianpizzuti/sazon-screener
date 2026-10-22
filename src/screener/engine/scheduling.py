"""Interview booking: which times to offer, how to show them, and which one the candidate chose.

Like dates and places, this is deterministic code: the times come from the client's
configuration and the bookings already taken; the language model is only a fallback for
reading a free-text choice ("el martes a las 5") when these rules can't.
"""

from __future__ import annotations

import re
from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

from screener.config import SchedulingSettings
from screener.domain.models import Schedule
from screener.domain.text import normalize

UTC = timezone.utc
# Which local hours suit each preferred shift (interviews happen in the configured windows).
SHIFT_HOURS = {Schedule.MORNING: (0, 14), Schedule.AFTERNOON: (14, 24), Schedule.EVENING: (17, 24)}

WEEKDAYS = {
    "es": ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"],
    "en": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
}
MONTHS_EN = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
WEEKDAY_WORDS = {normalize(w): i for names in WEEKDAYS.values() for i, w in enumerate(names)}
ORDINALS = {
    "primera": 0, "primero": 0, "first": 0, "1a": 0, "1o": 0,
    "segunda": 1, "segundo": 1, "second": 1, "2a": 1, "2o": 1,
    "tercera": 2, "tercero": 2, "third": 2, "3a": 2, "3o": 2,
}
LAST_WORDS = {"ultima", "ultimo", "last"}


def _utc(local: datetime) -> datetime:
    return local.astimezone(UTC).replace(tzinfo=None)


def local_time(slot_utc: datetime, tz: str) -> datetime:
    return slot_utc.replace(tzinfo=UTC).astimezone(ZoneInfo(tz))


def candidate_slots(
    settings: SchedulingSettings,
    tz: str,
    now_utc: datetime,
    prefer: list[Schedule],
    unavailable: set[datetime],
    count: int | None = None,
) -> list[datetime]:
    """Free interview starts (UTC) to offer: inside the configured windows, after the minimum
    lead time, not taken, preferring the candidate's shift and spreading them over different
    days, earliest first."""
    zone = ZoneInfo(tz)
    count = count or settings.offer_count
    local_now = now_utc.replace(tzinfo=UTC).astimezone(zone)
    earliest = local_now + timedelta(hours=settings.min_lead_hours)
    step = timedelta(minutes=settings.slot_minutes)

    starts: list[datetime] = []
    for offset in range(settings.horizon_days + 1):
        day: date = (local_now + timedelta(days=offset)).date()
        if day.weekday() not in settings.weekdays:
            continue
        for window in settings.windows:
            begin, end = (time.fromisoformat(part.strip()) for part in window.split("-"))
            t, stop = datetime.combine(day, begin, zone), datetime.combine(day, end, zone)
            while t + step <= stop:
                if t >= earliest and _utc(t) not in unavailable:
                    starts.append(t)
                t += step
    starts.sort()

    shifts = [s for s in prefer if s in SHIFT_HOURS]
    if shifts and Schedule.FLEXIBLE not in prefer:
        fitting = [t for t in starts if any(lo <= t.hour < hi for lo, hi in (SHIFT_HOURS[s] for s in shifts))]
        pool = fitting or starts
    else:
        pool = starts

    picked: list[datetime] = []
    for t in pool:  # one per day first, so the candidate gets a real choice
        if all(p.date() != t.date() for p in picked):
            picked.append(t)
        if len(picked) == count:
            break
    for t in pool:
        if len(picked) == count:
            break
        if t not in picked:
            picked.append(t)
    return sorted(_utc(t) for t in picked)


def slot_label(slot_utc: datetime, tz: str, locale: str) -> str:
    """Short label for a quick-reply button: "mar 27/10 · 17:00" / "Tue 27 Oct · 17:00"."""
    t = local_time(slot_utc, tz)
    if locale.startswith("en"):
        return f"{WEEKDAYS['en'][t.weekday()][:3]} {t.day} {MONTHS_EN[t.month - 1]} · {t:%H:%M}"
    return f"{WEEKDAYS['es'][t.weekday()][:3]} {t.day:02d}/{t.month:02d} · {t:%H:%M}"


def slot_long(slot_utc: datetime, tz: str, locale: str) -> str:
    """For sentences: "martes 27/10 a las 17:00" / "Tuesday 27 Oct at 17:00"."""
    t = local_time(slot_utc, tz)
    if locale.startswith("en"):
        return f"{WEEKDAYS['en'][t.weekday()]} {t.day} {MONTHS_EN[t.month - 1]} at {t:%H:%M}"
    return f"{WEEKDAYS['es'][t.weekday()]} {t.day:02d}/{t.month:02d} a las {t:%H:%M}"


_EXPLICIT_TIME = re.compile(r"\b(\d{1,2})[:h.](\d{2})\b")
# "a las 4" is 16:00 sharp; "a las 4 y media" is 16:30.
_SPOKEN_HOUR = re.compile(r"\b(?:a las|las|at|sobre las)\s+(\d{1,2})(?:\s+y\s+(media|cuarto))?\b")
_SPOKEN_MINUTES = {"": 0, "media": 30, "cuarto": 15}
_DATE = re.compile(r"\b(\d{1,2})/(\d{1,2})\b")


def match_choice(message: str, slots_utc: list[datetime], tz: str, locale: str, model_choice: int | None = None) -> int | None:
    """Index of the slot the candidate chose, or None. Rules first (button text, option
    number, weekday, date, time); the model's reading only when the rules find nothing."""
    if not slots_utc:
        return None
    n = normalize(message)
    labels = [normalize(slot_label(s, tz, locale)) for s in slots_utc]
    if n in labels:
        return labels.index(n)

    local = [local_time(s, tz) for s in slots_utc]
    candidates = set(range(len(slots_utc)))
    constrained = False

    if dates := _DATE.findall(message):
        day, month = (int(x) for x in dates[0])
        candidates &= {i for i, t in enumerate(local) if (t.day, t.month) == (day, month)}
        constrained = True
    tokens = n.split()
    weekdays = {WEEKDAY_WORDS[t] for t in tokens if t in WEEKDAY_WORDS}
    if weekdays:
        candidates &= {i for i, t in enumerate(local) if t.weekday() in weekdays}
        constrained = True
    hours: set[tuple[int, int | None]] = {(int(h), int(m)) for h, m in _EXPLICIT_TIME.findall(message)}
    hours |= {(int(h), _SPOKEN_MINUTES[m]) for h, m in _SPOKEN_HOUR.findall(n)}
    if hours:
        def fits(t: datetime) -> bool:
            # "a las 5" in an interview context means 17:00: no interviews before 9.
            return any(t.hour in (h, h + 12 if h < 9 else h) and (m is None or t.minute == m) for h, m in hours)
        candidates &= {i for i, t in enumerate(local) if fits(t)}
        constrained = True

    if not constrained and len(tokens) <= 8:
        picks = {ORDINALS[t] for t in tokens if t in ORDINALS}
        if any(t in LAST_WORDS for t in tokens):
            picks.add(len(slots_utc) - 1)
        if len(tokens) <= 4:  # a bare number only in a short reply ("2", "la 2"), not in a sentence
            picks |= {int(t) - 1 for t in tokens if t.isdigit() and 1 <= int(t) <= len(slots_utc)}
        if len(picks) == 1:
            return picks.pop()

    if constrained and len(candidates) == 1:
        return candidates.pop()
    if model_choice is not None and 1 <= model_choice <= len(slots_utc):
        return model_choice - 1
    return None


NONE_WORDS = ("ninguno", "ninguna", "otro dia", "otra hora", "otro horario", "otros horarios", "no me va",
              "no me viene", "no puedo", "none", "other time", "another time", "doesnt work", "don't work", "dont work")
CHANGE_WORDS = ("cambiar", "cambio", "reprogramar", "mover la", "no puedo ir", "no voy a poder", "otro dia", "otra hora",
                "reschedule", "change", "cant make it", "can't make it", "cancel")


def wants_other_times(message: str, intents: set[str], none_label: str) -> bool:
    n = normalize(message)
    return n == normalize(none_label) or any(w in n for w in NONE_WORDS) or ("deny" in intents and "affirm" not in intents)


def wants_to_reschedule(message: str, intents: set[str]) -> bool:
    n = normalize(message)
    return any(w in n for w in CHANGE_WORDS) or bool(intents & {"correction", "postpone"})
