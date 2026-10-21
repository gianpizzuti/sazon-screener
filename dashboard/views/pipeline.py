"""Pipeline: the recruiter queue, most actionable candidates first."""

from collections import Counter

import pandas as pd
import streamlit as st

import client
import ui

FLAG_LABELS = {
    "human_requested": "asked for a person",
    "late_start": "late start",
    "abuse": "abusive language",
    "update_after_close": "new info after close",
    "unclear_field": "unclear answer",
}


def page() -> None:
    st.title("Candidate pipeline")
    st.caption("Qualified candidates first, then the ones that need a human look. Click a row to open it.")
    rows = client.candidates()

    counts = Counter(r["status"] for r in rows)
    for column, key in zip(st.columns(6), ["qualified", "needs_review", "in_progress", "awaiting_reply", "abandoned", "disqualified"]):
        column.metric(ui.status_label(key), counts.get(key, 0))

    f1, f2, f3, f4 = st.columns([2.2, 2, 1.3, 1.5])
    statuses = f1.multiselect("Screening outcome", list(ui.STATUS), default=["qualified", "needs_review"], format_func=ui.status_label)
    reviews = f2.multiselect("Recruiter status", list(ui.REVIEW), format_func=ui.REVIEW.get, placeholder="Any")
    city = f3.selectbox("City", ["All", *sorted({r["city"] for r in rows if r["city"]})])
    search = f4.text_input("Search name", placeholder="e.g. Ana")

    shown = [
        r for r in rows
        if (not statuses or r["status"] in statuses)
        and (not reviews or r["review_status"] in reviews)
        and (city == "All" or r["city"] == city)
        and (not search or search.lower() in (r["name"] or "").lower())
    ]
    if not shown:
        st.info("No candidates match these filters." if rows else "No candidates yet. Try the agent from the sidebar.", icon=":material/info:")
        return

    df = pd.DataFrame([
        {
            "Status": ui.status_label(r["status"]),
            "Name": r["name"] or "–",
            "City": f'{r["city"]} · {r["zone"]}' if r["zone"] else (r["city"] or "–"),
            "Availability": ", ".join(ui.AVAILABILITY.get(a, a) for a in r["availability"]) or "–",
            "Shift": ", ".join(ui.SCHEDULE.get(s, s) for s in r["schedule"]) or "–",
            "Experience": ui.experience(r["experience_months"]),
            "Start": ui.short_date(r["start_date"]),
            "Recruiter": ui.REVIEW.get(r["review_status"], r["review_status"]),
            "Flags": ", ".join(FLAG_LABELS.get(f, f) for f in r["flags"]),
            "Open questions": r["open_questions"] or None,
            "Follow-ups": ui.followups(r),
            "Last activity": ui.ago(r["last_activity"]),
            "id": r["id"],
        }
        for r in shown
    ])
    st.caption(f"{len(shown)} of {len(rows)} candidates")
    event = st.dataframe(
        df.drop(columns="id"),
        hide_index=True,
        width="stretch",
        on_select="rerun",
        selection_mode="single-row",
        column_config={
            "Open questions": st.column_config.NumberColumn(help="Questions Sofía couldn't answer"),
            "Follow-ups": st.column_config.TextColumn(help="Reminders sent to a silent candidate (max 3), and when the next one goes out"),
        },
    )
    if event.selection.rows:
        st.switch_page("views/candidate.py", query_params={"id": df.iloc[event.selection.rows[0]]["id"]})


client.guarded(page)
