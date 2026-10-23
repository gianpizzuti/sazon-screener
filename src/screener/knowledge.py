"""Knowledge-base retrieval: which approved answers might answer a candidate's question (ADR 0010).

A multilingual embedding model ranks the topics of faq.yaml by meaning, so paraphrases and other
languages match ("¿me sale a cuenta con la gasolina?", "how much does it pay?"). A topic is indexed
by its question and its examples, and ranks by its closest phrasing. The shortlist goes to the
understanding model, which picks one topic or none: a related topic is not an answer (parking is
not "vehicle"), and that judgement needs a model, not a similarity score.

`hybrid` also ranks by keywords (BM25) and merges the two rankings by reciprocal rank fusion, the
textbook RAG setup. Measured on this knowledge base it is worse than meaning alone (evals/results/
retrieval.md: generic words such as "hace falta" lift wrong topics), so it is off by default; it is
here for knowledge bases full of exact names and codes, where keywords usually help.

Without the embedding model (not installed, or not downloaded yet) the shortlist is every topic:
the understanding model classifies over the whole list, as before ADR 0010. Correct at this size;
it only stops scaling at a few hundred entries.
"""

from __future__ import annotations

import logging
import math
import re
from collections import Counter
from functools import lru_cache
from pathlib import Path
from typing import Protocol

import numpy as np

from screener.config import ClientConfig, FaqEntry
from screener.domain.text import normalize

log = logging.getLogger(__name__)

MODELS_DIR = Path(__file__).resolve().parents[2] / "data" / "models"
RRF_K = 60  # the usual constant: rank 1 adds 1/61 and rank 10 adds 1/70, so neither ranking dominates
METHODS = ("keyword", "semantic", "hybrid")

# Words that say nothing about the topic. BM25 already discounts common words; this only removes
# the ones so short or frequent that they would match everything.
# Question words too: "how" in "how often is payday?" must not match "how far are the deliveries?".
_STOPWORDS = set("""a al con de del el en es la las lo los me mi o para por que se si su te tu un una y
como cual cuales cuando donde quien hay eso esto
an and any are be can do does how i in is it my of on or the there to what when where which who why you""".split())
_QUESTION = re.compile(r"¿?[^.!?¿¡\n]+\?")


def terms(text: str) -> list[str]:
    """Words for keyword search: normalised, without stopwords, plural "s" removed (propinas = propina)."""
    return [w[:-1] if len(w) > 3 and w.endswith("s") else w for w in normalize(text).split() if w not in _STOPWORDS]


def questions_in(text: str) -> list[str]:
    """The questions inside a longer message ("Mañanas. Pero, ¿hay parking?" -> "¿hay parking?")."""
    return [q.strip() for q in _QUESTION.findall(text) if q.strip() != text.strip()]


class _BM25:
    def __init__(self, docs: list[list[str]], k1: float = 1.2, b: float = 0.75):
        self.k1, self.b = k1, b
        self.tf = [Counter(d) for d in docs]
        self.norm = [k1 * (1 - b + b * len(d) / (sum(map(len, docs)) / len(docs))) for d in docs]
        df = Counter(t for d in docs for t in set(d))
        self.idf = {t: math.log(1 + (len(docs) - n + 0.5) / (n + 0.5)) for t, n in df.items()}

    def scores(self, query: list[str]) -> np.ndarray:
        out = np.zeros(len(self.tf))
        for t in set(query) & self.idf.keys():
            for i, tf in enumerate(self.tf):
                if f := tf.get(t):
                    out[i] += self.idf[t] * f * (self.k1 + 1) / (f + self.norm[i])
        return out


class Embedder(Protocol):
    def embed(self, texts: list[str]) -> np.ndarray:
        """One unit-length row per text."""


class FastEmbedder:
    """A sentence-embedding model run locally (ONNX, via fastembed): no API call, no data leaves the server."""

    def __init__(self, model: str, cache_dir: Path = MODELS_DIR):
        from fastembed import TextEmbedding

        self.name = model
        self._model = TextEmbedding(model, cache_dir=str(cache_dir))

    def embed(self, texts: list[str]) -> np.ndarray:
        vectors = np.array(list(self._model.embed(texts)), dtype=np.float32)
        return vectors / np.linalg.norm(vectors, axis=1, keepdims=True)


@lru_cache(maxsize=4)
def load_embedder(model: str) -> FastEmbedder | None:
    """Loaded once per process (downloaded on first use into data/models)."""
    try:
        return FastEmbedder(model)
    except Exception as exc:  # not installed, offline on the first run, a broken download
        log.warning("embedding model %s unavailable, the understanding model will see every topic: %s", model, exc)
        return None


class KnowledgeIndex:
    def __init__(self, faq: list[FaqEntry], embedder: Embedder | None = None, shortlist: int = 5,
                 method: str = "semantic"):
        self.entries = list(faq)
        self.embedder = embedder
        self.shortlist = shortlist
        self.default_method = method
        topic, texts = [], []
        for i, entry in enumerate(self.entries):
            for text in [entry.question, *questions_in(entry.question), *entry.examples]:
                topic.append(i)
                texts.append(text)
        self._topic = np.array(topic)
        self._bm25 = _BM25([terms(t) for t in texts])
        self._vectors = embedder.embed(texts) if embedder else None
        self.phrasings = len(texts)

    @property
    def method(self) -> str:
        return self.default_method if self._vectors is not None else "every topic"

    def search(self, message: str) -> list[FaqEntry]:
        """The topics shown to the understanding model for this message."""
        if self._vectors is None:
            return self.entries
        by_id = {e.id: e for e in self.entries}
        return [by_id[i] for i in self.rank(message, self.default_method)[: self.shortlist]]

    def rank(self, message: str, method: str = "semantic") -> list[str]:
        """Topic ids with any evidence, best first. The semantic side also scores each question
        inside the message on its own, so a question at the end of a long answer is not diluted."""
        rankings = []
        if method in ("keyword", "hybrid"):
            rankings.append(self._ranking(self._bm25.scores(terms(message)), keep_zero=False))
        if method in ("semantic", "hybrid"):
            if self._vectors is None:
                raise ValueError("semantic search needs an embedding model")
            queries = self.embedder.embed([message, *questions_in(message)])
            rankings.append(self._ranking((self._vectors @ queries.T).max(axis=1), keep_zero=True))
        fused: Counter[int] = Counter()
        for ranking in rankings:
            for position, topic in enumerate(ranking, 1):
                fused[topic] += 1 / (RRF_K + position)
        return [self.entries[t].id for t, _ in fused.most_common()]

    def _ranking(self, scores: np.ndarray, keep_zero: bool) -> list[int]:
        """Topics ordered by their best-scoring phrasing."""
        best = np.full(len(self.entries), -np.inf)
        np.maximum.at(best, self._topic, scores)
        return [int(i) for i in np.argsort(-best, kind="stable") if keep_zero or best[i] > 0]


def build_knowledge(cfg: ClientConfig) -> KnowledgeIndex:
    r = cfg.retrieval
    return KnowledgeIndex(cfg.faq, load_embedder(r.embedding_model) if r.embedding_model else None, r.shortlist, r.method)
