"""Try the agent: play the candidate in the web channel (same API WhatsApp would use)."""

import streamlit as st

import client
import ui


def start(language: str | None) -> None:
    result = client.start_conversation(language)
    st.session_state.chat = {
        "id": result["conversation_id"],
        "messages": [("agent", m["text"]) for m in result["messages"]],
        "quick": result["messages"][-1]["quick_replies"],
        "analysis": None,
        "stage": result["stage"],
        "completed": False,
        "data": result["data"],
    }


def send(text: str) -> None:
    chat = st.session_state.chat
    chat["messages"].append(("candidate", text))
    with st.spinner("Sofía is typing…"):
        result = client.send_message(chat["id"], text)
    chat["messages"] += [("agent", m["text"]) for m in result["messages"]]
    if not result["messages"]:
        chat["messages"].append(("system", "Sofía doesn't reply: the conversation is closed and there was nothing to answer."))
    chat["quick"] = result["messages"][-1]["quick_replies"] if result["messages"] else []
    chat.update(analysis=result["analysis"], stage=result["stage"], completed=result["completed"], data=result["data"])


def page() -> None:
    st.title("Try the agent")
    st.caption("You are the candidate. The web chat calls the same API a WhatsApp webhook or a voice agent would.")
    controls = st.columns([1.2, 1.4, 4], vertical_alignment="bottom")
    language = controls[0].segmented_control("Opening language", ["es", "en"], default="es", format_func=str.upper)
    if controls[1].button("New conversation", icon=":material/add_comment:") or "chat" not in st.session_state:
        start(language)
        st.rerun()

    chat = st.session_state.chat
    talk, side = st.columns([3, 2], gap="large")
    with talk:
        for role, text in chat["messages"]:
            if role == "system":
                st.caption(f"_{text}_")
                continue
            agent = role == "agent"
            with st.chat_message("assistant" if agent else "user", avatar="🛵" if agent else "🙂"):
                st.markdown(text.replace("\n", "  \n") if agent else text)
        if chat["quick"]:
            choice = st.pills("Quick replies", chat["quick"], key=f"quick-{len(chat['messages'])}", label_visibility="collapsed")
            if choice:
                send(choice)
                st.rerun()
        if chat["completed"]:
            st.success(f'Screening finished: {ui.status_label(chat["stage"])}', icon=":material/flag:")
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
        collected = {k: v for k, v in chat["data"].items() if v not in (None, [])}
        st.json(collected or {}, expanded=False)
        st.caption(f'Stage: {chat["stage"]} · conversation {chat["id"][:8]}')

    if prompt := st.chat_input("Write as the candidate…"):
        send(prompt)
        st.rerun()


client.guarded(page)
