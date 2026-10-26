"""Knowledge-base retrieval (ADR 0007): the shortlist shown to the understanding model."""

from __future__ import annotations

import zlib
from collections import Counter

import numpy as np
import pytest
import yaml

from conftest import ROOT, TODAY
from screener.domain.models import Stage
from screener.domain.text import normalize
from screener.knowledge import KnowledgeIndex, questions_in, terms
from screener.llm.interfaces import UnderstandRequest
from screener.llm.prompts import build_understand_system, build_understand_user
from test_api import TEXTS, full_screening

RETRIEVAL_CASES = yaml.safe_load((ROOT / "evals" / "retrieval_cases.yaml").read_text())


class WordEmbedder:
    """Stands in for the embedding model: texts that share words are close."""

    def embed(self, texts):
        rows = np.zeros((len(texts), 512), dtype=np.float32)
        for row, text in zip(rows, texts):
            for word in terms(text):
                row[zlib.crc32(word.encode()) % 512] += 1
        return rows / np.maximum(np.linalg.norm(rows, axis=1, keepdims=True), 1e-9)


@pytest.fixture
def index(config):
    return KnowledgeIndex(config.faq, WordEmbedder(), shortlist=5)


# ------------------------------------------------------------------ text
def test_keyword_terms_drop_function_words_and_plurals():
    assert terms("¿Hay propinas para los repartidores?") == ["propina", "repartidore"]
    assert "how" not in terms("how often is payday?")


def test_the_questions_inside_a_longer_message():
    assert questions_in("Mañanas, por favor. Pero, ¿hay sitio para aparcar?") == ["¿hay sitio para aparcar?"]
    assert questions_in("¿cuánto se paga?") == []  # the message itself is the question


# ------------------------------------------------------------------ the shortlist
def test_without_an_embedding_model_the_model_sees_every_topic(config):
    plain = KnowledgeIndex(config.faq)
    assert plain.method == "every topic" and plain.search("¿hay parking?") == config.faq


def test_the_shortlist_is_the_closest_topics(index):
    topics = index.search("¿me quedo yo con las propinas?")
    assert len(topics) == 5 and topics[0].id == "tips"


def test_a_topic_ranks_by_its_closest_phrasing(index):
    # "¿dónde dejo la moto durante el turno?" is an example of parking, not its question
    assert index.rank("¿dónde dejo la moto durante el turno?")[0] == "parking"


def test_a_question_at_the_end_of_a_long_message_is_not_diluted(index):
    message = "Vivo en Sevilla, en Triana, y tengo media jornada libre por las mañanas. ¿Hay parking para los repartidores?"
    assert index.rank(message)[0] == "parking"


def test_hybrid_fuses_the_two_rankings(index):
    keyword, semantic = index.rank("¿pagáis el kilometraje?", "keyword"), index.rank("¿pagáis el kilometraje?", "semantic")
    hybrid = index.rank("¿pagáis el kilometraje?", "hybrid")
    assert set(hybrid) == set(keyword) | set(semantic) and hybrid[0] == "expenses"


def test_semantic_search_needs_the_model(config):
    with pytest.raises(ValueError):
        KnowledgeIndex(config.faq).rank("¿cuánto se paga?", "semantic")


# ------------------------------------------------------------------ what the understanding model sees
def test_the_shortlist_travels_with_its_approved_answers(config, index):
    message = "¿me pagan la gasolina?"
    prompt = build_understand_user(UnderstandRequest(
        message=message, stage=Stage.SCREENING, current_field=None, last_agent_message=None, known={},
        today=TODAY, language="es", faq_topics=index.search(message)))
    assert "- expenses: ¿Me pagan la gasolina?" in prompt and "compensamos el combustible" in prompt
    assert prompt.count("\n- ") == 5
    system = build_understand_system(config)
    assert not [f.id for f in config.faq if f.question in system]  # the topics left the cached system prompt


def test_the_engine_sends_the_shortlist_and_keeps_it_for_audit(make_engine, config):
    engine = make_engine(full_screening())
    engine.knowledge = KnowledgeIndex(config.faq, WordEmbedder(), shortlist=5)
    cid = engine.start().conversation_id
    engine.handle(cid, TEXTS[0])
    request = engine.understander.requests[-1]
    assert len(request.faq_topics) == 5
    row = next(m for m in engine.repo.messages(cid) if m.role == "candidate")
    assert row.meta["faq_topics"] == [t.id for t in request.faq_topics]


# ------------------------------------------------------------------ the knowledge base and its eval
def test_every_topic_has_examples_and_a_unique_id(config):
    assert not [i for i, n in Counter(f.id for f in config.faq).items() if n > 1]
    assert all(len(f.examples) >= 3 for f in config.faq)


def test_the_eval_questions_are_held_out_from_the_index(config):
    """A case identical to an indexed phrasing would measure memory, not retrieval."""
    indexed = {normalize(t) for f in config.faq for t in [f.question, *questions_in(f.question), *f.examples]}
    assert not [c["id"] for c in RETRIEVAL_CASES if normalize(c["msg"]) in indexed]


def test_the_eval_labels_name_real_topics(config):
    topics = {f.id for f in config.faq}
    from evals.extraction import load_cases

    labels = [c["faq"] for c in RETRIEVAL_CASES] + [c["faq"] for c in load_cases() if "faq" in c]
    assert {label for label in labels if label} <= topics
    assert not [i for i, n in Counter(c["id"] for c in RETRIEVAL_CASES).items() if n > 1]
