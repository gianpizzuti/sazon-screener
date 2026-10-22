"""HTTP API.

Two audiences, two groups of routes (all under /api):
  /api/conversations  channel side: what a web chat, a WhatsApp webhook or a voice agent calls
  /api/candidates     recruiter side: what the recruiter web app (and an ATS) calls

The recruiter web app (served at /) is just another client of this API, so business logic lives in
one place. Interactive docs (OpenAPI) at /docs: the starting point for an ATS integration.

Run:  uvicorn screener.api.app:app --port 8000
"""

from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager, suppress
from pathlib import Path
from typing import Literal

from fastapi import APIRouter, BackgroundTasks, FastAPI, HTTPException, Query, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from screener.analytics import Analytics, compute
from screener.engine.engine import ScreeningEngine, TurnResult
from screener.storage.repository import REVIEW_STATUSES, ConversationNotFound
from screener.views import CandidateDetail, CandidateRow, build_detail, build_rows


class StartRequest(BaseModel):
    channel: str = "web"
    language: Literal["es", "en"] | None = None
    # What the application says (in production, from the ATS): the job ad and its restaurant.
    country: Literal["ES", "MX"] | None = None  # sets Spain/Mexico Spanish and the timezone from the first message
    job: str | None = Field(default=None, max_length=200)
    area_id: str | None = None


class MessageRequest(BaseModel):
    text: str = Field(min_length=1, max_length=4000)


class AdvanceRequest(BaseModel):
    hours: float = Field(gt=0, le=24 * 14)


class ReviewRequest(BaseModel):
    status: Literal[REVIEW_STATUSES]  # type: ignore[valid-type]
    note: str = ""
    by: str = ""


log = logging.getLogger(__name__)


def create_app(engine: ScreeningEngine | None = None, scheduler: bool = True) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        if engine is not None:
            app.state.engine = engine
        else:
            from screener.factory import build_engine

            app.state.engine = build_engine()
        task = asyncio.create_task(_followup_loop(app.state.engine)) if scheduler else None
        yield
        if task:
            task.cancel()
            with suppress(asyncio.CancelledError):
                await task

    app = FastAPI(
        title="Sazón Screener API",
        version="0.1.0",
        description="Candidate screening agent for Grupo Sazón: channel endpoints and recruiter endpoints.",
        lifespan=lifespan,
    )

    def get_engine(request: Request) -> ScreeningEngine:
        return request.app.state.engine

    api = APIRouter(prefix="/api")

    @api.get("/health")
    def health(request: Request) -> dict:
        """Also returns the engine's clock, so clients show times consistently (demo clock included)."""
        return {"status": "ok", "now": get_engine(request).clock().isoformat()}

    # ------------------------------------------------------------------ channel side
    @api.post("/conversations", response_model=TurnResult, tags=["channel"])
    def start_conversation(body: StartRequest, request: Request) -> TurnResult:
        """Open a conversation: returns the fixed greeting (AI disclosure + privacy note)."""
        engine = get_engine(request)
        if body.area_id and not engine.cfg.area(body.area_id):
            raise HTTPException(422, f"unknown area_id {body.area_id!r}")
        return engine.start(channel=body.channel, language=body.language, country=body.country, job=body.job, area_id=body.area_id)

    @api.post("/conversations/{conversation_id}/messages", response_model=TurnResult, tags=["channel"])
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
    @api.get("/candidates", response_model=list[CandidateRow], tags=["recruiter"])
    def list_candidates(
        request: Request,
        status: list[str] | None = Query(None, description="qualified, needs_review, in_progress, abandoned, disqualified, withdrawn, terminated"),
        review_status: list[str] | None = Query(None),
        city: str | None = None,
        needs_review: bool | None = None,
    ) -> list[CandidateRow]:
        """The recruiter queue, most actionable first."""
        engine = get_engine(request)
        rows = build_rows(engine.repo, now=engine.clock(), next_followup=engine.next_followup_at)
        return [
            r for r in rows
            if (not status or r.status in status)
            and (not review_status or r.review_status in review_status)
            and (not city or (r.city or "").lower() == city.lower())
            and (needs_review is None or r.needs_review == needs_review)
        ]

    @api.get("/candidates/{conversation_id}", response_model=CandidateDetail, tags=["recruiter"])
    def get_candidate(conversation_id: str, request: Request) -> CandidateDetail:
        engine = get_engine(request)
        try:
            return build_detail(engine.repo, conversation_id, now=engine.clock(), next_followup=engine.next_followup_at)
        except ConversationNotFound:
            raise HTTPException(404, "candidate not found")

    @api.put("/candidates/{conversation_id}/review", tags=["recruiter"])
    def review_candidate(conversation_id: str, body: ReviewRequest, request: Request) -> dict:
        """Record what a recruiter decided. Overriding the bot's outcome is audited as a human override."""
        try:
            return get_engine(request).repo.set_review(conversation_id, body.status, body.note, body.by)
        except ConversationNotFound:
            raise HTTPException(404, "candidate not found")

    @api.delete("/candidates/{conversation_id}", status_code=204, tags=["recruiter"])
    def erase_candidate(conversation_id: str, request: Request) -> None:
        """Erase all of a candidate's data on request (GDPR right to erasure)."""
        try:
            get_engine(request).repo.delete_conversation(conversation_id)
        except ConversationNotFound:
            raise HTTPException(404, "candidate not found")

    @api.post("/candidates/{conversation_id}/summary", tags=["recruiter"])
    def regenerate_summary(conversation_id: str, request: Request) -> dict:
        try:
            summary = get_engine(request).summarize(conversation_id)
        except ConversationNotFound:
            raise HTTPException(404, "candidate not found")
        if summary is None:
            raise HTTPException(503, "no summarizer configured")
        return summary

    @api.get("/config", tags=["recruiter"])
    def workspace_config(request: Request) -> dict:
        """The rules this workspace runs on (read-only, no secrets): what "How it works" shows."""
        cfg = get_engine(request).cfg
        return {
            "client": cfg.name,
            "description": cfg.description,
            "agent": cfg.agent.name,
            "role": cfg.role,
            "service_areas": [
                {"id": a.id, "name": a.name, "country": a.country, "restaurants": a.restaurants, "zones": [z.name for z in a.zones],
                 "interview_place": a.interview_place}
                for a in cfg.service_areas
            ],
            "faq": [{"id": f.id, "question": f.question} for f in cfg.faq],
            "followups": cfg.followups.model_dump(exclude={"scheduler_interval_seconds"}),
            "thresholds": {
                "max_failed_attempts": cfg.agent.max_failed_attempts,
                "late_start_days": cfg.agent.late_start_days,
                "max_message_chars": cfg.agent.max_message_chars,
            },
            "models": cfg.models.model_dump(),
        }

    @api.get("/analytics", response_model=Analytics, tags=["recruiter"])
    def analytics(request: Request) -> Analytics:
        engine = get_engine(request)
        return compute(engine.repo, now=engine.clock())

    @api.post("/followups/run", tags=["operations"])
    def run_followups(request: Request) -> list[dict]:
        """Send due follow-ups now (normally done every minute by the scheduler)."""
        return get_engine(request).run_followups()

    # ------------------------------------------------------------------ demo only
    @api.get("/demo/clock", tags=["demo"])
    def demo_clock(request: Request) -> dict:
        clock = _demo_clock(request)
        return {"now": clock().isoformat(), "offset_hours": clock.offset_hours}

    @api.post("/demo/advance", tags=["demo"])
    def demo_advance(body: AdvanceRequest, request: Request) -> dict:
        """Move the simulated clock forward hour by hour, running the scheduler at each step
        (exactly what a day of real time would do)."""
        engine, clock, done, left = get_engine(request), _demo_clock(request), [], body.hours
        while left > 0:
            step = min(1.0, left)
            clock.advance(step)
            left -= step
            done += engine.run_followups()
        return {"now": clock().isoformat(), "offset_hours": clock.offset_hours, "actions": done}

    app.include_router(api)
    _serve_web_app(app)
    return app


