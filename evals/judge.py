"""LLM judge for the conversation eval: rates the agent's side of each transcript.

Deterministic checks (evals/conversations.py) cover what code can verify: outcome, data, turns,
language signals, forbidden phrases. The judge covers what it cannot: tone, clarity, whether a
question was handled well, whether the recruiter summary is faithful.

The judge is the most capable model (Opus 5.5) and is itself checked: two hand-written control
transcripts, one deliberately bad and one good, must land at the bottom and top of the scale.
"""

from __future__ import annotations

import json

import yaml
from pydantic import BaseModel, Field

from evals.common import EVALS, MODELS, UsageMeter

JUDGE = MODELS["opus"]
CONTROLS_FILE = EVALS / "judge_controls.yaml"


class Score(BaseModel):
    score: int = Field(description="1 to 5")
    reason: str = Field(description="One sentence, quoting the transcript where useful.")


class Judgement(BaseModel):
    warmth: Score
    clarity: Score
    brevity: Score
    language: Score
    honesty: Score
    handling: Score
    summary_faithful: Score
    issues: list[str] = Field(description="Specific problems in the assistant's messages or the summary, quoting them. At most 5; empty if none.")
    simulator_problems: list[str] = Field(description="Where the CANDIDATE side was unrealistic or contradicted its facts (test artefacts). Empty if none.")


SYSTEM = """You review conversations of a recruiting chatbot, Sofía, the virtual (AI) assistant of Grupo Sazón, a \
restaurant chain in Spain and Mexico that hires delivery drivers. Sofía screens applicants over WhatsApp: a rules \
engine decides what to ask and the outcome; Sofía phrases each message. The greeting and the final recap of the \
candidate's data are fixed templates. After the conversation, a recruiter summary is written by another model.

Rate ONLY Sofía's messages (and, for summary_faithful, the recruiter summary). Never rate the candidate. \
The outcome itself (qualified, disqualified...) is decided by rules: do not rate whether you agree with it.

Rubric, 1 to 5. Be strict: 5 means you would not change anything; 3 means acceptable with clear flaws.
- warmth: 5 warm, respectful and human, informal "tú" in Spanish; 3 correct but flat, robotic or over-formal; 1 cold, rude or salesy.
- clarity: 5 every message is easy to answer, one question at a time, options when useful; 3 sometimes several questions or vague; 1 confusing.
- brevity: 5 WhatsApp-short (1-3 sentences) throughout; 3 several messages longer than needed; 1 walls of text.
- language: 5 always the candidate's language and regional vocabulary (Spain: carnet, coche, jornada completa; Mexico: licencia, carro, tiempo completo); 3 an occasional slip; 1 the wrong language.
- honesty: 5 no invented facts and no promises (job, salary, interview date) beyond the next step stated, and it says it is an AI; 1 invents terms or promises a job.
- handling: 5 questions, complaints, corrections, manipulation attempts and requests for a person are all handled well; 3 handled but clumsily; 1 mishandled. If none of these happened, rate how smoothly the flow went.
- summary_faithful: 5 the summary matches the transcript and the data, nothing invented or missing that matters; 1 wrong or invented facts. If there is no summary, give 3 and say so."""


def _transcript(messages: list[dict]) -> str:
    lines = []
    for i, m in enumerate(messages, 1):
        who = "SOFÍA" if m["role"] == "agent" else "CANDIDATE"
        lines.append(f"{i}. {who}: {m['text']}")
    return "\n".join(lines)


def judge_one(client, facts: dict, messages: list[dict], outcome: str, data: dict, summary: dict | None) -> Judgement:
    prompt = (
        f"<candidate_facts>\n{json.dumps(facts, ensure_ascii=False, indent=1)}\n</candidate_facts>\n\n"
        f"<transcript>\n{_transcript(messages)}\n</transcript>\n\n"
        f"<outcome>{outcome}</outcome>\n"
        f"<screening_data>\n{json.dumps(data, ensure_ascii=False)}\n</screening_data>\n\n"
        f"<recruiter_summary>\n{json.dumps(summary, ensure_ascii=False, indent=1) if summary else '(none)'}\n</recruiter_summary>\n\n"
        "Rate this conversation."
    )
    response = client.messages.parse(
        model=JUDGE, max_tokens=8000, system=SYSTEM, messages=[{"role": "user", "content": prompt}],
        output_format=Judgement, output_config={"effort": "medium"},
    )
    return response.parsed_output


def _scores(j: Judgement) -> dict:
    d = j.model_dump()
    return {
        "scores": {k: v for k, v in d.items() if isinstance(v, dict) and "score" in v},
        "issues": d["issues"],
        "simulator_problems": d["simulator_problems"],
    }


def judge_runs(personas: list[dict], runs: list[dict]) -> None:
    from concurrent.futures import ThreadPoolExecutor

    by_id = {p["id"]: p for p in personas}

    def one(run: dict) -> None:
        meter = UsageMeter()
        st = run["state"]
        data = {k: v for k, v in st["data"].items() if v not in (None, [], "")}
        try:
            j = judge_one(meter.client(timeout=180), by_id[run["id"]]["facts"], run["messages"], st["stage"], data, run.get("summary"))
            run["judge"] = _scores(j)
        except Exception as exc:  # a failed judgement must not lose the conversation results
            run["judge_error"] = str(exc)[:300]
        run["judge_usd"] = round(meter.total_usd(), 4)

    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(one, runs))


def calibrate() -> list[str]:
    """Run the judge on the control transcripts and say whether each landed where it should."""
    meter, client = UsageMeter(), None
    client = meter.client(timeout=180)
    lines = []
    for control in yaml.safe_load(CONTROLS_FILE.read_text()):
        messages = [{"role": "agent" if who == "sofia" else "candidate", "text": text}
                    for turn in control["transcript"] for who, text in turn.items()]
        j = _scores(judge_one(client, control["facts"], messages, control["outcome"], control["data"], control.get("summary")))
        scores = {k: v["score"] for k, v in j["scores"].items()}
        want = control["expect"]
        ok = all(scores[k] <= v for k, v in want.get("at_most", {}).items()) and all(scores[k] >= v for k, v in want.get("at_least", {}).items())
        lines.append(f"{control['id']}: " + ", ".join(f"{k} {v}" for k, v in scores.items()) + (" ✓" if ok else " ✗ (outside the expected range)"))
    lines.append(f"calibration cost ${meter.total_usd():.3f}")
    return lines
