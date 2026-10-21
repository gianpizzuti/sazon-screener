"""Candidate: everything a recruiter needs to decide, and why the agent did what it did."""

import json

import pandas as pd
import streamlit as st

import client
import ui

MD_SPECIAL = str.maketrans({c: f"\\{c}" for c in "\\`*_{}[]<>()#+-.!|"})


def as_text(text: str) -> str:
    """Show candidate text literally (no markdown rendering), keeping line breaks."""
    return text.translate(MD_SPECIAL).replace("\n", "  \n")


def field_value(field: str, data: dict) -> str:
    match field:
        case "full_name":
            return data["full_name"] or "–"
        case "drivers_license":
            return {"yes": "Yes", "no": "No", "in_progress": "In progress"}.get(data["license_status"] or "", "–")
        case "location":
            if data["in_service_area"] is False:
                return f'{data["location_raw"]} (outside the service area)'
            return data["city"] or "–"
        case "zone":
            return data["zone"] or "–"
        case "availability":
            return ", ".join(ui.AVAILABILITY[a] for a in data["availability"]) or "–"
        case "schedule":
            return ", ".join(ui.SCHEDULE[s] for s in data["preferred_schedule"]) or "–"
        case "experience_years":
            return ui.experience(data["experience_months"])
        case "experience_platforms":
            return ", ".join(data["experience_platforms"]) or "–"
        case "start_date":
            return ui.short_date(data["start_date"]) if data["start_date"] else "–"
    return "–"


def summary_block(cid: str, summary: dict | None, finished: bool) -> None:
    head, button = st.columns([4, 1.3])
    head.subheader("Summary")
    if button.button("Regenerate", icon=":material/refresh:", disabled=not finished, help="Write the summary again from the latest data"):
        with st.spinner("Writing the summary…"):
            client.regenerate_summary(cid)
        st.rerun()
    if not summary:
        st.caption("The summary is written when the conversation ends." if not finished else "No summary yet: press Regenerate.")
        return
    st.markdown(f"**{summary['headline']}**")
    st.write(summary["summary"])
    good, bad = st.columns(2)
    with good:
        st.markdown("**Strengths**")
        for item in summary["strengths"] or ["–"]:
            st.markdown(f"- {item}")
    with bad:
        st.markdown("**To check**")
        for item in summary["concerns"] or ["–"]:
            st.markdown(f"- {item}")
    if summary.get("candidate_questions"):
        st.markdown("**Candidate's open questions**")
        for item in summary["candidate_questions"]:
            st.markdown(f"- {item}")
    st.info(summary["recommended_action"], icon=":material/assignment_turned_in:")
    if summary.get("source") == "template":
        st.caption("Automatic summary unavailable: fallback summary shown.")


def decision_block(cid: str, row: dict, review: dict) -> None:
    st.subheader("Recruiter decision")
    with st.form("review"):
        options = list(ui.REVIEW)
        status = st.selectbox("Status", options, index=options.index(review["status"]), format_func=ui.REVIEW.get)
        note = st.text_area("Note", value=review["note"], placeholder="e.g. Called, interview Thursday 11:00 at Chamberí")
        by = st.text_input("Your name", value=review["updated_by"] or st.session_state.get("recruiter", ""))
        overriding = (row["status"] in ("disqualified", "withdrawn") and status in ("contacted", "interview", "hired")) or (
            row["status"] == "qualified" and status == "rejected"
        )
        if overriding:
            st.warning("This overrides the automated outcome. It will be logged as a human override.", icon=":material/gavel:")
        if st.form_submit_button("Save decision", type="primary"):
            client.review(cid, status, note, by)
            st.session_state["recruiter"] = by
            st.toast("Decision saved", icon="✅")
            st.rerun()
    if review.get("updated_at"):
        st.caption(f'Last update {ui.ago(review["updated_at"])}{" by " + review["updated_by"] if review["updated_by"] else ""}')


