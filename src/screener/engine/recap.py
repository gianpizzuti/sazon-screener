"""Deterministic recap rendering.

The recap is the one message where the candidate checks their data, so precision beats
naturalness: it is rendered from state by code, never paraphrased by a model.
"""

from __future__ import annotations

from datetime import date

from screener.config import Copy
from screener.domain.models import ConversationState, FieldName, FieldStatus

WEEKDAYS = {
    "es": ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"],
    "en": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
}
MONTHS_EN = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def format_date(d: date, locale: str, today: date | None = None) -> str:
    lang = locale.split("-")[0]
    show_year = today is not None and d.year != today.year
    if lang == "en":
        return f"{WEEKDAYS['en'][d.weekday()]} {d.day} {MONTHS_EN[d.month - 1]}" + (f" {d.year}" if show_year else "")
    return f"{WEEKDAYS['es'][d.weekday()]} {d.day:02d}/{d.month:02d}" + (f"/{d.year}" if show_year else "")


def render_recap(state: ConversationState, copy: Copy, today: date) -> str:
    loc = state.locale
    d = state.data

    def label(key: str) -> str:
        return copy.text(f"recap.labels.{key}", loc)

    def unclear_or(field: FieldName, value: str | None) -> str:
        if state.field(field).status == FieldStatus.UNCLEAR or not value:
            return copy.text("values.unclear", loc)
        return value

    license_value = None
    if d.has_drivers_license is not None:
        license_value = copy.text("values.yes" if d.has_drivers_license else "values.no", loc)

    place = d.city
    if place and d.zone:
        place = f"{d.city} ({d.zone})"

    availability = ", ".join(copy.text(f"values.availability.{a.value}", loc) for a in d.availability)
    schedule = ", ".join(copy.text(f"values.schedule.{s.value}", loc) for s in d.preferred_schedule)

    experience = None
    if d.experience_months is not None:
        if d.experience_months == 0:
            experience = copy.text("values.no_experience", loc)
        else:
            experience = _duration(d.experience_months, copy, loc)
            if d.experience_platforms:
                experience += f" ({', '.join(d.experience_platforms)})"

    start = None
    if d.start_date:
        start = format_date(d.start_date, loc, today)
        if d.start_date == today:
            start = copy.text("values.start_immediate", loc, date=start)

    lines = [
        copy.text("recap.title", loc),
        f"• {label('full_name')}: {unclear_or(FieldName.FULL_NAME, d.full_name)}",
        f"• {label('drivers_license')}: {unclear_or(FieldName.DRIVERS_LICENSE, license_value)}",
        f"• {label('location')}: {unclear_or(FieldName.LOCATION, place)}",
        f"• {label('availability')}: {unclear_or(FieldName.AVAILABILITY, availability)}",
        f"• {label('schedule')}: {unclear_or(FieldName.SCHEDULE, schedule)}",
        f"• {label('experience')}: {unclear_or(FieldName.EXPERIENCE_YEARS, experience)}",
        f"• {label('start_date')}: {unclear_or(FieldName.START_DATE, start)}",
        "",
        copy.text("recap.question", loc),
    ]
    return "\n".join(lines)


def _duration(months: int, copy: Copy, loc: str) -> str:
    if months < 12:
        return copy.text("values.months", loc, n=str(months))
    if months == 12:
        return copy.text("values.one_year", loc)
    years = f"{round(months / 12, 1):g}"
    return copy.text("values.years", loc, n=years if loc == "en" else years.replace(".", ","))
