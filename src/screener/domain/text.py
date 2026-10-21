"""Text normalisation and grounding checks."""

from __future__ import annotations

import re
import unicodedata

_PUNCT = re.compile(r"[^\w\s']", re.UNICODE)
_SPACES = re.compile(r"\s+")


def normalize(text: str) -> str:
    """Lowercase, strip accents and punctuation, collapse whitespace."""
    text = unicodedata.normalize("NFKD", text.lower())
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = _PUNCT.sub(" ", text)
    return _SPACES.sub(" ", text).strip()


def contains_phrase(haystack_norm: str, phrase: str) -> bool:
    """Whole-word phrase match on already-normalised text."""
    needle = normalize(phrase)
    if not needle:
        return False
    return re.search(rf"(?<!\w){re.escape(needle)}(?!\w)", haystack_norm) is not None


def is_grounded(quote: str | None, message: str, min_token_overlap: float = 0.7) -> bool:
    """True if `quote` really comes from `message`.

    Anti-hallucination check: the extraction model must cite the candidate's words for
    every value. Exact (normalised) substring passes; otherwise most of the quote's
    tokens must appear in the message, to tolerate small re-spellings.
    """
    if not quote:
        return False
    q, m = normalize(quote), normalize(message)
    if not q:
        return False
    if q in m:
        return True
    q_tokens, m_tokens = q.split(), set(m.split())
    hits = sum(1 for token in q_tokens if token in m_tokens)
    return hits / len(q_tokens) >= min_token_overlap
