"""Analytics: is the agent fixing the client's two problems, and where does it struggle?"""

import pandas as pd
import streamlit as st

import client
import ui


def chart_or_table(title: str, caption: str, rows: list[tuple[str, int]], value_label: str, as_table: bool, **kwargs) -> None:
    st.subheader(title)
    st.caption(caption)
    if not rows:
        st.caption("_No data yet._")
        return
    if as_table:
        st.dataframe(pd.DataFrame(rows, columns=["", value_label]), hide_index=True, width="stretch")
    else:
        st.altair_chart(ui.hbar(rows, value_label, **kwargs), width="stretch", theme=None)


def page() -> None:
    head, toggle = st.columns([5, 1], vertical_alignment="bottom")
    head.title("Analytics")
    as_table = toggle.toggle("Tables", help="Show every chart as a table")
    a = client.analytics()
    started = a["totals"]["started"]
    if not started:
        st.info("No conversations yet.", icon=":material/info:")
        return

    k = st.columns(5)
    k[0].metric("Completion rate", ui.pct(a["completion_rate"]), help="Finished / (finished + abandoned). Conversations still waiting are not counted yet")
    k[1].metric("Qualified", ui.pct(a["qualified_rate"]), help="Qualified / finished")
    k[2].metric("Median time to finish", "–" if a["median_minutes_to_finish"] is None else f'{a["median_minutes_to_finish"]:g} min')
    k[3].metric("Median replies", "–" if a["median_candidate_messages"] is None else f'{a["median_candidate_messages"]:g}', help="Candidate messages per finished conversation")
    k[4].metric("Human overrides", a["human_overrides"], help="Recruiter decisions that contradict the automated outcome")

    chart_or_table(
        "Funnel", "Candidates who got past each question. The drops at License and City are the knock-outs working.",
        [(s["step"], s["count"]) for s in a["funnel"]], "Candidates", as_table, keep_order=True, share_of=started,
    )
    left, right = st.columns(2, gap="large")
    with left:
        chart_or_table("Why candidates are knocked out", "Disqualification reasons.",
                       [(ui.REASONS.get(k, k), v) for k, v in a["knockout_reasons"].items()], "Candidates", as_table)
        chart_or_table("Where candidates get frustrated", "Frustrated messages by the question being asked: candidates for rewording.",
                       list(a["frustration_by_field"].items()), "Messages", as_table)
    with right:
        chart_or_table("Where abandoned candidates stopped", "Pending question when the last reminder went unanswered.",
                       list(a["drop_off"].items()), "Candidates", as_table)
        chart_or_table("What candidates ask", "Questions answered from the FAQ, by topic.",
                       [(k.replace("_", " ").capitalize(), v) for k, v in a["faq_usage"].items()], "Questions", as_table)

    st.subheader("Re-engagement")
    st.caption("Silent candidates get up to 3 reminders (+2 h, +24 h, +72 h, never at night in their timezone). "
               "Recovery = candidates who replied after a reminder: the direct measure of the 60% no-answer problem.")
    r = st.columns(4)
    r[0].metric("Candidates nudged", a["candidates_nudged"])
    r[1].metric("Recovered", a["candidates_recovered"])
    r[2].metric("Recovery rate", ui.pct(a["recovery_rate"]))
    r[3].metric("Follow-ups sent", a["followups_sent"])
    if a["recovered_by_followup"]:
        chart_or_table("Which reminder brought them back", "", list(a["recovered_by_followup"].items()), "Candidates", as_table, keep_order=True)

    st.subheader("Questions Sofía couldn't answer")
    st.caption("Each one is a candidate for the FAQ.")
    if a["unanswered_questions"]:
        for question in a["unanswered_questions"]:
            st.markdown(f"- {question}")
    else:
        st.caption("_None so far._")

    st.subheader("AI health")
    h = st.columns(5)
    h[0].metric("Template fallback rate", ui.pct(a["template_fallback_rate"]), help="Agent messages written by templates because the model failed or was rejected by the guard")
    h[1].metric("LLM errors", a["llm_errors"])
    h[2].metric("Guard rejections", a["guard_rejections"], help="Drafts rejected by the output guard (length, markdown, leaked instructions)")
    h[3].metric("Languages", " · ".join(f"{k.upper()} {v}" for k, v in a["languages"].items()))
    h[4].metric("Spain / Mexico", f'{a["countries"].get("ES", 0)} / {a["countries"].get("MX", 0)}', help="Candidates by country of their delivery city")


client.guarded(page)
