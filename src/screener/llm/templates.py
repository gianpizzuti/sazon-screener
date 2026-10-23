"""Template responder: deterministic messages from the client's copy.

Used (1) as the degraded mode when the LLM is unavailable or its draft fails the guard,
so a conversation never breaks, and (2) in tests, so the engine is testable offline.
"""

from __future__ import annotations

from screener.config import ClientConfig
from screener.llm.interfaces import SpeakRequest


class TemplateResponder:
    def __init__(self, config: ClientConfig):
        self.cfg = config
        self.copy = config.copy_

    def compose(self, request: SpeakRequest) -> str:
        d = request.directive
        loc = d.locale
        t = self.copy.text
        parts: list[str] = []

        if "resume" in d.notes:
            parts.append(t("misc.resume", loc))
        if "abuse_warning" in d.notes:
            parts.append(t("misc.abuse_warning", loc))
        if d.answer:
            parts.append(d.answer.answer or t("misc.unanswered_question", loc))
        if "human_request" in d.notes:
            parts.append(t("misc.human_request", loc))

        match d.kind:
            case "ask":
                parts.append(self._question(d))
            case "outcome":
                parts.append(self.outcome_text(request))
            case "postpone_ack":
                parts.append(t("misc.postpone_ack", loc))
            case "ask_correction":
                parts.append(t("misc.ask_correction", loc))
            case "talent_pool_ack":
                parts.append(t("talent_pool.yes" if d.talent_pool_answer else "talent_pool.no", loc))
            case "closed_followup":
                if "update_after_close" in d.notes:
                    parts.append(t("misc.update_after_close", loc))
                elif not d.answer:
                    parts.append(t("misc.closing_followup", loc))
            case "interlude" | "recap" | "silent":
                pass
        return " ".join(p for p in parts if p)

    def _question(self, d) -> str:
        """Issue-specific wording when the copy has it ('¿Y tu apellido?'), else retry + question."""
        t, loc = self.copy.text, d.locale
        question = t(f"ask.{d.ask_field.value}", loc, city=d.zone_city or "")
        if not d.ask_issue:
            return question
        try:
            return t(f"issue.{d.ask_issue}", loc, options=", ".join(d.ask_options), question=question,
                     place=d.unlisted_zone or "", city=d.zone_city or "")
        except KeyError:
            return f"{t('misc.retry_prefix', loc)} {question}"

    def outcome_text(self, request: SpeakRequest) -> str:
        d = request.directive
        key = "qualified_book" if d.outcome == "qualified" and d.interview_offer else d.outcome
        return self.copy.text(
            f"outcome.{key}",
            d.locale,
            name=d.candidate_name,
            place=d.outcome_place or "",
            next_steps=self.cfg.localized(self.cfg.next_steps, d.locale),
        )