WEB_DIST = Path(__file__).resolve().parents[3] / "web" / "dist"


def _serve_web_app(app: FastAPI) -> None:
    """Serve the built recruiter web app (web/dist) at /, with client-side routing fallback.
    One process in production; during development Vite serves it and proxies /api."""
    if not (WEB_DIST / "index.html").exists():
        return
    app.mount("/assets", ImmutableStaticFiles(directory=WEB_DIST / "assets"), name="assets")

    @app.get("/{path:path}", include_in_schema=False)
    def web_app(path: str):
        file = WEB_DIST / path
        if path and file.is_file() and WEB_DIST in file.resolve().parents:
            return FileResponse(file)
        if path.startswith("api/"):
            raise HTTPException(404, "not found")
        # Always revalidated: a cached index.html points to the previous build's file names, which
        # no longer exist after a new build, so pages loaded on demand failed (found after a rebuild).
        return FileResponse(WEB_DIST / "index.html", headers={"Cache-Control": "no-cache"})


class ImmutableStaticFiles(StaticFiles):
    """Built assets have a content hash in their name: a new build means a new name, so cache forever."""

    def file_response(self, *args, **kwargs):
        response = super().file_response(*args, **kwargs)
        response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
        return response


def _demo_clock(request: Request):
    from screener.engine.clock import DemoClock

    clock = request.app.state.engine.clock
    if not isinstance(clock, DemoClock):
        raise HTTPException(404, "demo tools are disabled (set SCREENER_DEMO_TOOLS=1)")
    return clock


async def _followup_loop(engine: ScreeningEngine) -> None:
    """Pilot scheduler: one loop in the API process. Production: one scheduled job with an
    idempotency constraint, so several API workers can't send the same follow-up twice."""
    while True:
        await asyncio.sleep(engine.cfg.followups.scheduler_interval_seconds)
        try:
            await asyncio.to_thread(engine.run_followups)
        except Exception:  # never let one bad run stop re-engagement
            log.exception("follow-up run failed")


app = create_app()
