"""Exploratory conversations: fixed candidate messages, real engine and models, read by a person.

    python -m evals.explore                  # every scenario in exploratory.yaml (~0.03 USD each)
    python -m evals.explore --only ex04 ex18

Writes evals/results/exploratory/<id>.md (each turn with what the model read and what the rules
decided) and evals/results/exploratory/README.md (quick triage against `expect`).
"""

from __future__ import annotations

import argparse
import json
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta

import yaml

from evals.common import EVALS, NOW, RESULTS, UsageMeter, load_config
from screener.domain.text import normalize
from screener.engine.engine import ScreeningEngine
from screener.knowledge import build_knowledge
from screener.llm.claude import ClaudeResponder, ClaudeUnderstander
from screener.storage.repository import Repository

SCENARIOS_FILE = EVALS / "exploratory.yaml"
OUT = RESULTS / "exploratory"


def run(scenario: dict) -> dict:
    cfg = load_config()
    meter = UsageMeter()
    client = meter.client()
    clock = {"now": NOW}
    engine = ScreeningEngine(
        config=cfg, repository=Repository("sqlite://"), understander=ClaudeUnderstander(client, cfg),
        responder=ClaudeResponder(client, cfg), summarizer=None, clock=lambda: clock["now"],
        knowledge=build_knowledge(cfg),
    )
    result = engine.start(channel="eval", language=scenario.get("start_language"), country=scenario.get("country"))
    cid = result.conversation_id
    turns = [{"role": "agent", "text": m.text, "buttons": m.quick_replies} for m in result.messages]
    for text in scenario["messages"]:
        clock["now"] += timedelta(seconds=40)
        result = engine.handle(cid, text)
        a = result.analysis
        note = ""
        if a:
            values = {k: v for k, v in a.extracted.model_dump(mode="json").items() if v not in (None, [], "")}
            note = ", ".join(a.intents) + (f" · {json.dumps(values, ensure_ascii=False)}" if values else "")
            if a.faq_id:
                note += f" · faq={a.faq_id}"
            if a.chosen_option:
                note += f" · option={a.chosen_option}"
        turns.append({"role": "candidate", "text": text, "note": note, "events": result.event_types})
        turns += [{"role": "agent", "text": m.text, "buttons": m.quick_replies} for m in result.messages]
    state = engine.repo.get_state(cid)
    return {"scenario": scenario, "turns": turns, "state": state.model_dump(mode="json"), "usd": meter.total_usd()}


def triage(scenario: dict, state: dict) -> list[str]:
    """Differences from `expect` (a quick first look; the transcript is what matters)."""
    exp, d, iv = scenario.get("expect", {}), state["data"], state.get("interview") or {}
    problems = []
    checks = {
        "stage": state["stage"], "interview": iv.get("status"), "city_id": d.get("city_id"), "zone": d.get("zone"),
        "availability": d.get("availability"), "start_date": d.get("start_date"), "license_type": d.get("license_type"),
        "experience_months": d.get("experience_months"),
    }
    for key, want in exp.items():
        if key == "flag":
            if not any(f["code"] == want for f in state["flags"]):
                problems.append(f"flag {want} missing")
        elif key == "zone":
            if normalize(str(checks["zone"])) != normalize(str(want)):
                problems.append(f"zone: expected {want}, got {checks['zone']}")
        elif checks.get(key) != want:
            problems.append(f"{key}: expected {want}, got {checks.get(key)}")
    return problems


def transcript_md(r: dict, problems: list[str]) -> str:
    sc, st = r["scenario"], r["state"]
    lines = [f"# {sc['id']}", "", f"**End:** {st['stage']}"
             + (f" · interview {st['interview']['status']}" if st.get("interview") else "")
             + (f" · triage: {'; '.join(problems)}" if problems else " · triage: as expected"), ""]
    for t in r["turns"]:
        if t["role"] == "agent":
            buttons = f"  \n  `[{' | '.join(t['buttons'])}]`" if t.get("buttons") else ""
            lines.append(f"- **Sofía:** {t['text']}{buttons}")
        else:
            lines.append(f"- *Candidate:* {t['text']}  \n  <sub>{t['note']}{' · events: ' + ', '.join(t['events']) if t['events'] else ''}</sub>")
    data = {k: v for k, v in st["data"].items() if v not in (None, [], "")}
    lines += ["", f"**Data:** `{json.dumps(data, ensure_ascii=False)}`"]
    if st["flags"]:
        lines.append("**Flags:** " + ", ".join(f["code"] for f in st["flags"]))
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--only", nargs="+", help="scenario ids or prefixes")
    args = parser.parse_args()
    scenarios = yaml.safe_load(SCENARIOS_FILE.read_text())
    if args.only:
        scenarios = [s for s in scenarios if any(s["id"].startswith(o) for o in args.only)]
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(run, scenarios))
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for r in results:
        problems = triage(r["scenario"], r["state"])
        (OUT / f"{r['scenario']['id']}.md").write_text(transcript_md(r, problems))
        rows.append(f"| [`{r['scenario']['id']}`]({r['scenario']['id']}.md) | {r['state']['stage']} | {'; '.join(problems) or '✓'} |")
        print(f"{r['scenario']['id']}: {r['state']['stage']} {'; '.join(problems) or 'ok'}")
    if not args.only:
        index = ["# Exploratory conversations", "",
                 f"Run {datetime.now():%Y-%m-%d %H:%M} · {len(results)} scenarios · ${sum(r['usd'] for r in results):.2f}. "
                 "Triage compares the end state with `expect`; each transcript was read by a person.", "",
                 "| Scenario | End | Triage |", "|---|---|---|", *rows]
        (OUT / "README.md").write_text("\n".join(index) + "\n")
    print(f"cost ${sum(r['usd'] for r in results):.3f}")


if __name__ == "__main__":
    main()
