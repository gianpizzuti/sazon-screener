"""Shared presentation helpers: status labels, formatting, charts."""

from __future__ import annotations

from datetime import date, datetime, timezone

import altair as alt
import pandas as pd
import streamlit as st

# Status always shown as icon + label, never colour alone.
STATUS = {
    "qualified": ("✅", "Qualified", "green"),
    "needs_review": ("⚠️", "Needs review", "orange"),
    "in_progress": ("💬", "In progress", "blue"),
    "abandoned": ("💤", "Abandoned", "gray"),
    "disqualified": ("⛔", "Disqualified", "red"),
    "withdrawn": ("↩️", "Withdrawn", "gray"),
    "terminated": ("🚫", "Closed (abuse)", "gray"),
}
REVIEW = {
    "new": "New",
    "contacted": "Contacted",
    "interview": "Interview",
    "hired": "Hired",
    "rejected": "Rejected",
}
REASONS = {
    "no_license": "No driver's license",
    "license_in_progress": "License in progress",
    "out_of_area": "Outside service area",
}
AVAILABILITY = {"full_time": "Full-time", "part_time": "Part-time", "weekends": "Weekends"}
SCHEDULE = {"morning": "Morning", "afternoon": "Afternoon", "evening": "Evening", "flexible": "Flexible"}
FIELD_LABELS = {
    "full_name": "Name",
    "drivers_license": "Driver's license",
    "location": "City / zone",
    "zone": "Zone",
    "availability": "Availability",
    "schedule": "Schedule",
    "experience_years": "Experience",
    "experience_platforms": "Platforms",
    "start_date": "Start date",
}
FIELD_STATUS = {"valid": "✅ valid", "unclear": "⚠️ unclear", "invalid": "❌ invalid", "missing": "· missing", "skipped": "– skipped"}

# Single-series charts use one validated blue (light / dark steps), text uses text tokens.
CHART = {
    "light": {"series": "#2a78d6", "text": "#52514e", "grid": "#e4e3df"},
    "dark": {"series": "#3987e5", "text": "#c3c2b7", "grid": "#3a3a37"},
}


def theme() -> dict:
    mode = getattr(st.context.theme, "type", None) or "light"
    return CHART.get(mode, CHART["light"])


def status_label(status: str) -> str:
    icon, label, _ = STATUS.get(status, ("•", status, "gray"))
    return f"{icon} {label}"


def status_badge(status: str) -> None:
    icon, label, color = STATUS.get(status, ("•", status, "gray"))
    st.badge(label, icon=icon, color=color)


def experience(months: int | None) -> str:
    if months is None:
        return "–"
    if months == 0:
        return "None"
    return f"{months} mo" if months < 12 else f"{months / 12:.1f}".rstrip("0").rstrip(".") + " yr"


def short_date(value) -> str:
    if not value:
        return "–"
    d = date.fromisoformat(value[:10]) if isinstance(value, str) else value
    return d.strftime("%a %d %b")


def ago(value: str | None) -> str:
    if not value:
        return "–"
    then = datetime.fromisoformat(value).replace(tzinfo=timezone.utc)
    minutes = (datetime.now(timezone.utc) - then).total_seconds() / 60
    if minutes < 1:
        return "just now"
    if minutes < 60:
        return f"{minutes:.0f} min ago"
    if minutes < 48 * 60:
        return f"{minutes / 60:.0f} h ago"
    return f"{minutes / 1440:.0f} d ago"


def pct(value: float | None) -> str:
    return "–" if value is None else f"{value:.0%}"


def hbar(rows: list[tuple[str, int]], value_label: str, keep_order: bool = False, share_of: int | None = None) -> alt.Chart:
    """Horizontal single-series bar chart: thin bars, rounded data end, value at the tip, tooltip."""
    t = theme()
    df = pd.DataFrame(rows, columns=["label", "value"])
    if share_of:
        df["share"] = df["value"] / share_of
    tooltip = [alt.Tooltip("label:N", title=""), alt.Tooltip("value:Q", title=value_label)]
    if share_of:
        tooltip.append(alt.Tooltip("share:Q", title="of started", format=".0%"))
    base = alt.Chart(df).encode(
        y=alt.Y("label:N", sort=list(df["label"]) if keep_order else "-x", title=None,
                axis=alt.Axis(labelColor=t["text"], labelLimit=180, ticks=False, domain=False, labelPadding=8)),
        x=alt.X("value:Q", title=None, scale=alt.Scale(domainMin=0, nice=True),
                axis=alt.Axis(labels=False, ticks=False, domain=False, grid=True, gridColor=t["grid"], tickMinStep=1)),
        tooltip=tooltip,
    )
    bars = base.mark_bar(size=18, cornerRadiusEnd=4, color=t["series"])
    labels = base.mark_text(align="left", dx=6, color=t["text"], fontSize=12).encode(text="value:Q")
    return (bars + labels).properties(height=max(90, 32 * len(df))).configure_view(stroke=None)
