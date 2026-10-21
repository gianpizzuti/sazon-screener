"""Claude implementations of the LLM capabilities.

Model per task (docs/decisions/0002-llm-per-task.md):
  understand -> fast model, low effort, structured output (hot path)
  speak      -> stronger writer, low effort (hot path, candidate-facing)
  summary    -> most capable model (off the hot path)
Every failure is converted to LLMError so the engine can fall back to templates.
"""

from __future__ import annotations

import json
import logging

import anthropic
from pydantic import ValidationError

from screener.config import ClientConfig
from screener.domain.models import ConversationState
from screener.llm.interfaces import ChatMessage, LLMError, SpeakRequest, UnderstandRequest
from screener.llm.prompts import (
    build_speak_system,
    build_summary_system,
    build_understand_system,
    build_understand_user,
    render_directive,
)
from screener.llm.schemas import CandidateSummary, TurnAnalysis

log = logging.getLogger(__name__)

# Server-side refusal fallback (Claude API). Harmless for this domain, but a declined
# request then gets a second chance instead of falling straight to templates.
FALLBACK_BETA = "server-side-fallback-2026-07-01"
CONVERSATION_OPENER = "[The candidate applied online for the delivery driver role. The assistant opened the conversation.]"


def make_client(timeout: float = 20.0) -> anthropic.Anthropic:
    """Hot-path client: short timeout, SDK retries (429/5xx/connection) with backoff."""
    return anthropic.Anthropic(timeout=timeout, max_retries=2)


def _cached_system(text: str) -> list[dict]:
    return [{"type": "text", "text": text, "cache_control": {"type": "ephemeral"}}]


def _check_stop(response) -> None:
    if response.stop_reason == "refusal":
        raise LLMError(f"refusal: {getattr(response, 'stop_details', None)}")
    if response.stop_reason == "max_tokens":
        raise LLMError("output truncated (max_tokens)")


class ClaudeUnderstander:
    def __init__(self, client: anthropic.Anthropic, config: ClientConfig):
        self.client = client
        self.model = config.models.understand
        self.system = _cached_system(build_understand_system(config))

    def analyze(self, request: UnderstandRequest) -> TurnAnalysis:
        try:
            response = self.client.messages.parse(
                model=self.model,
                max_tokens=4096,
                system=self.system,
                messages=[{"role": "user", "content": build_understand_user(request)}],
                output_format=TurnAnalysis,
                output_config={"effort": "low"},
            )
        except (anthropic.APIError, ValidationError) as exc:
            raise LLMError(f"understand failed: {exc}") from exc
        _check_stop(response)
        if response.parsed_output is None:
            raise LLMError("understand returned no parsed output")
        return response.parsed_output


class ClaudeResponder:
    def __init__(self, client: anthropic.Anthropic, config: ClientConfig):
        self.client = client
        self.config = config
        self.model = config.models.speak
        self.system = _cached_system(build_speak_system(config))
        self.window = config.agent.history_window

    def compose(self, request: SpeakRequest) -> str:
        messages: list[dict] = [{"role": "user", "content": CONVERSATION_OPENER}]
        for m in request.history[-self.window :]:
            messages.append({"role": "assistant" if m.role == "agent" else "user", "content": m.text})
        # Per-turn instructions travel as a mid-conversation system message: an operator
        # channel the candidate cannot imitate, and the cached prefix stays intact.
        messages.append({"role": "system", "content": render_directive(request.directive, self.config, request.feedback)})
        try:
            response = self.client.beta.messages.create(
                model=self.model,
                max_tokens=2048,
                system=self.system,
                messages=messages,
                output_config={"effort": "low"},
                betas=[FALLBACK_BETA],
                fallbacks="default",
            )
        except anthropic.APIError as exc:
            raise LLMError(f"speak failed: {exc}") from exc
        _check_stop(response)
        text = "".join(block.text for block in response.content if block.type == "text").strip()
        if not text:
            raise LLMError("speak returned empty text")
        return text


class ClaudeSummarizer:
    def __init__(self, client: anthropic.Anthropic, config: ClientConfig):
        # Off the hot path: a generous timeout is fine.
        self.client = client.with_options(timeout=120.0)
        self.model = config.models.summary
        self.system = _cached_system(build_summary_system(config))

    def summarize(self, state: ConversationState, transcript: list[ChatMessage]) -> CandidateSummary:
        payload = {
            "outcome": state.stage.value,
            "disqualification_reason": state.disqualification_reason,
            "screening_data": state.data.model_dump(mode="json"),
            "unclear_fields": [f.value for f, s in state.fields.items() if s.status.value == "unclear"],
            "flags": [f"{f.code}:{f.detail}" if f.detail else f.code for f in state.flags],
            "unanswered_questions": state.pending_questions,
        }
        conversation = "\n".join(f"{m.role.upper()}: {m.text}" for m in transcript)
        prompt = (
            f"<screening>\n{json.dumps(payload, ensure_ascii=False, indent=1)}\n</screening>\n\n"
            f"<transcript>\n{conversation}\n</transcript>\n\nWrite the recruiter summary."
        )
        try:
            response = self.client.beta.messages.parse(
                model=self.model,
                max_tokens=8000,
                system=self.system,
                messages=[{"role": "user", "content": prompt}],
                output_format=CandidateSummary,
                output_config={"effort": "medium"},
                betas=[FALLBACK_BETA],
                fallbacks="default",
            )
        except (anthropic.APIError, ValidationError) as exc:
            raise LLMError(f"summary failed: {exc}") from exc
        _check_stop(response)
        if response.parsed_output is None:
            raise LLMError("summary returned no parsed output")
        return response.parsed_output
