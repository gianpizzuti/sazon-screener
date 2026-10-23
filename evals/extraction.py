"""Extraction eval: how well a model reads one candidate message (the UNDERSTAND step).

Runs every case in extraction_cases.yaml through the production ClaudeUnderstander
(same prompt, same schema) with the model under test, and scores it field by field.

    python -m evals.extraction                          # the production model (Haiku)
    python -m evals.extraction --models haiku sonnet opus
    python -m evals.extraction --only lic_si sd_exact   # a few cases, printed in full

Writes evals/results/extraction_<model>.json and regenerates evals/results/extraction.md
from every result file present.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import time
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from functools import lru_cache

import yaml

from evals.common import EVALS, MODELS, RESULTS, TODAY, UsageMeter, load_config, pct, percentile
from screener.config import ClientConfig
from screener.domain.locations import LocationMatcher
from screener.domain.models import FieldName, Stage
from screener.domain.text import is_grounded, normalize
from screener.knowledge import KnowledgeIndex, build_knowledge
from screener.llm.claude import ClaudeUnderstander
from screener.llm.prompts import build_understand_system
from screener.llm.interfaces import LLMError, UnderstandRequest
from screener.llm.schemas import Extracted, TurnAnalysis

CASES_FILE = EVALS / "extraction_cases.yaml"
FIELDS = list(Extracted.model_fields)
EVIDENCE_GROUP = {
    "full_name": "full_name",
    "drivers_license": "drivers_license",
    "license_type": "drivers_license",
    "location_text": "location",
    "location_city_id": "location",
    "location_zone": "location",
    "location_outside_service_area": "location",
    "availability": "availability",
    "schedule": "schedule",
    "experience_months": "experience",
    "experience_platforms": "experience",
    "start_date": "start_date",
}
# Intents that change the flow: a false alarm ends, pauses or escalates a conversation.
FLOW_INTENTS = {"opt_out", "postpone", "human_request", "abuse"}
CHECKS = {  # case key -> (label, how to read it from the analysis)
    "lang": ("language", lambda a: a.language),
    "clear": ("language_is_clear", lambda a: a.language_is_clear),
    "faq": ("faq routing", lambda a: a.faq_id),
    "sentiment": ("sentiment", lambda a: a.sentiment),
    "variant": ("spanish variant", lambda a: a.spanish_variant),
    "target": ("correction target", lambda a: a.correction_target),
    "choice": ("interview time chosen", lambda a: a.chosen_option),
}
WORKERS = {"haiku": 8, "sonnet": 6, "opus": 4}


def load_cases() -> list[dict]:
    return yaml.safe_load(CASES_FILE.read_text())


# What the engine already knows when each question is asked, in the order questions are asked.
# Cases get this context by default, as in production ("known: {}" tests a cold context).
# Version 1 of the eval had no context and overstated one risk: "6 months with Deliveroo in
# Berlin" was read as the candidate's location 19/20 times without context, 0/20 with it.
TYPICAL_KNOWN = [
    ("drivers_license", "name", "Ana Torres"),
    ("location", "licence", "yes"),
    ("zone", "city", "Madrid"),
    ("availability", "zone", "Centro"),
    ("schedule", "availability", "full_time"),
    ("experience_years", "schedule", "morning"),
    ("experience_platforms", "experience_months", "12"),
    ("start_date", "platforms", "Glovo"),
]


def known_for(case: dict) -> dict[str, str]:
    if "known" in case:
        return {k: str(v) for k, v in (case["known"] or {}).items()}
    asked, known = case.get("asked"), {}
    if not asked or asked == "full_name":
        return known
    mexico = "mexico" in case.get("tags", [])
    for field, key, value in TYPICAL_KNOWN:
        known[key] = {"city": "Guadalajara", "zone": "Providencia"}.get(key, value) if mexico else value
        if field == asked:
            break
    return known


def request_for(case: dict, cfg: ClientConfig, knowledge: KnowledgeIndex | None = None) -> UnderstandRequest:
    asked = case.get("asked")
    conv = case.get("conv", "es")
    known = known_for(case)
    if "agent" in case:
        agent = case["agent"]
    elif asked:
        agent = cfg.copy_.text(f"ask.{asked}", conv, name=known.get("name"), city=known.get("city"))
    else:
        agent = cfg.copy_.text("greeting", conv)
    return UnderstandRequest(
        message=case["msg"],
        stage=Stage(case.get("stage") or ("screening" if asked else "intro")),
        current_field=FieldName(asked) if asked else None,
        last_agent_message=agent,
        known=known,
        today=TODAY,
        language=conv,
        faq_topics=knowledge.search(case["msg"]) if knowledge else cfg.faq,
    )


# ------------------------------------------------------------------ scoring
def _empty(value) -> bool:
    return value is None or value == [] or value == ""


def same(field: str, gold, got) -> bool:
    if isinstance(gold, dict) and "one_of" in gold:
        return any(same(field, g, got) for g in gold["one_of"])
    if gold is None:
        return _empty(got)
    if _empty(got):
        return False
    if field == "location_text":  # gold is "present": the raw place only has to be captured
        return True
    if field in ("full_name", "location_zone"):
        return normalize(got) == normalize(gold)
    if field in ("availability", "schedule"):
        return set(got) == set(gold)
    if field == "experience_platforms":  # as written: "Uber" matches "Uber Eats"
        g, o = [normalize(x) for x in gold], [normalize(x) for x in got]
        return len(g) == len(o) and all(any(a in b or b in a for b in o) for a in g)
    if field == "start_date":
        return all(got.get(k) == v for k, v in gold.items())
    return got == gold


def score(case: dict, analysis: TurnAnalysis) -> dict:
    got = analysis.extracted.model_dump(mode="json")
    expect = case.get("expect") or {}
    ignore = set(case.get("ignore") or [])

    fields: dict[str, str] = {}
    for f in FIELDS:
        if f in ignore:
            continue
        if f not in expect:
            fields[f] = "ok" if _empty(got[f]) else "spurious"
        elif same(f, expect[f], got[f]):
            fields[f] = "correct"
        else:
            fields[f] = "missed" if _empty(got[f]) else "wrong"

    grounded = {}
    for f in FIELDS:
        if not _empty(got[f]):
            group = EVIDENCE_GROUP[f]
            grounded[f] = any(e.field == group and is_grounded(e.quote, case["msg"]) for e in analysis.evidence)

    checks: dict[str, bool] = {}
    for key, (label, read) in CHECKS.items():
        if key == "lang":
            expected = case.get("lang", "es")  # every case checks the language unless it says "any"
            if expected == "any":
                continue
        elif key in case:
            expected = case[key]
        else:
            continue
        checks[label] = read(analysis) == expected
    intents = set(analysis.intents)
    if case.get("intents"):
        checks["intents detected"] = set(case["intents"]) <= intents
    if case.get("forbid"):
        checks["forbidden intents absent"] = not (set(case["forbid"]) & intents)
    expected_intents = set(case.get("intents") or [])
    # The policy handles opt_out before anything else: with it, other flow intents change nothing.
    alarms = [] if "opt_out" in expected_intents & intents else sorted((intents & FLOW_INTENTS) - expected_intents)
    checks["no flow-changing false alarm"] = not alarms

    ok = all(v in ("ok", "correct") for v in fields.values()) and all(checks.values())
    return {"fields": fields, "grounded": grounded, "checks": checks, "false_alarms": alarms, "ok": ok}


@lru_cache(maxsize=1)
def _workspace() -> tuple[ClientConfig, LocationMatcher]:
    cfg = load_config()
    return cfg, LocationMatcher(cfg.service_areas)


def location_after_rules(got: dict) -> dict:
    """City and zone as the engine resolves them: the rules read the raw place first and the model's
    city is only a tie-break or fallback (the same order as ScreeningPolicy._apply_location)."""
    cfg, matcher = _workspace()
    match = matcher.match(got.get("location_text"))
    city, zone = (match.city_id, match.zone) if match.status == "resolved" else (None, None)
    model_city = got.get("location_city_id")
    if match.status == "ambiguous" and model_city in match.option_city_ids:
        city = model_city
    elif match.status == "no_match" and cfg.area(model_city):
        city = model_city
    if city and not zone:
        zone = matcher.zone_in_city(city, got.get("location_zone") or got.get("location_text")) or got.get("location_zone")
    return {"location_city_id": city, "location_zone": zone}


def compact(analysis: TurnAnalysis) -> dict:
    d = analysis.model_dump(mode="json")
    d["extracted"] = {k: v for k, v in d["extracted"].items() if not _empty(v)}
    return d


# ------------------------------------------------------------------ running
def run_model(short: str, cases: list[dict]) -> dict:
    model = MODELS[short]
    cfg = load_config(understand=model)
    meter = UsageMeter()
    understander = ClaudeUnderstander(meter.client(), cfg)
    knowledge = build_knowledge(cfg)

    def one(case: dict) -> dict:
        req = request_for(case, cfg, knowledge)
        started = time.perf_counter()
        try:
            analysis = understander.analyze(req)
        except LLMError as exc:
            return {"id": case["id"], "tags": case.get("tags", []), "msg": case["msg"], "ok": False,
                    "error": str(exc)[:300], "latency_s": round(time.perf_counter() - started, 2)}
        latency = time.perf_counter() - started
        return {"id": case["id"], "tags": case.get("tags", []), "msg": case["msg"],
                "latency_s": round(latency, 2), **score(case, analysis), "got": compact(analysis)}

    with ThreadPoolExecutor(max_workers=WORKERS.get(short, 4)) as pool:
        results = list(pool.map(one, cases))
    return {
        "model": model,
        "short": short,
        "prompt": hashlib.sha256(build_understand_system(cfg).encode()).hexdigest()[:8],
        "run_at": datetime.now().isoformat(timespec="seconds"),
        "commit": subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, cwd=EVALS).stdout.strip(),
        "usage": meter.by_model(),
        "usd": round(meter.total_usd(), 4),
        "cases": results,
    }


# ------------------------------------------------------------------ summarising
def summarize(run: dict) -> dict:
    cases = run["cases"]
    scored = [c for c in cases if "fields" in c]
    outcomes = Counter(o for c in scored for o in c["fields"].values())
    per_field: dict[str, Counter] = defaultdict(Counter)
    for c in scored:
        for f, o in c["fields"].items():
            per_field[f][o] += 1
    check_tot: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    for c in scored:
        for name, passed in c["checks"].items():
            check_tot[name][0] += passed
            check_tot[name][1] += 1
    values = [g for c in scored for g in c["grounded"].values()]
    usable = sum(1 for c in scored for f, o in c["fields"].items() if o == "correct" and c["grounded"].get(f, True))
    tags: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    for c in cases:
        for t in c["tags"]:
            tags[t][0] += c["ok"]
            tags[t][1] += 1
    latencies = [c["latency_s"] for c in cases if "latency_s" in c]
    gold = {g["id"]: g for g in load_cases()}
    loc_model = loc_rules = loc_total = 0
    for c in scored:
        g = gold.get(c["id"].split("#")[0], {})
        expect, ignore = g.get("expect") or {}, set(g.get("ignore") or [])
        after = location_after_rules(c["got"]["extracted"])
        for f in ("location_city_id", "location_zone"):
            if f in expect and f not in ignore:
                loc_total += 1
                loc_model += c["fields"].get(f) == "correct"
                loc_rules += same(f, expect[f], after[f])
    expected = outcomes["correct"] + outcomes["wrong"] + outcomes["missed"]
    return {
        "cases": len(cases),
        "passed": sum(c["ok"] for c in cases),
        "errors": sum(1 for c in cases if "error" in c),
        "expected_values": expected,
        "correct": outcomes["correct"],
        "wrong": outcomes["wrong"],
        "missed": outcomes["missed"],
        "spurious": outcomes["spurious"],
        "usable": usable,
        "grounded": sum(values),
        "values": len(values),
        "per_field": per_field,
        "checks": check_tot,
        "tags": tags,
        "false_alarms": sum(1 for c in scored if c["false_alarms"]),
        "loc": (loc_model, loc_rules, loc_total),
        "p50": percentile(latencies, 50),
        "p95": percentile(latencies, 95),
        "usd": run["usd"],
        "prompt": run.get("prompt", "?"),
        "usd_per_1k": 1000 * run["usd"] / max(1, len(cases)),
    }


def failure_line(case: dict, gold_cases: dict[str, dict]) -> str:
    if "error" in case:
        return f"- `{case['id']}` «{case['msg']}»: error {case['error'][:120]}"
    gold = gold_cases.get(case["id"], {})
    got = case["got"]["extracted"]
    parts = []
    for f, o in case["fields"].items():
        if o in ("wrong", "missed", "spurious"):
            want = (gold.get("expect") or {}).get(f)
            parts.append(f"{f} {o}: expected `{json.dumps(want, ensure_ascii=False)}`, got `{json.dumps(got.get(f), ensure_ascii=False)}`")
    for name, passed in case["checks"].items():
        if not passed:
            detail = {
                "intents detected": f"expected {gold.get('intents')}, got {case['got']['intents']}",
                "forbidden intents absent": f"forbidden {gold.get('forbid')}, got {case['got']['intents']}",
                "no flow-changing false alarm": f"got {case['false_alarms']}",
                "language": f"expected {gold.get('lang', 'es')}, got {case['got']['language']}",
                "language_is_clear": f"expected {gold.get('clear')}, got {case['got']['language_is_clear']}",
                "faq routing": f"expected {gold.get('faq')}, got {case['got']['faq_id']}",
                "sentiment": f"expected {gold.get('sentiment')}, got {case['got']['sentiment']}",
                "spanish variant": f"expected {gold.get('variant')}, got {case['got']['spanish_variant']}",
                "correction target": f"expected {gold.get('target')}, got {case['got']['correction_target']}",
                "interview time chosen": f"expected {gold.get('choice')}, got {case['got'].get('chosen_option')}",
            }.get(name, "")
            parts.append(f"{name}: {detail}")
    return f"- `{case['id']}` «{case['msg']}»: " + "; ".join(parts)


def write_report() -> None:
    runs = []
    for short in MODELS:  # production model first
        path = RESULTS / f"extraction_{short}.json"
        if path.exists():
            runs.append(json.loads(path.read_text()))
    if not runs:
        return
    gold = {c["id"]: c for c in load_cases()}
    sums = [summarize(r) for r in runs]
    head = "| | " + " | ".join(f"{r['short'].title()} (`{r['model']}`)" for r in runs) + " |"
    sep = "|---|" + "---|" * len(runs)

    def row(label: str, fn) -> str:
        return f"| {label} | " + " | ".join(fn(s) for s in sums) + " |"

    lines = [
        "# Extraction eval",
        "",
        f"{len(gold)} hand-labelled candidate messages (Spain and Mexico Spanish, English, slang, typos, several answers in one",
        "message, corrections, FAQ questions, prompt injection). Each goes through the production understanding prompt and",
        "schema with the model under test. Generated by `python -m evals.extraction`; methodology in `evals/README.md`.",
        "",
        "## Summary",
        "",
        head,
        sep,
        row("Understand prompt (sha256)", lambda s: f"`{s['prompt']}`"),
        row("Cases fully correct", lambda s: f"**{s['passed']}/{s['cases']}** ({pct(s['passed'], s['cases'])})"),
        row("Field accuracy (values a human expects)", lambda s: f"{s['correct']}/{s['expected_values']} ({pct(s['correct'], s['expected_values'])})"),
        row("… usable after the grounding check", lambda s: f"{s['usable']}/{s['expected_values']} ({pct(s['usable'], s['expected_values'])})"),
        row("Spurious values (not said by the candidate)", lambda s: str(s["spurious"])),
        row("Location city + zone: model alone → after the rules",
            lambda s: f"{s['loc'][0]}/{s['loc'][2]} → **{s['loc'][1]}/{s['loc'][2]}**"),
        row("Values with a verbatim quote", lambda s: f"{s['grounded']}/{s['values']} ({pct(s['grounded'], s['values'])})"),
        row("Flow-changing false alarms", lambda s: str(s["false_alarms"])),
    ]
    check_names = sorted({n for s in sums for n in s["checks"] if n != "no flow-changing false alarm"})
    for name in check_names:
        lines.append(row(name.capitalize(), lambda s, n=name: f"{s['checks'][n][0]}/{s['checks'][n][1]}" if n in s["checks"] else "n/a"))
    lines += [
        row("API errors", lambda s: str(s["errors"])),
        row("Latency p50 / p95", lambda s: f"{s['p50']:.2f} s / {s['p95']:.2f} s"),
        row("Cost of this run", lambda s: f"${s['usd']:.3f}"),
        row("Cost per 1,000 messages", lambda s: f"${s['usd_per_1k']:.2f}"),
        "",
        "## Accuracy by field",
        "",
        "Correct / expected; spurious values in brackets.",
        "",
        head,
        sep,
    ]
    for f in FIELDS:
        def cell(s, f=f):
            c = s["per_field"].get(f, Counter())
            exp = c["correct"] + c["wrong"] + c["missed"]
            spur = f" [{c['spurious']}]" if c["spurious"] else ""
            return (f"{c['correct']}/{exp}" if exp else "–") + spur
        lines.append(row(f"`{f}`", cell))
    lines += ["", "## Cases fully correct, by tag", "", head, sep]
    for tag in sorted({t for s in sums for t in s["tags"]}):
        lines.append(row(tag, lambda s, t=tag: f"{s['tags'][t][0]}/{s['tags'][t][1]}" if t in s["tags"] else "–"))
    for r in runs:
        failures = [c for c in r["cases"] if not c["ok"]]
        lines += ["", f"## Failures: {r['short'].title()} ({len(failures)})", ""]
        lines += [failure_line(c, gold) for c in sorted(failures, key=lambda c: c["id"])] or ["None."]
    (RESULTS / "extraction.md").write_text("\n".join(lines) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--models", nargs="+", default=["haiku"], choices=list(MODELS))
    parser.add_argument("--only", nargs="+", help="case ids: run just these and print them (nothing is saved)")
    args = parser.parse_args()
    cases = load_cases()
    if args.only:
        cases = [c for c in cases if c["id"] in args.only]
    RESULTS.mkdir(parents=True, exist_ok=True)
    for short in args.models:
        run = run_model(short, cases)
        if args.only:
            print(json.dumps(run["cases"], ensure_ascii=False, indent=1))
            print(f"cost: ${run['usd']:.4f}")
            continue
        (RESULTS / f"extraction_{short}.json").write_text(json.dumps(run, ensure_ascii=False, indent=1) + "\n")
        s = summarize(run)
        print(f"{short}: {s['passed']}/{s['cases']} cases correct, fields {s['correct']}/{s['expected_values']}, "
              f"spurious {s['spurious']}, p50 {s['p50']:.2f}s, ${s['usd']:.3f}")
    if not args.only:
        write_report()


if __name__ == "__main__":
    main()
