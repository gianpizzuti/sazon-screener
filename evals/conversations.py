"""Conversation eval: simulated candidates screened end to end by the real engine.

A model plays each persona in personas.yaml (only from its brief and facts); the engine screens
it with the production models and rules. Deterministic checks compare the end state with what the
persona's facts imply; evals/judge.py then rates the agent's side of each transcript.

    python -m evals.conversations                  # all personas, then the judge
    python -m evals.conversations --only p01 p08   # some personas (ids or prefixes)
    python -m evals.conversations --no-judge

Writes evals/results/conversations/<persona>.md, evals/results/conversations.json and
evals/results/conversations.md.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta

import anthropic
import yaml

from evals.common import EVALS, MODELS, NOW, RESULTS, UsageMeter, load_config, pct
from screener.domain.text import function_word_language, normalize
from screener.engine.engine import ScreeningEngine
from screener.knowledge import build_knowledge
from screener.llm.claude import ClaudeResponder, ClaudeSummarizer, ClaudeUnderstander
from screener.storage.repository import Repository

PERSONAS_FILE = EVALS / "personas.yaml"
OUT = RESULTS / "conversations"
SIMULATOR = MODELS["haiku"]  # restating given facts in a given style is a narrow task (D152)
MAX_CANDIDATE_MESSAGES = 25
END = "[END]"
# Things the agent must never say (promises or invented terms). The judge looks for subtler ones.
FORBIDDEN = re.compile(r"(estás contratad|quedas contratad|you'?re hired|you are hired|\d+\s?(€|euros|pesos)|\$\s?\d)", re.I)


def load_personas() -> list[dict]:
    return yaml.safe_load(PERSONAS_FILE.read_text())


# ------------------------------------------------------------------ the simulated candidate
def simulator_system(p: dict) -> str:
    facts = "\n".join(f"- {k}: {v}" for k, v in p["facts"].items())
    return f"""You are role-playing a job applicant, to test a recruiting chatbot. You chat on WhatsApp with \
Sofía, the virtual assistant of Grupo Sazón, a restaurant chain hiring delivery drivers. Today is \
Tuesday 20 October 2026.

# Your character
{p["brief"].strip()}

# Your facts: the only facts you may use. Never invent others; if asked something not covered, give a short plausible answer consistent with them.
{facts}

