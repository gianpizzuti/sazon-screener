"""Knowledge-base retrieval eval: does the right topic reach the understanding model, and does it pick it?

    python -m evals.retrieval                        # retrieval only: local models, no API, $0
    python -m evals.retrieval --models minilm mpnet  # compare embedding models (mpnet: 1 GB download)
    python -m evals.retrieval --route --repeat 2     # also the topic Haiku chooses, in four setups (~0.32 USD)
    python -m evals.retrieval --report               # rewrite the report from the last results

Retrieval is scored on the questions some topic answers (recall@k: the right topic is among the
first k; MRR: 1/position, averaged). Routing is the end result: the topic the production
understanding model picks from what retrieval showed it, including "none" for the questions
nothing answers. Writes evals/results/retrieval.json and evals/results/retrieval.md.
"""

from __future__ import annotations

import argparse
import json
import statistics
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from datetime import datetime

import yaml

from evals.common import EVALS, RESULTS, UsageMeter, load_config, pct
from evals.extraction import request_for
from screener.knowledge import METHODS, KnowledgeIndex, build_knowledge, load_embedder
from screener.llm.claude import ClaudeUnderstander
from screener.llm.interfaces import LLMError

CASES_FILE = EVALS / "retrieval_cases.yaml"
EMBEDDING_MODELS = {
    "minilm": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",  # 384 dims, 0.22 GB
    "mpnet": "sentence-transformers/paraphrase-multilingual-mpnet-base-v2",   # 768 dims, 1.0 GB
}
# Topics shown to the understanding model: (retrieval shortlist?, with each topic's approved answer?)
SETUPS = {
    "shortlist + answers": (True, True),   # production (D213)
    "shortlist": (True, False),            # first version of the shortlist
    "every topic + answers": (False, True),  # control: the answers without retrieval
    "every topic": (False, False),         # first version: classification over every title
}


def load_cases() -> list[dict]:
    return yaml.safe_load(CASES_FILE.read_text())


# ------------------------------------------------------------------ retrieval ($0)
def score_retrieval(index: KnowledgeIndex, cases: list[dict], method: str) -> dict:
    answerable = [c for c in cases if c["faq"]]
    ranks, latencies = {}, []
    for c in answerable:
        started = time.perf_counter()
        ranking = index.rank(c["msg"], method)
        latencies.append(1000 * (time.perf_counter() - started))
        ranks[c["id"]] = ranking.index(c["faq"]) + 1 if c["faq"] in ranking else None
    n = len(answerable)

    def recall(k, subset=answerable):
        return sum(1 for c in subset if ranks[c["id"]] and ranks[c["id"]] <= k) / len(subset)

    observed = [c for c in answerable if c["source"] == "observed"]
    return {
        "recall@1": recall(1), "recall@3": recall(3), "recall@5": recall(5),
        "mrr": sum(1 / r for r in ranks.values() if r) / n,
        "observed recall@5": recall(5, observed) if observed else None,
        "median_ms": statistics.median(latencies),
        "misses@5": [{"id": c["id"], "msg": c["msg"], "faq": c["faq"], "rank": ranks[c["id"]],
                      "top": index.rank(c["msg"], method)[:3]} for c in answerable if not ranks[c["id"]] or ranks[c["id"]] > 5],
    }


def compare(cases: list[dict], models: list[str]) -> dict:
    cfg = load_config()
    out = {}
    for short in models:
        started = time.perf_counter()
        embedder = load_embedder(EMBEDDING_MODELS[short])
        loaded = time.perf_counter()
        index = KnowledgeIndex(cfg.faq, embedder, cfg.retrieval.shortlist)
        built = time.perf_counter()
        out[short] = {
            "model": EMBEDDING_MODELS[short], "phrasings": index.phrasings,
            "load_s": round(loaded - started, 2), "index_s": round(built - loaded, 2),
            "methods": {m: score_retrieval(index, cases, m) for m in METHODS},
        }
        print(f"{short}: " + ", ".join(f"{m} R@5={r['recall@5']:.0%}" for m, r in out[short]["methods"].items()))
    return out


# ------------------------------------------------------------------ routing (Haiku)
def route(cases: list[dict], repeat: int) -> dict:
    cfg = load_config()
    index = build_knowledge(cfg)  # what production shows the model
    titles_only = {e.id: e.model_copy(update={"answer": {"default": ""}}) for e in cfg.faq}  # the prompt omits empty answers
    out = {}
    for setup, (shortlist, answers) in SETUPS.items():
        meter = UsageMeter()
        understander = ClaudeUnderstander(meter.client(), cfg)

        def one(case: dict) -> dict:
            topics = index.search(case["msg"]) if shortlist else cfg.faq
            topics = topics if answers else [titles_only[t.id] for t in topics]
            context = {"msg": case["msg"], "asked": "availability", "conv": case.get("conv", "es")}
            request = replace(request_for(context, cfg), faq_topics=topics)
            try:
                got = understander.analyze(request).faq_id
            except LLMError as exc:
                return {"id": case["id"], "error": str(exc)[:200]}
            gold = case["faq"]
            outcome = "correct" if got == gold else ("missed" if got is None else "wrong topic")
            return {"id": case["id"], "msg": case["msg"], "faq": gold, "got": got, "outcome": outcome,
                    "round": case.get("round", 1), "shown": [t.id for t in topics] if shortlist else "all"}

        with ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(one, [c for c in cases for _ in range(repeat)]))
        answerable = [r for r in results if r.get("faq")]
        unanswerable = [r for r in results if "outcome" in r and not r["faq"]]
        out[setup] = {
            "runs": len(results),
            "errors": sum(1 for r in results if "error" in r),
            "answerable_correct": sum(r["outcome"] == "correct" for r in answerable),
            "answerable_wrong_topic": sum(r["outcome"] == "wrong topic" for r in answerable),
            "answerable_missed": sum(r["outcome"] == "missed" for r in answerable),
            "answerable": len(answerable),
            "none_correct": sum(r["outcome"] == "correct" for r in unanswerable),
            "none_wrong_topic": sum(r["outcome"] == "wrong topic" for r in unanswerable),
            "unanswerable": len(unanswerable),
            "round2_correct": sum(r["outcome"] == "correct" for r in results if r.get("round") == 2),
            "round2": sum(1 for r in results if r.get("round") == 2),
            "usage": meter.by_model(),
            "usd": round(meter.total_usd(), 4),
            "failures": [r for r in results if r.get("outcome") not in (None, "correct")],
        }
        s = out[setup]
        print(f"{setup}: {s['answerable_correct']}/{s['answerable']} right topic, "
              f"{s['none_correct']}/{s['unanswerable']} none, ${s['usd']:.3f}")
    return out