def transcript_block(transcript: list[dict]) -> None:
    st.subheader("Conversation")
    st.caption("Expand any message to see what the agent understood or why it said what it said.")
    for m in transcript:
        agent = m["role"] == "agent"
        with st.chat_message("assistant" if agent else "user", avatar="🛵" if agent else "🙂"):
            st.markdown(as_text(m["text"]))
            meta = m["meta"]
            if agent:
                directive = meta.get("directive") or {}
                st.caption(f'{meta.get("kind", "")} · written by {"the model" if meta.get("source") == "llm" else "a template"}')
                if directive:
                    with st.expander("Why this message"):
                        st.json(directive, expanded=False)
            elif "analysis" in meta:
                a = meta["analysis"]
                extracted = {k: v for k, v in a["extracted"].items() if v not in (None, [])}
                st.caption(f'{", ".join(a["intents"])} · {a["language"]} · {a["sentiment"]}')
                with st.expander("What the agent understood"):
                    st.json({"extracted": extracted, "evidence": a["evidence"], "question": a["question"], "faq_id": a["faq_id"]}, expanded=True)
            elif meta.get("error"):
                st.caption("⚠️ not understood (technical error), candidate asked to repeat")


def page() -> None:
    rows = client.candidates()
    if not rows:
        st.info("No candidates yet. Try the agent from the sidebar.", icon=":material/info:")
        return
    labels = {r["id"]: f'{ui.status_label(r["status"])} · {r["name"] or "Unnamed"} · {r["city"] or "–"}' for r in rows}
    wanted = st.query_params.get("id")
    ids = list(labels)
    cid = st.selectbox("Candidate", ids, index=ids.index(wanted) if wanted in labels else 0, format_func=labels.get)
    st.query_params["id"] = cid

    detail = client.candidate(cid)
    row, data = detail["row"], detail["data"]
    finished = row["status"] not in ("in_progress", "abandoned")

    st.title(row["name"] or "Unnamed candidate")
    badge, info = st.columns([1, 6], vertical_alignment="center")
    with badge:
        ui.status_badge(row["status"])
    place = f'{row["city"]} · {row["zone"]}' if row["zone"] else (row["city"] or "city unknown")
    info.caption(f'{place} · speaks {row["language"].upper()} · via {row["channel"]} · started {ui.ago(row["created_at"])}')
    if row["disqualification_reason"]:
        st.caption(f'Knock-out: **{ui.REASONS.get(row["disqualification_reason"], row["disqualification_reason"])}**'
                   + (f' · talent pool: {"yes" if detail["talent_pool_opt_in"] else "no"}' if detail["talent_pool_opt_in"] is not None else ""))

    left, right = st.columns([3, 2], gap="large")
    with left:
        summary_block(cid, detail["summary"], finished)
        st.subheader("Screening data")
        st.dataframe(
            pd.DataFrame([
                {"Field": ui.FIELD_LABELS[f["field"]], "Value": field_value(f["field"], data),
                 "Status": ui.FIELD_STATUS.get(f["status"], f["status"]), "Candidate's words": f["evidence"] or ""}
                for f in detail["fields"]
            ]),
            hide_index=True, width="stretch",
        )
    with right:
        decision_block(cid, row, detail["review"])
        if detail["flags"]:
            st.subheader("Flags")
            for flag in detail["flags"]:
                st.markdown(f'- ⚑ **{flag["code"].replace("_", " ")}** {flag["detail"].replace("_", " ")}')
        if detail["pending_questions"]:
            st.subheader("Questions Sofía couldn't answer")
            for question in detail["pending_questions"]:
                st.markdown(f"- {as_text(question)}")
        st.download_button(
            "Download JSON (ATS payload)", icon=":material/download:",
            data=json.dumps(detail, ensure_ascii=False, indent=2, default=str),
            file_name=f"candidate-{cid[:8]}.json", mime="application/json",
        )
        with st.popover("Erase candidate data", icon=":material/delete_forever:"):
            st.caption("Right to erasure (GDPR): deletes the transcript, data, summary and audit trail. This cannot be undone.")
            if st.button("Erase permanently", type="primary"):
                client.erase(cid)
                st.query_params.clear()
                st.switch_page("views/pipeline.py")

    transcript_block(detail["transcript"])
    with st.expander("Audit trail"):
        st.dataframe(
            pd.DataFrame([{"When": e["created_at"][:19].replace("T", " "), "Event": e["type"], "Details": json.dumps(e["payload"], ensure_ascii=False)} for e in detail["events"]]),
            hide_index=True, width="stretch",
        )


client.guarded(page)
