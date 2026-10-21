"""HTTP API.

Two audiences, two groups of routes:
  /conversations  channel side: what a web chat, a WhatsApp webhook or a voice agent calls
  /candidates     recruiter side: what the dashboard (and an ATS) calls

The recruiter dashboard is just another client of this API, so business logic lives in
one place. Interactive docs (OpenAPI) at /docs: the starting point for an ATS integration.

Run:  uvicorn screener.api.app:app --port 8000
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Literal

from fastapi import BackgroundTasks, FastAPI, HTTPException, Query, Request
from pydantic import BaseModel, Field

from screener.analytics import Analytics, compute
from screener.engine.engine import ScreeningEngine, TurnResult
from screener.storage.repository import REVIEW_STATUSES, ConversationNotFound
from screener.views import CandidateDetail, CandidateRow, build_detail, build_rows


class StartRequest(BaseModel):
    channel: str = "web"
    language: Literal["es", "en"] | None = None


class MessageRequest(BaseModel):
    text: str = Field(min_length=1, max_length=4000)


class ReviewRequest(BaseModel):
    status: Literal[REVIEW_STATUSES]  # type: ignore[valid-type]
    note: str = ""
    by: str = ""


def create_app(engine: ScreeningEngine | None = None) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        if engine is not None:
            app.state.engine = engine
        else:
            from screener.factory import build_engine

            app.state.engine = build_engine()
        yield

    app = FastAPI(
        title="Sazón Screener API",
        version="0.1.0",
        description="Candidate screening agent for Grupo Sazón: channel endpoints and recruiter endpoints.",
        lifespan=lifespan,
    )

    def get_engine(request: Request) -> ScreeningEngine:
        return request.app.state.engine

    @app.get("/health")
    def health() -> dict:
        return {"status": "ok"}

    # ------------------------------------------------------------------ channel side
    @app.post("/conversations", response_model=TurnResult, tags=["channel"])
    def start_conversation(body: StartRequest, request: Request) -> TurnResult:
        """Open a conversation: returns the fixed greeting (AI disclosure + privacy note)."""
        return get_engine(request).start(channel=body.channel, language=body.language)

    @app.post("/conversations/{conversation_id}/messages", response_model=TurnResult, tags=["channel"])
    def send_message(
        conversation_id: str,
        body: MessageRequest,
        request: Request,
        background: BackgroundTasks,
        debug: bool = Query(False, description="Include the model's analysis of the message (never for candidates)."),
    ) -> TurnResult:
        """One candidate message in, the agent's replies out."""
        engine = get_engine(request)
        try:
            result = engine.handle(conversation_id, body.text)
        except ConversationNotFound:
            raise HTTPException(404, "conversation not found")
        stale_summary = "update_after_close" in result.event_types
        if result.completed and (stale_summary or engine.repo.get_summary(conversation_id) is None):
            background.add_task(engine.summarize, conversation_id)  # off the hot path
        if not debug:
            result.analysis = None
        return result

    # ------------------------------------------------------------------ recruiter side
    @app.get("/candidates", response_model=list[CandidateRow], tags=["recruiter"])
    def list_candidates(
        request: Request,
        status: list[str] | None = Query(None, description="qualified, needs_review, in_progress, abandoned, disqualified, withdrawn, terminated"),
        review_status: list[str] | None = Query(None),
        city: str | None = None,
        needs_review: bool | None = None,
    ) -> list[CandidateRow]:
        """The recruiter queue, most actionable first."""
        rows = build_rows(get_engine(request).repo)
        return [
            r for r in rows
            if (not status or r.status in status)
            and (not review_status or r.review_status in review_status)
            and (not city or (r.city or "").lower() == city.lower())
            and (needs_review is None or r.needs_review == needs_review)
        ]

    @app.get("/candidates/{conversation_id}", response_model=CandidateDetail, tags=["recruiter"])
    def get_candidate(conversation_id: str, request: Request) -> CandidateDetail:
        try:
            return build_detail(get_engine(request).repo, conversation_id)
        except ConversationNotFound:
            raise HTTPException(404, "candidate not found")

    @app.put("/candidates/{conversation_id}/review", tags=["recruiter"])
    def review_candidate(conversation_id: str, body: ReviewRequest, request: Request) -> dict:
        """Record what a recruiter decided. Overriding the bot's outcome is audited as a human override."""
        try:
            return get_engine(request).repo.set_review(conversation_id, body.status, body.note, body.by)
        except ConversationNotFound:
            raise HTTPException(404, "candidate not found")

    @app.delete("/candidates/{conversation_id}", status_code=204, tags=["recruiter"])
    def erase_candidate(conversation_id: str, request: Request) -> None:
        """Erase all of a candidate's data on request (GDPR right to erasure)."""
        try:
            get_engine(request).repo.delete_conversation(conversation_id)
        except ConversationNotFound:
            raise HTTPException(404, "candidate not found")

    @app.post("/candidates/{conversation_id}/summary", tags=["recruiter"])
    def regenerate_summary(conversation_id: str, request: Request) -> dict:
        try:
            summary = get_engine(request).summarize(conversation_id)
        except ConversationNotFound:
            raise HTTPException(404, "candidate not found")
        if summary is None:
            raise HTTPException(503, "no summarizer configured")
        return summary

    @app.get("/analytics", response_model=Analytics, tags=["recruiter"])
    def analytics(request: Request) -> Analytics:
        return compute(get_engine(request).repo)

    return app


app = create_app()
