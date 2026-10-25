"""Volume test: thousands of synthetic screenings through the real engine and API, at $0.

The engine, policy, storage, interview booking, follow-up scheduler and API are the production code.
Only the two language models are replaced: a scripted reader returns what the model would have read,
and the fixed templates write the replies. So this measures our own code, and how the recruiter
endpoints behave as the database grows; the models' latency and cost are measured by the evals.

    python scripts/volume_test.py --n 1000            # a week of Grupo Sazón
    python scripts/volume_test.py --n 1000 10000      # and the 10K/week scenario

Writes evals/results/volume.md (and .json); the databases go to data/volume-<n>.db (gitignored).
"""

from __future__ import annotations

import argparse
import json
import random
import statistics
import threading
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from pathlib import Path

from fastapi.testclient import TestClient

from screener.api.app import create_app
from screener.domain.models import StartDateExpr, utcnow
from screener.engine.engine import ScreeningEngine
from screener.factory import load_config
from screener.llm.schemas import Evidence, Extracted, TurnAnalysis
from screener.llm.templates import TemplateResponder
from screener.storage.repository import Repository
from screener.views import display_status

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "evals" / "results"
EVIDENCE = {"full_name": "full_name", "drivers_license": "drivers_license", "license_type": "drivers_license",
            "location_text": "location", "location_city_id": "location", "location_outside_service_area": "location",
            "availability": "availability", "schedule": "schedule", "experience_months": "experience",
            "experience_platforms": "experience", "start_date": "start_date"}
FIRST = ["Lucía", "Mateo", "Sofía", "Hugo", "Martina", "Leo", "Valeria", "Daniel", "Camila", "Pablo", "Ximena", "Diego"]
LAST = ["García", "López", "Martínez", "Sánchez", "Pérez", "Gómez", "Ruiz", "Hernández", "Díaz", "Torres", "Ramírez", "Flores"]
# Outcome mix of a week of applications (illustrative: the pilot gives the real one)
PATHS = {"qualified": 50, "no_licence": 10, "out_of_area": 7, "unclear_licence": 5, "withdrawn": 5,
         "abandoned": 18, "in_progress": 5}


def reading(message: str, intents=("provide_info",), **fields) -> TurnAnalysis:
    """What the understanding model would return for this message, with valid evidence."""
    extracted = Extracted.model_validate({**Extracted.empty().model_dump(), **fields})
    groups = sorted({EVIDENCE[k] for k, v in fields.items() if v is not None})
    return TurnAnalysis.blank(intents=list(intents), extracted=extracted,
                              evidence=[Evidence(field=g, quote=message) for g in groups])


class ScriptedReader:
    """Each worker thread plays one candidate at a time: it reads that candidate's script in order."""

    def __init__(self):
        self.local = threading.local()

    def load(self, script: list[TurnAnalysis]):
        self.local.script = list(script)

    def analyze(self, request):
        return self.local.script.pop(0)


