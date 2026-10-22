"""The eval datasets and scorers are code too: check them offline, without calling a model."""

from __future__ import annotations

from collections import Counter

import pytest

from evals.common import load_config
from evals.extraction import EVIDENCE_GROUP, FIELDS, load_cases, request_for, score
from screener.llm.schemas import Evidence, Extracted, TurnAnalysis

CASES = load_cases()
CASE_KEYS = {"id", "tags", "asked", "stage", "conv", "known", "agent", "msg", "expect", "ignore",
             "lang", "clear", "intents", "forbid", "faq", "sentiment", "variant", "target", "choice"}


def _first(value):
    return value["one_of"][0] if isinstance(value, dict) and "one_of" in value else value


def perfect_analysis(case: dict) -> TurnAnalysis:
    """What a flawless model would return for this case, built from the gold labels."""
    values = {f: _first(v) for f, v in (case.get("expect") or {}).items()}
    if values.get("location_text") == "present":
        values["location_text"] = case["msg"]
    groups = {EVIDENCE_GROUP[f] for f, v in values.items() if v is not None}
    lang = case.get("lang", "es")
    return TurnAnalysis(
        language="es" if lang == "any" else lang,
        language_is_clear=case.get("clear", True),
        spanish_variant=case.get("variant", "unknown"),
        intents=case.get("intents") or (["provide_info"] if groups else ["other"]),
        sentiment=case.get("sentiment", "neutral"),
        question=None,
        faq_id=case.get("faq"),
        correction_target=case.get("target"),
        chosen_option=case.get("choice"),
        extracted=Extracted.model_validate({**Extracted.empty().model_dump(), **values}),
        evidence=[Evidence(field=g, quote=case["msg"]) for g in sorted(groups)],
    )


def test_case_ids_are_unique():
    assert not [i for i, n in Counter(c["id"] for c in CASES).items() if n > 1]


@pytest.mark.parametrize("case", CASES, ids=[c["id"] for c in CASES])
def test_case_is_well_formed(case):
    assert set(case) <= CASE_KEYS, f"unknown keys: {set(case) - CASE_KEYS}"
    assert set(case.get("expect") or {}) <= set(FIELDS)
    assert set(case.get("ignore") or []) <= set(FIELDS)
    request_for(case, load_config())  # the context the model would see can be built


@pytest.mark.parametrize("case", CASES, ids=[c["id"] for c in CASES])
def test_a_perfect_answer_scores_as_correct(case):
    """Guards the scorer and the labels together: gold labels must pass their own checks."""
    result = score(case, perfect_analysis(case))
    assert result["ok"], result


def test_a_hallucinated_value_is_spurious():
    case = next(c for c in CASES if c["id"] == "inj_approve_me")
    analysis = perfect_analysis(case).model_copy(update={"extracted": Extracted.model_validate(
        {**Extracted.empty().model_dump(), "drivers_license": "yes"})})
    result = score(case, analysis)
    assert result["fields"]["drivers_license"] == "spurious" and not result["ok"]
