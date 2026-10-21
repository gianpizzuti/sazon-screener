"""Recruiter dashboard for Grupo Sazón. Run with `make run` (starts the API too)."""

import streamlit as st

st.set_page_config(page_title="Sazón Screener", page_icon="🛵", layout="wide")

pages = [
    st.Page("views/pipeline.py", title="Pipeline", icon=":material/groups:", default=True),
    st.Page("views/candidate.py", title="Candidate", icon=":material/person:"),
    st.Page("views/analytics.py", title="Analytics", icon=":material/insights:"),
    st.Page("views/chat.py", title="Try the agent", icon=":material/chat:"),
]
navigation = st.navigation(pages)
with st.sidebar:
    st.caption("**Grupo Sazón** · delivery-driver screening")
    st.caption("Screening by Sofía (AI). Every outcome can be overridden by a recruiter.")
navigation.run()
