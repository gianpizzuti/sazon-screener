"""Export finished demo conversations as readable Markdown samples (samples/*.md).

Highlights are derived from the event log, so each sample states what it demonstrates
without hand-written labels. Only web-channel conversations are exported (terminal
tests are left out), and conversations still in progress are skipped.

    python scripts/export_samples.py
"""

from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

from screener.domain.models import ConversationState
from screener.factory import DEFAULT_DB
from screener.storage.repository import Repository
from screener.views import display_status

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "samples"
STATUS = {
    "qualified": "✅ Qualified", "needs_review": "⚠️ Needs review", "disqualified": "⛔ Disqualified",
    "withdrawn": "↩️ Withdrawn", "abandoned": "💤 Abandoned", "terminated": "🚫 Closed",
}
HIGHLIGHTS = {
    "language_switched": "switches language",
    "question_answered": "asks a question answered from the FAQ",
    "question_unanswered": "asks something not in the FAQ (not improvised, logged for the recruiter)",
    "field_corrected": "corrects an answer",
    "field_reopened": "says a detail is wrong at the recap, the field is asked again",
    "field_invalid": "gives an invalid or ambiguous answer, asked again",
    "field_unclear": "stays unclear after two attempts: flagged, the conversation moves on",
    "human_requested": "asks for a human: flagged, screening continues",
    "abuse_strike": "uses abusive language",
    "knockout": "is knocked out",
    "talent_pool": "answers the talent-pool opt-in",
    "update_after_close": "sends new information after the end",
    "ignored_after_close": "keeps chatting after the end: no endless replies",
}


def slug(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def highlights(events, state: ConversationState, messages, status: str) -> list[str]:
    seen: list[str] = []

    def add(label: str) -> None:
        if label not in seen:
            seen.append(label)

    if state.language == "en" and not any(e.type == "language_switched" for e in events):
        add("talks in English from the start")
    for m in messages:
        analysis = m.meta.get("analysis") if m.role == "candidate" else None
        if not analysis:
            continue
        given = {k for k, v in analysis["extracted"].items() if v not in (None, [])}
        if len({k.split("_")[0] for k in given}) >= 3:
            add("gives several answers in one message: those questions are skipped")
        if analysis["intents"] == ["other"]:
            add("sends off-script messages (non-answers or attempts to steer the agent): no effect on the outcome")
    for e in events:
        label = HIGHLIGHTS.get(e.type)
        if e.type == "sentiment" and e.payload.get("value") == "frustrated":
            label = "gets frustrated: empathy and remaining-question count"
        if e.type == "knockout":
            label = f"is knocked out ({e.payload['reason'].replace('_', ' ')})"
        if e.type == "stage_changed" and e.payload.get("to") == "withdrawn":
            label = "withdraws: accepted gracefully, can come back anytime"
        if label:
            add(label)
    if status == "abandoned":
        add(f"stops replying at {(state.current_field or 'the intro').replace('_', ' ')}: recorded as drop-off")
    if any(f.code == "late_start" for f in state.flags):
        add("starts in more than 90 days: flagged")
    if state.language == "es" and state.spanish_variant == "es-MX":
        add("Mexican Spanish vocabulary")
    return seen


def render(state: ConversationState, status: str, messages, events, summary: dict | None) -> str:
    name = state.data.full_name or "Unnamed candidate"
    candidate_turns = sum(1 for m in messages if m.role == "candidate")
    lines = [
        f"# {name} · {STATUS.get(status, status)}",
        "",
        f"**Language:** {state.language.upper()} · **Candidate messages:** {candidate_turns}"
        + (f" · **City:** {state.data.city}" if state.data.city else ""),
        "",
        "**What this conversation shows:** the candidate " + "; ".join(highlights(events, state, messages, status) or ["completes the screening without issues"]) + ".",
        "",
        "## Conversation",
        "",
    ]
    for m in messages:
        who = "🛵 **Sofía**" if m.role == "agent" else "🙂 **Candidate**"
        text = m.text.replace("\n", "  \n> ")
        source = " _(template)_" if m.role == "agent" and m.meta.get("source") == "template" else ""
        lines += [f"{who}{source}", f"> {text}", ""]
    if status == "abandoned":
        lines += ["_The candidate stopped replying here._", ""]
    data = {k: v for k, v in state.data.model_dump(mode="json").items() if v not in (None, [])}
    lines += ["## Structured data", "", "```json", json.dumps(data, ensure_ascii=False, indent=2), "```", ""]
    if summary and summary.get("source") == "llm":
        lines += [
            "## Recruiter summary (generated after the conversation)",
            "",
            f"**{summary['headline']}**",
            "",
            summary["summary"],
            "",
            "**Strengths:** " + "; ".join(summary["strengths"]) if summary["strengths"] else "",
            "",
            "**To check:** " + "; ".join(summary["concerns"]) if summary["concerns"] else "",
            "",
            f"**Recommended action:** {summary['recommended_action']}",
            "",
        ]
    return "\n".join(lines)


def main() -> None:
    repo = Repository(DEFAULT_DB)
    OUT.mkdir(exist_ok=True)
    index = ["# Sample conversations", "",
             "Real conversations with the agent (real models, real policy), generated by `scripts/seed_demo.py` "
             "and exported by `scripts/export_samples.py`. Each file shows the transcript, the structured data "
             "extracted and the recruiter summary.", "",
             "| Sample | Outcome | What it shows |", "|---|---|---|"]
    exported = 0
    for row in sorted(repo.conversations(), key=lambda r: r.created_at):
        state = ConversationState.model_validate(row.state)
        status = display_status(state, max(r.updated_at for r in repo.conversations()))
        if state.channel != "web" or status == "in_progress":
            continue
        events, messages = repo.events(state.id), repo.messages(state.id)
        exported += 1
        filename = f"{exported:02d}-{slug(state.data.full_name or 'candidate')}-{status}.md"
        (OUT / filename).write_text(render(state, status, messages, events, row.summary), encoding="utf-8")
        shows = "; ".join(highlights(events, state, messages, status)) or "completes the screening without issues"
        index.append(f"| [{state.data.full_name or 'Unnamed'}]({filename}) | {STATUS.get(status, status)} | {shows} |")
    (OUT / "README.md").write_text("\n".join(index) + "\n", encoding="utf-8")
    print(f"exported {exported} conversations to {OUT}")


if __name__ == "__main__":
    main()
