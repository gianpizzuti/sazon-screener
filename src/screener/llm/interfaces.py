"""Capabilities the engine needs from language models, independent of any provider.

The engine depends on "something that understands a message", "something that writes a
reply" and "something that summarises", not on Anthropic's SDK. Swapping the provider,
or running tests with fakes, means providing another implementation of these protocols.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Literal, Protocol

from screener.domain.models import ConversationState, FieldName, Stage
from screener.engine.directive import Directive
from screener.llm.schemas import CandidateSummary, TurnAnalysis


class LLMError(Exception):
    """No usable model output: API error, timeout, refusal or invalid structured output."""


@dataclass
class ChatMessage:
    role: Literal["agent", "candidate"]
    text: str


@dataclass
class UnderstandRequest:
    message: str
    stage: Stage
    current_field: FieldName | None
    last_agent_message: str | None
    known: dict[str, str]
    today: date
    language: str


@dataclass
class SpeakRequest:
    directive: Directive
    history: list[ChatMessage]
    feedback: str | None = None  # set when a previous draft failed the output guard


class Understander(Protocol):
    def analyze(self, request: UnderstandRequest) -> TurnAnalysis: ...


class Responder(Protocol):
    def compose(self, request: SpeakRequest) -> str: ...


class Summarizer(Protocol):
    def summarize(self, state: ConversationState, transcript: list[ChatMessage]) -> CandidateSummary: ...