# How to write
- Like a real person on WhatsApp: {p.get("style", "short and informal")}.
- Answer what the assistant asks. Volunteer extra information only if your character says so.
- Reply with the message text only: no quotes, no stage directions, no explanations.
- When the assistant has clearly finished (said goodbye, or explained the next step) and asks nothing more, reply exactly {END}"""


def simulate(client: anthropic.Anthropic, system: str, history: list[dict]) -> str:
    response = client.messages.create(
        model=SIMULATOR, max_tokens=400, system=system, messages=history, output_config={"effort": "low"},
    )
    return "".join(b.text for b in response.content if b.type == "text").strip()


# ------------------------------------------------------------------ one conversation
def run_persona(p: dict) -> dict:
    cfg = load_config()
    engine_meter, sim_meter = UsageMeter(), UsageMeter()
    client = engine_meter.client()
    clock = {"now": NOW}
    engine = ScreeningEngine(
        config=cfg,
        repository=Repository("sqlite://"),  # in memory, one per persona
        understander=ClaudeUnderstander(client, cfg),
        responder=ClaudeResponder(client, cfg),
        summarizer=ClaudeSummarizer(client, cfg),
        clock=lambda: clock["now"],
        knowledge=build_knowledge(cfg),
    )
    sim_client, system = sim_meter.client(), simulator_system(p)

    result = engine.start(channel="eval", language=p.get("start_language"), country=p.get("country"))
    cid = result.conversation_id
    history = [{"role": "user", "content": "\n\n".join(m.text for m in result.messages)}]
    sent, after_end, simulator_error = 0, 0, None
    while sent < MAX_CANDIDATE_MESSAGES:
        try:
            reply = simulate(sim_client, system, history)
        except anthropic.APIError as exc:
            simulator_error = str(exc)[:200]
            break
        if not reply or END in reply:
            break
        history.append({"role": "assistant", "content": reply})
        clock["now"] += timedelta(seconds=40)
        result = engine.handle(cid, reply)
        sent += 1
        if not result.messages:
            break  # the agent stays silent after the end: nothing more to say
        history.append({"role": "user", "content": "\n\n".join(m.text for m in result.messages)})
        if result.completed:
            after_end += 1
            if after_end > 2:
                break
    summary = engine.summarize(cid) if engine.repo.get_state(cid).is_terminal else None

    state = engine.repo.get_state(cid)
    rows = engine.repo.messages(cid)
    events = engine.repo.events(cid)
    messages = [{"role": r.role, "text": r.text, "meta": r.meta or {}} for r in rows]
    return {
        "id": p["id"],
        "state": state.model_dump(mode="json"),
        "messages": messages,
        "events": [e.type for e in events],
        "summary": summary,
        "candidate_messages": sent,
        "simulator_error": simulator_error,
        "usage": {"engine": engine_meter.by_model(), "simulator": sim_meter.by_model()},
        "usd": {"engine": round(engine_meter.total_usd(), 4), "simulator": round(sim_meter.total_usd(), 4)},
    }


# ------------------------------------------------------------------ deterministic checks
def same_value(key: str, want, got) -> bool:
    if key == "full_name":
        return got is not None and normalize(got) == normalize(want)
    if key in ("availability", "preferred_schedule"):
        return set(got or []) == set(want)
    if key == "experience_platforms":
        g, o = [normalize(x) for x in want], [normalize(x) for x in got or []]
        return len(g) == len(o) and all(any(a in b or b in a for b in o) for a in g)
    return got == want


def check(p: dict, run: dict, char_limit: int) -> dict:
    exp, st = p["expect"], run["state"]
    checks: dict[str, bool] = {"outcome": st["stage"] == exp["stage"]}
    if "reason" in exp:
        checks["knock-out reason"] = st["disqualification_reason"] == exp["reason"]
    if "talent_pool" in exp:
        checks["talent pool answer"] = st["talent_pool_opt_in"] == exp["talent_pool"]
    data_ok = {k: same_value(k, v, st["data"].get(k)) for k, v in (exp.get("data") or {}).items()}
    if data_ok:
        checks["data"] = all(data_ok.values())
    for flag in exp.get("flags", []):
        checks[f"flag {flag}"] = any(f["code"] == flag for f in st["flags"])
    for event, n in (exp.get("events") or {}).items():
        checks[f"{event} ≥ {n}"] = run["events"].count(event) >= n
    checks["within turn budget"] = run["candidate_messages"] <= exp["max_turns"]
    agent = [m for m in run["messages"] if m["role"] == "agent"]
    llm = [m for m in agent if m["meta"].get("source") == "llm"]
    lang = p.get("language", "es")
    signals = [function_word_language(m["text"]) for m in llm]
    wrong_language = [m["text"] for m, s in zip(llm, signals) if s and s != lang]
    checks["replies in the candidate's language"] = not wrong_language
    forbidden = [m["text"] for m in agent if FORBIDDEN.search(m["text"])]
    checks["no promises or invented figures"] = not forbidden
    checks["no model errors"] = "llm_error" not in run["events"]
    fallbacks = [m for m in agent if m["meta"].get("source") == "template" and m["meta"].get("kind") not in ("greeting", "recap")]
    return {
        "checks": checks,
        "ok": all(checks.values()),
        "data_fields": data_ok,
        "wrong_language": wrong_language,
        "forbidden": forbidden,
        "template_fallbacks": len(fallbacks),
        "guard_rejections": run["events"].count("guard_rejected"),
        "longest_message": max((len(m["text"]) for m in llm), default=0),
        "char_limit": char_limit,
    }


# ------------------------------------------------------------------ outputs
def transcript_md(p: dict, run: dict, result: dict) -> str:
    st = run["state"]
    lines = [f"# {p['id']}", "", f"> {p['brief'].strip()}", "",
             f"**Expected:** {p['expect']['stage']} · **Got:** {st['stage']}"
             + (f" ({st['disqualification_reason']})" if st["disqualification_reason"] else "")
             + f" · **Checks:** {'all passed' if result['ok'] else ', '.join(k for k, v in result['checks'].items() if not v) + ' failed'}",
             "", "| | Message | |", "|---|---|---|"]
    for m in run["messages"]:
        text = m["text"].replace("\n", "<br>").replace("|", "\\|")
        if m["role"] == "agent":
            lines.append(f"| **Sofía** | {text} | `{m['meta'].get('source', '')}` |")
        else:
            a = (m["meta"] or {}).get("analysis") or {}
            got = ", ".join(f"{k}={v}" for k, v in (a.get("extracted") or {}).items() if v not in (None, [], ""))
            note = " · ".join(x for x in [",".join(a.get("intents", [])), got] if x)
            lines.append(f"| *Candidate* | {text} | {note} |")
    lines += ["", "**Screening data:** `" + json.dumps({k: v for k, v in st["data"].items() if v not in (None, [], "")}, ensure_ascii=False) + "`"]
    if st["flags"]:
        lines.append("**Flags:** " + ", ".join(f["code"] for f in st["flags"]))
    if run.get("summary"):
        lines += ["", "**Recruiter summary:** " + run["summary"].get("summary", "")]
    if run.get("judge"):
        j = run["judge"]
        lines += ["", "**Judge:** " + " · ".join(f"{k} {v['score']}/5" for k, v in j["scores"].items())]
        lines += [f"- {i}" for i in j.get("issues", [])]
    return "\n".join(lines) + "\n"


def write_report(personas: list[dict], runs: list[dict]) -> None:
    by_id = {p["id"]: p for p in personas}
    passed = sum(r["result"]["ok"] for r in runs)
    engine_usd = sum(r["usd"]["engine"] for r in runs)
    sim_usd = sum(r["usd"]["simulator"] for r in runs)
    judge_usd = sum(r.get("judge_usd", 0) for r in runs)
    screened = [r for r in runs if r["state"]["stage"] in ("qualified", "needs_review")]
    per_full = sum(r["usd"]["engine"] for r in screened) / max(1, len(screened))
    lines = [
        "# Conversation eval",
        "",
        f"{len(runs)} simulated candidates (`evals/personas.yaml`), each played by `{SIMULATOR}` from a brief and a list of facts,",
        "screened end to end by the production engine (real models, real rules). Deterministic checks compare the end",
        "state with what the persona's facts imply; an Opus judge rates the agent's messages (`evals/judge.py`).",
        "Generated by `python -m evals.conversations`; transcripts in [`conversations/`](conversations/).",
        "",
        "## Summary",
        "",
        "| | |",
        "|---|---|",
        f"| Conversations passing every check | **{passed}/{len(runs)}** |",
        f"| Outcome as expected | {sum(r['result']['checks']['outcome'] for r in runs)}/{len(runs)} |",
        f"| Screening data exactly right | {sum(r['result']['checks'].get('data', True) for r in runs)}/{len(runs)} |",
        f"| Candidate messages per conversation (median) | {sorted(r['candidate_messages'] for r in runs)[len(runs) // 2]} |",
        f"| Agent messages written by the model / by templates (fallbacks) | "
        f"{sum(1 for r in runs for m in r['messages'] if m['role'] == 'agent' and m['meta'].get('source') == 'llm')} / "
        f"{sum(r['result']['template_fallbacks'] for r in runs)} |",
        f"| Output-guard rejections | {sum(r['result']['guard_rejections'] for r in runs)} |",
        f"| Engine cost per complete screening | ${per_full:.3f} (≈ ${per_full * 1000:.0f} per 1,000 complete screenings) |",
        f"| Cost of this run: engine / simulator / judge | ${engine_usd:.2f} / ${sim_usd:.2f} / ${judge_usd:.2f} |",
    ]
    judged = [r for r in runs if r.get("judge")]
    if judged:
        dims = list(judged[0]["judge"]["scores"])
        lines += ["", "## Judge scores (1-5)", "", "| Persona | " + " | ".join(d.replace("_", " ") for d in dims) + " |",
                  "|---|" + "---|" * len(dims)]
        for r in judged:
            lines.append(f"| `{r['id']}` | " + " | ".join(str(r["judge"]["scores"][d]["score"]) for d in dims) + " |")
        lines.append("| **Mean** | " + " | ".join(f"**{sum(r['judge']['scores'][d]['score'] for r in judged) / len(judged):.1f}**" for d in dims) + " |")
        cal = runs[0].get("calibration")
        if cal:
            lines += ["", "**Judge calibration** (hand-written control transcripts, `evals/judge_controls.yaml`): " + "; ".join(cal)]
    lines += ["", "## Checks by persona", "", "| Persona | Expected | Got | Turns | Failed checks | Cost |", "|---|---|---|---|---|---|"]
    for r in runs:
        p, res, st = by_id[r["id"]], r["result"], r["state"]
        failed = ", ".join(k for k, v in res["checks"].items() if not v) or "–"
        if res["data_fields"] and not all(res["data_fields"].values()):
            failed += " (" + ", ".join(k for k, v in res["data_fields"].items() if not v) + ")"
        lines.append(f"| [`{r['id']}`](conversations/{r['id']}.md) | {p['expect']['stage']} | {st['stage']} | "
                     f"{r['candidate_messages']}/{p['expect']['max_turns']} | {failed} | ${r['usd']['engine']:.3f} |")
    issues = [(r["id"], i) for r in judged for i in r["judge"].get("issues", [])]
    if issues:
        lines += ["", "## Issues raised by the judge", ""] + [f"- `{pid}`: {i}" for pid, i in issues]
    sim = [(r["id"], i) for r in judged for i in r["judge"].get("simulator_problems", [])]
    if sim:
        lines += ["", "## Simulator problems (test artefacts, not agent errors)", ""] + [f"- `{pid}`: {i}" for pid, i in sim]
    (RESULTS / "conversations.md").write_text("\n".join(lines) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--only", nargs="+", help="persona ids or prefixes (p01 p08 ...)")
    parser.add_argument("--no-judge", action="store_true")
    args = parser.parse_args()
    personas = load_personas()
    if args.only:
        personas = [p for p in personas if any(p["id"].startswith(o) for o in args.only)]
    cfg = load_config()
    with ThreadPoolExecutor(max_workers=4) as pool:
        runs = list(pool.map(run_persona, personas))
    for p, run in zip(personas, runs):
        run["result"] = check(p, run, cfg.agent.max_message_chars)
    if not args.no_judge:
        from evals.judge import calibrate, judge_runs
        judge_runs(personas, runs)
        calibration = calibrate()
        runs[0]["calibration"] = calibration
    OUT.mkdir(parents=True, exist_ok=True)
    for p, run in zip(personas, runs):
        (OUT / f"{p['id']}.md").write_text(transcript_md(p, run, run["result"]))
    meta = {"run_at": datetime.now().isoformat(timespec="seconds"),
            "commit": subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, cwd=EVALS).stdout.strip()}
    (RESULTS / "conversations.json").write_text(json.dumps({**meta, "runs": runs}, ensure_ascii=False, indent=1, default=str) + "\n")
    write_report(personas, runs)
    for run in runs:
        res = run["result"]
        print(f"{run['id']}: {run['state']['stage']} {'OK' if res['ok'] else 'FAIL ' + str([k for k, v in res['checks'].items() if not v])}"
              f" turns={run['candidate_messages']} ${run['usd']['engine']:.3f}")
    print(f"passed {sum(r['result']['ok'] for r in runs)}/{len(runs)}; see {RESULTS / 'conversations.md'}")


if __name__ == "__main__":
    main()
