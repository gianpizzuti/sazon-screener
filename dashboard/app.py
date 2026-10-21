"""Recruiter dashboard for Grupo Sazón. Run with `make run` (starts the API too)."""

import streamlit as st

import client

st.set_page_config(page_title="Sazón Screener", page_icon="🛵", layout="wide")

pages = [
    st.Page("views/pipeline.py", title="Pipeline", icon=":material/groups:", default=True),
    st.Page("views/candidate.py", title="Candidate", icon=":material/person:"),
    st.Page("views/analytics.py", title="Analytics", icon=":material/insights:"),
    st.Page("views/chat.py", title="Try the agent", icon=":material/chat:"),
]
navigation = st.navigation(pages)
try:
    st.session_state["server_now"] = client.server_now()
    demo = client.demo_clock()
except client.ApiUnavailable:
    demo = None

with st.sidebar:
    st.caption("**Grupo Sazón** · delivery-driver screening")
    st.caption("Screening by Sofía (AI). Every outcome can be overridden by a recruiter.")
    if demo is not None:
        st.divider()
        st.markdown("**Demo clock**")
        shown = st.session_state["server_now"][:16].replace("T", " ")
        st.caption(f"Simulated time: {shown} UTC" + (f" (+{demo['offset_hours']:g} h)" if demo["offset_hours"] else ""))
        st.caption("Moves time forward for everyone, so follow-ups go out as they would in real life.")
        cols = st.columns(3)
        for col, (label, hours) in zip(cols, [("+2 h", 2), ("+1 day", 24), ("+3 days", 72)]):
            if col.button(label, width="stretch"):
                with st.spinner("Time passes…"):
                    result = client.advance(hours)
                sent = sum(1 for a in result["actions"] if a["action"] == "followup")
                gave_up = sum(1 for a in result["actions"] if a["action"] == "abandoned")
                st.session_state["flash"] = f"{sent} follow-up(s) sent, {gave_up} candidate(s) marked abandoned"
                st.rerun()
if flash := st.session_state.pop("flash", None):
    st.toast(flash, icon="⏳")
navigation.run()