# ------------------------------------------------------------------ report
def report(data: dict) -> str:
    cases = data["cases"]
    answerable = sum(1 for c in cases if c["faq"])
    lines = [
        "# Knowledge-base retrieval", "",
        f"Run {data['run_at']} · {len(cases)} questions ({answerable} answered by a topic, "
        f"{len(cases) - answerable} by none; {sum(c['source'] == 'observed' for c in cases)} asked by simulated candidates) · "
        f"{data['topics']} topics. Method and limits: [README](../README.md#knowledge-base-retrieval).", "",
        "## Retrieval: is the right topic in the shortlist?", "",
        "| Embedding model | Method | Recall@1 | Recall@3 | Recall@5 | MRR | Observed R@5 | Median ms |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for short, m in data["retrieval"].items():
        for method, r in m["methods"].items():
            obs = f"{r['observed recall@5']:.0%}" if r["observed recall@5"] is not None else "n/a"
            lines.append(f"| {short} | {method} | {r['recall@1']:.0%} | {r['recall@3']:.0%} | {r['recall@5']:.0%} | "
                         f"{r['mrr']:.2f} | {obs} | {r['median_ms']:.1f} |")
    lines += ["", "Keyword search does not use the embedding model, so its rows are the same for every model.", ""]
    for short, m in data["retrieval"].items():
        lines.append(f"- **{short}** (`{m['model']}`): {m['phrasings']} phrasings indexed; model load {m['load_s']} s, index {m['index_s']} s.")
        for method in ("semantic", "hybrid"):
            for miss in m["methods"][method]["misses@5"]:
                lines.append(f"  - {method} miss `{miss['id']}` \"{miss['msg']}\" → expected `{miss['faq']}` "
                             f"(rank {miss['rank']}), top 3: {', '.join(miss['top'])}")
    if data.get("routing"):
        lines += ["", "## Routing: which topic does the understanding model choose?", "",
                  f"{data['routing_repeat']} run(s) per question.", "",
                  "| Topics shown | Right topic | Wrong topic | None (missed) | None when nothing answers | Topic when nothing answers | Written after run 1 | Cost |",
                  "|---|---|---|---|---|---|---|---|"]
        for setup, s in data["routing"].items():
            lines.append(f"| {setup} | {s['answerable_correct']}/{s['answerable']} ({pct(s['answerable_correct'], s['answerable'])}) | "
                         f"{s['answerable_wrong_topic']} | {s['answerable_missed']} | {s['none_correct']}/{s['unanswerable']} | "
                         f"{s['none_wrong_topic']} | {s['round2_correct']}/{s['round2']} ({pct(s['round2_correct'], s['round2'])}) | ${s['usd']:.3f} |")
        lines += ["", "A wrong topic is the error that matters: the writer receives an approved answer to another "
                  "question (it still checks the fit, D145). A missed topic is safe: \"the team will confirm\". "
                  "\"Written after run 1\": the right outcome (the topic, or none) on the 24 questions written before the "
                  "change they would judge was run (D213).", ""]
        for setup, s in data["routing"].items():
            for f in s["failures"]:
                shown = "" if f["shown"] == "all" else f" · shown: {', '.join(f['shown'])}"
                lines.append(f"- {setup} · `{f['id']}` \"{f['msg']}\" → expected `{f['faq']}`, got `{f['got']}`{shown}")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--models", nargs="+", default=["minilm"], choices=list(EMBEDDING_MODELS))
    parser.add_argument("--route", action="store_true", help="also run the understanding model (costs API calls)")
    parser.add_argument("--repeat", type=int, default=1, help="routing runs per question")
    parser.add_argument("--report", action="store_true", help="only rewrite retrieval.md from retrieval.json")
    args = parser.parse_args()
    if args.report:
        (RESULTS / "retrieval.md").write_text(report(json.loads((RESULTS / "retrieval.json").read_text())))
        return
    cases = load_cases()
    data = {"run_at": datetime.now().isoformat(timespec="minutes"), "cases": cases,
            "topics": len(load_config().faq), "retrieval": compare(cases, args.models)}
    if args.route:
        data["routing"], data["routing_repeat"] = route(cases, args.repeat), args.repeat
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "retrieval.json").write_text(json.dumps(data, ensure_ascii=False, indent=1))
    (RESULTS / "retrieval.md").write_text(report(data))


if __name__ == "__main__":
    main()
