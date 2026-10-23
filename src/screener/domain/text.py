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


# Function words that exist in only one of the two languages ("a", "no", "me" are in both).
_ES_WORDS_RAW = """el la los las un una unos unas y o que de del en con por para pero muy mas tambien
es soy estoy tengo vivo puedo quiero hola gracias si mi mis tu su sus al lo le les nos ya bueno vale
porque cuando donde como desde hace hasta sin sobre este esta eso esto mañana tarde noche"""
_EN_WORDS_RAW = """the and or of to in on at with for but very also is am are was have has had do does
can could would will i you we they my your our it this that these those hi hello thanks thank yes
please because when where how from since near like just"""


def function_word_language(text: str) -> str | None:
    """Cheap, deterministic language guess from function words; None when there's no signal.

    Used as a second opinion: the LLM alone once read "en la noche" and "full time y part
    time" as English. A language switch now needs the model AND this not to disagree.
    """
    tokens = normalize(text).split()
    es = sum(t in _ES_WORDS for t in tokens)
    en = sum(t in _EN_WORDS for t in tokens)
    if es == en:
        return None
    return "es" if es > en else "en"


_ES_WORDS = {normalize(w) for w in _ES_WORDS_RAW.split()}
_EN_WORDS = {normalize(w) for w in _EN_WORDS_RAW.split()}


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


# Words that clearly mark Mexican or Spain Spanish ("dale", "va", "ok" mark neither).
_VARIANT_MARKERS = {
    "es-MX": ["carro", "licencia de manejo", "manejo", "chamba", "chambear", "ahorita", "que onda", "orale",
              "neta", "simon", "chido", "padrisimo", "mande", "platicar"],
    "es-ES": ["coche", "carnet", "vale", "curro", "currar", "vosotros", "vuestro", "vuestra", "guay", "mola",
              "molar", "tio", "tia"],
}


def spanish_variant_markers(text: str) -> str | None:
    """Spain or Mexico Spanish if the message uses words that clearly mark only one of them.

    A second opinion for the model's guess, like `function_word_language` for the language:
    "dale" alone once switched a candidate in Spain to Mexican vocabulary."""
    norm = normalize(text)
    hits = {variant for variant, words in _VARIANT_MARKERS.items() if any(contains_phrase(norm, w) for w in words)}
    return hits.pop() if len(hits) == 1 else None