def candidate(rng: random.Random, cfg) -> tuple[str, str, list[tuple[str, TurnAnalysis]]]:
    """A random applicant: (path, opening language, [(message, what the model reads)])."""
    path = rng.choices(list(PATHS), weights=list(PATHS.values()))[0]
    lang = "en" if rng.random() < 0.15 else None
    area = rng.choices(cfg.service_areas, weights=[a.restaurants for a in cfg.service_areas])[0]
    name = f"{rng.choice(FIRST)} {rng.choice(LAST)}"
    place = f"{area.name}, {rng.choice(area.zones).name}"
    licence = rng.choice(["car", "motorbike"])
    months = rng.choice([0, 0, 6, 12, 24, 36])
    steps = [("sí", reading("sí", intents=("affirm",))), (name, reading(name, full_name=name))]
    if path == "no_licence":
        return path, lang, steps + [("no tengo carnet", reading("no tengo carnet", drivers_license="no")),
                                    ("vale", reading("vale", intents=("affirm",)))]
    if path == "unclear_licence":
        steps += [("más o menos", reading("más o menos", intents=("other",)))] * 2
    else:
        steps.append((f"sí, de {licence}", reading("sí", drivers_license="yes", license_type=licence)))
    if path == "withdrawn":
        return path, lang, steps + [("ya no me interesa", reading("ya no me interesa", intents=("opt_out",)))]
    if path == "out_of_area":
        return path, lang, steps + [
            ("vivo en Toledo", reading("vivo en Toledo", location_text="Toledo", location_outside_service_area=True)),
            ("no, gracias", reading("no, gracias", intents=("deny",)))]
    steps += [
        (place, reading(place, location_text=place, location_city_id=area.id)),
        ("media jornada", reading("media jornada", availability=[rng.choice(["full_time", "part_time", "weekends"])])),
        ("tardes", reading("tardes", schedule=[rng.choice(["morning", "afternoon", "evening", "flexible"])])),
        ("experiencia", reading("experiencia", experience_months=months, experience_platforms=["Glovo"] if months else None)),
        ("en una semana", reading("en una semana", start_date=StartDateExpr(kind="in_weeks", amount=1))),
        ("sí, todo correcto", reading("sí", intents=("affirm",))),
    ]
    if path in ("qualified", "unclear_licence"):
        if rng.random() < 0.1:  # none of the times fits, twice: a recruiter takes over
            steps += [("Ninguno me va bien", reading("ninguno", intents=("deny",)))] * 2
        else:
            choice = rng.choice(["1", "2", "3"])
            steps.append((choice, reading(choice)))
    if path in ("abandoned", "in_progress"):
        steps = steps[: rng.randint(3, len(steps) - 2)]
    return path, lang, steps


def pctl(values: list[float], q: float) -> float:
    return statistics.quantiles(values, n=100, method="inclusive")[int(q) - 1] if len(values) > 1 else (values or [0])[0]


def timed(fn, runs: int) -> dict:
    ms = []
    out = None
    for _ in range(runs):
        t = time.perf_counter()
        out = fn()
        ms.append(1000 * (time.perf_counter() - t))
    return {"p50_ms": round(statistics.median(ms), 1), "max_ms": round(max(ms), 1), "out": out}


