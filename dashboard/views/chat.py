"""Try the agent: play the candidate in the web channel (same API WhatsApp would use)."""

import streamlit as st

import client
import ui


def start(language: str | None) -> None:
    result = client.start_conversation(language)
    st.session_state.chat = {"id": result["conversation_id"], "quick": result["messages"][-1]["quick_replies"],
                             "analysis": None, "silent": False}


def send(text: str) -> None:
    chat = st.session_state.chat
    with st.spinner("Sofía is typing…"):
        result = client.send_message(chat["id"], text)
    chat["quick"] = result["messages"][-1]["quick_replies"] if result["messages"] else []
    chat["analysis"], chat["silent"] = result["analysis"], not result["messages"]


def page() -> None:
    st.title("Try the agent")
    st.caption("You are the candidate. The web chat calls the same API a WhatsApp webhook or a voice agent would. "
               "Stop replying and use the demo clock in the sidebar to see the follow-ups.")
    controls = st.columns([1.2, 1.4, 4], vertical_alignment="bottom")
    language = controls[0].segmented_control("Opening language", ["es", "en"], default="es", format_func=str.upper)
    if controls[1].button("Start a conversation" if "chat" not in st.session_state else "New conversation",
                          icon=":material/add_comment:", type="primary" if "chat" not in st.session_state else "secondary"):
        start(language)  # only on click: visiting the page must not create candidates in the pipeline
        st.rerun()
    if "chat" not in st.session_state:
        st.info("Start a conversation to receive Sofía's first message, as a candidate would after applying.", icon=":material/chat:")
        return

    chat = st.session_state.chat
    detail = client.candidate(chat["id"])  # the transcript lives in the API: follow-ups show up too
    row, transcript = detail["row"], detail["transcript"]
    talk, side = st.columns([3, 2], gap="large")
    with talk:
        for m in transcript:
            agent = m["role"] == "agent"
            with st.chat_message("assistant" if agent else "user", avatar="🛵" if agent else "🙂"):
                st.markdown(m["text"].replace("\n", "  \n") if agent else m["text"])
                if m["meta"].get("kind") == "followup":
                    st.caption(f'⏳ automatic follow-up {m["meta"]["attempt"]} (you went silent)')
        if chat["silent"]:
            st.caption("_Sofía doesn't reply: the conversation is closed and there was nothing to answer._")
        last_is_agent = transcript and transcript[-1]["role"] == "agent" and transcript[-1]["meta"].get("kind") != "followup"
        if chat["quick"] and last_is_agent:
            choice = st.pills("Quick replies", chat["quick"], key=f"quick-{len(transcript)}", label_visibility="collapsed")
            if choice:
                send(choice)
                st.rerun()
        if row["status"] not in ("in_progress", "awaiting_reply", "abandoned"):
            st.success(f'Screening finished: {ui.status_label(row["status"])}', icon=":material/flag:")
            if st.button("Open in the recruiter view", icon=":material/open_in_new:"):
                st.switch_page("views/candidate.py", query_params={"id": chat["id"]})

    with side:
        st.subheader("What the agent understood")
        a = chat["analysis"]
        if a:
            st.caption(f'Intents: {", ".join(a["intents"]) or "–"} · language: {a["language"]}'
                       f'{" (clear)" if a["language_is_clear"] else " (no signal)"} · sentiment: {a["sentiment"]}')
            extracted = {k: v for k, v in a["extracted"].items() if v not in (None, [])}
            st.json({"extracted": extracted, "evidence": a["evidence"], "faq_id": a["faq_id"]}, expanded=True)
        else:
            st.caption("Send a message to see how it is interpreted.")
        st.subheader("Collected so far")
        collected = {k: v for k, v in detail["data"].items() if v not in (None, [])}
        st.json(collected or {}, expanded=False)
        st.caption(f'Status: {ui.status_label(row["status"])} · conversation {chat["id"][:8]}')

    if prompt := st.chat_input("Write as the candidate…"):
        send(prompt)
        st.rerun()


client.guarded(page)