def run(n: int, workers: int) -> dict:
    cfg = load_config()
    db = ROOT / "data" / f"volume-{n}.db"
    db.unlink(missing_ok=True)
    reader, clock = ScriptedReader(), threading.local()
    end = utcnow()
    engine = ScreeningEngine(config=cfg, repository=Repository(f"sqlite:///{db}"), understander=reader,
                             responder=TemplateResponder(cfg), clock=lambda: getattr(clock, "now", end))
    rng = random.Random(n)
    people = [candidate(rng, cfg) for _ in range(n)]
    starts = sorted(end - timedelta(hours=rng.uniform(1 if p[0] == "in_progress" else 2, 7 * 24)) for p in people)
    turn_ms: list[float] = []
    lock = threading.Lock()

    def screen(i: int) -> None:
        path, lang, steps = people[i]
        clock.now = starts[i]
        reader.load([r for _, r in steps])
        cid = engine.start(channel="web", language=lang).conversation_id
        for text, _ in steps:
            clock.now += timedelta(seconds=40)
            t = time.perf_counter()
            engine.handle(cid, text)
            with lock:
                turn_ms.append(1000 * (time.perf_counter() - t))

    t0 = time.perf_counter()
    with ThreadPoolExecutor(max_workers=workers) as pool:
        list(pool.map(screen, range(n)))
    seconds = time.perf_counter() - t0

    clock.now = end  # the scheduler's pass happens "now": reminders and abandonment for the silent ones
    followups = timed(engine.run_followups, 1)
    states = [engine.repo.get_state(c.id) for c in engine.repo.conversations()]
    statuses = Counter(display_status(s, end) for s in states)
    interviews = Counter(s.interview.status.value for s in states if s.interview)

    api = {}
    reader.load([])
    with TestClient(create_app(engine=engine, scheduler=False)) as client:
        some = random.Random(1).sample([s.id for s in states], 20)
        for label, fn, runs in [
            ("GET /api/candidates (the pipeline)", lambda: client.get("/api/candidates"), 5),
            ("GET /api/analytics", lambda: client.get("/api/analytics"), 5),
            ("GET /api/candidates/{id} (one candidate)", lambda: client.get(f"/api/candidates/{some.pop()}"), 20),
        ]:
            r = timed(fn, runs)
            api[label] = {"p50_ms": r["p50_ms"], "max_ms": r["max_ms"], "kb": round(len(r["out"].content) / 1024, 1)}

    return {
        "n": n, "workers": workers, "seconds": round(seconds, 1), "turns": len(turn_ms),
        "turn_p50_ms": round(statistics.median(turn_ms), 1), "turn_p95_ms": round(pctl(turn_ms, 95), 1),
        "turn_max_ms": round(max(turn_ms), 1), "turns_per_s": round(len(turn_ms) / seconds, 1),
        "followups_pass_ms": followups["p50_ms"], "followup_actions": len(followups["out"]),
        "db_mb": round(db.stat().st_size / 1e6, 1),
        "rows": {"messages": len(engine.repo.all_messages()), "events": len(engine.repo.events())},
        "statuses": dict(statuses.most_common()), "interviews": dict(interviews.most_common()),
        "api": api,
    }


def report(runs: list[dict]) -> str:
    lines = [
        "# Volume test", "",
        "Thousands of synthetic screenings through the production engine, storage, scheduler and API "
        "(`scripts/volume_test.py`). The language models are replaced by a scripted reader and the fixed "
        "templates, so this measures **our own code at volume, at $0**; model latency and cost are in the "
        "other evals (understanding ≈ 1.6 s, writing ≈ 1.3 s per turn). One process, SQLite, a laptop.", "",
        "| | " + " | ".join(f"{r['n']:,} screenings" for r in runs) + " |",
        "|---|" + "---|" * len(runs),
    ]
    def row(label, fn):
        lines.append(f"| {label} | " + " | ".join(fn(r) for r in runs) + " |")
    row("Candidate messages processed", lambda r: f"{r['turns']:,} in {r['seconds']} s ({r['turns_per_s']}/s, {r['workers']} threads)")
    row("Engine time per message, without the models: p50 / p95", lambda r: f"{r['turn_p50_ms']} / {r['turn_p95_ms']} ms")
    row("Follow-up scheduler, one pass over every conversation", lambda r: f"{r['followups_pass_ms']:,.0f} ms ({r['followup_actions']} reminders or abandonments)")
    row("Database", lambda r: f"{r['db_mb']} MB · {r['rows']['messages']:,} messages · {r['rows']['events']:,} events")
    for label in runs[0]["api"]:
        row(label, lambda r, l=label: f"{r['api'][l]['p50_ms']:,.0f} ms p50 · {r['api'][l]['kb']:,} KB")
    row("Outcomes", lambda r: ", ".join(f"{k} {v}" for k, v in r["statuses"].items()))
    row("Interviews", lambda r: ", ".join(f"{k} {v}" for k, v in r["interviews"].items()))
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--n", nargs="+", type=int, default=[1000])
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()
    runs = []
    for n in args.n:
        print(f"{n} screenings…", flush=True)
        runs.append(run(n, args.workers))
        print(json.dumps({k: v for k, v in runs[-1].items() if k not in ("statuses", "interviews")}, indent=1), flush=True)
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "volume.json").write_text(json.dumps(runs, indent=1))
    (RESULTS / "volume.md").write_text(report(runs))


if __name__ == "__main__":
    main()
