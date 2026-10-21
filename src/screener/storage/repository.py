"""Persistence: conversations, messages and events.

SQLite through SQLAlchemy: zero setup for whoever runs the project, real SQL for the
recruiter dashboard, and Postgres is a connection-string change away.

Four tables, four jobs:
  conversations: current state (JSON) + a few denormalised columns to filter on
  messages:      the full transcript, each message with its "why" (analysis / directive)
  events:        append-only audit trail; analytics are computed from it
  reviews:       what a HUMAN decided (recruiter status, notes). Kept apart from what the
                 bot decided, so automated and human decisions are never confused.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String, Text, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker
from sqlalchemy.pool import StaticPool

from screener.domain.models import ConversationState, utcnow
from screener.engine.directive import Event
from screener.llm.interfaces import ChatMessage


class Base(DeclarativeBase):
    pass


class ConversationRow(Base):
    __tablename__ = "conversations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    client_id: Mapped[str] = mapped_column(String(64), index=True)
    channel: Mapped[str] = mapped_column(String(32))
    stage: Mapped[str] = mapped_column(String(32), index=True)
    language: Mapped[str] = mapped_column(String(8))
    city_id: Mapped[str | None] = mapped_column(String(64), index=True, nullable=True)
    country: Mapped[str | None] = mapped_column(String(2), nullable=True)
    needs_review: Mapped[bool] = mapped_column(Boolean, default=False)
    disqualification_reason: Mapped[str | None] = mapped_column(String(32), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    last_candidate_message_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    state: Mapped[dict] = mapped_column(JSON)
    summary: Mapped[dict | None] = mapped_column(JSON, nullable=True)


class MessageRow(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    conversation_id: Mapped[str] = mapped_column(ForeignKey("conversations.id"), index=True)
    role: Mapped[str] = mapped_column(String(16))  # agent | candidate
    text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    meta: Mapped[dict] = mapped_column(JSON, default=dict)


class EventRow(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    conversation_id: Mapped[str] = mapped_column(ForeignKey("conversations.id"), index=True)
    type: Mapped[str] = mapped_column(String(48), index=True)
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class ReviewRow(Base):
    __tablename__ = "reviews"

    conversation_id: Mapped[str] = mapped_column(ForeignKey("conversations.id"), primary_key=True)
    status: Mapped[str] = mapped_column(String(24), default="new")
    note: Mapped[str] = mapped_column(Text, default="")
    updated_by: Mapped[str] = mapped_column(String(64), default="")
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


# Recruiter workflow after the screening. Moving a bot-disqualified candidate forward (or
# rejecting a bot-qualified one) is a human override and is logged as such.
REVIEW_STATUSES = ("new", "contacted", "interview", "hired", "rejected")
ADVANCING = {"contacted", "interview", "hired"}


class ConversationNotFound(KeyError):
    pass


class Repository:
    def __init__(self, url: str = "sqlite:///data/screener.db"):
        kwargs: dict = {}
        if url.startswith("sqlite"):
            kwargs["connect_args"] = {"check_same_thread": False}
            if url in ("sqlite://", "sqlite:///:memory:"):
                kwargs["poolclass"] = StaticPool  # one shared in-memory DB (tests)
            else:
                Path(url.removeprefix("sqlite:///")).parent.mkdir(parents=True, exist_ok=True)
        self.engine = create_engine(url, **kwargs)
        Base.metadata.create_all(self.engine)
        self._session = sessionmaker(self.engine, expire_on_commit=False)

    # -------------------------------------------------------------- writes
    def save_turn(
        self,
        state: ConversationState,
        messages: list[tuple[str, str, dict]],
        events: list[Event],
    ) -> None:
        """Persist a whole turn atomically: state, new messages and events."""
        state.updated_at = utcnow()
        with self._session.begin() as s:
            row = s.get(ConversationRow, state.id) or ConversationRow(id=state.id, client_id=state.client_id)
            row.channel = state.channel
            row.stage = state.stage.value
            row.language = state.language
            row.city_id = state.data.city_id
            row.country = state.data.country
            row.needs_review = state.needs_review
            row.disqualification_reason = state.disqualification_reason.value if state.disqualification_reason else None
            row.created_at = state.created_at
            row.updated_at = state.updated_at
            row.last_candidate_message_at = state.last_candidate_message_at
            row.completed_at = state.completed_at
            row.state = state.model_dump(mode="json")
            s.add(row)
            s.flush()
            for role, text, meta in messages:
                s.add(MessageRow(conversation_id=state.id, role=role, text=text, meta=_jsonable(meta)))
            for event in events:
                s.add(EventRow(conversation_id=state.id, type=event.type, payload=_jsonable(event.payload)))

    def set_review(self, conversation_id: str, status: str, note: str = "", by: str = "") -> dict:
        """Record a recruiter decision; overriding the bot's outcome is logged as a human override."""
        if status not in REVIEW_STATUSES:
            raise ValueError(f"unknown status {status!r}")
        with self._session.begin() as s:
            conversation = s.get(ConversationRow, conversation_id)
            if conversation is None:
                raise ConversationNotFound(conversation_id)
            review = s.get(ReviewRow, conversation_id) or ReviewRow(conversation_id=conversation_id, status="new")
            previous = review.status
            review.status, review.note, review.updated_by, review.updated_at = status, note, by, utcnow()
            s.add(review)
            if previous != status:
                s.add(EventRow(conversation_id=conversation_id, type="review_status_changed",
                               payload={"from": previous, "to": status, "by": by}))
            bot_outcome = conversation.stage
            if (bot_outcome in ("disqualified", "withdrawn") and status in ADVANCING) or (
                bot_outcome == "qualified" and status == "rejected"
            ):
                s.add(EventRow(conversation_id=conversation_id, type="human_override",
                               payload={"bot_outcome": bot_outcome, "recruiter_status": status, "by": by, "note": note}))
            return _review_dict(review)

    def delete_conversation(self, conversation_id: str) -> None:
        """Erase everything about a candidate (GDPR right to erasure): state, transcript, events, review."""
        with self._session.begin() as s:
            conversation = s.get(ConversationRow, conversation_id)
            if conversation is None:
                raise ConversationNotFound(conversation_id)
            for model in (MessageRow, EventRow, ReviewRow):
                s.query(model).filter_by(conversation_id=conversation_id).delete()
            s.delete(conversation)

    def get_review(self, conversation_id: str) -> dict:
        with self._session() as s:
            review = s.get(ReviewRow, conversation_id)
            return _review_dict(review) if review else {"status": "new", "note": "", "updated_by": "", "updated_at": None}

    def reviews(self) -> dict[str, dict]:
        with self._session() as s:
            return {r.conversation_id: _review_dict(r) for r in s.scalars(select(ReviewRow))}

    def save_summary(self, conversation_id: str, summary: dict) -> None:
        with self._session.begin() as s:
            row = s.get(ConversationRow, conversation_id)
            if row is None:
                raise ConversationNotFound(conversation_id)
            row.summary = summary

    # -------------------------------------------------------------- reads
    def get_state(self, conversation_id: str) -> ConversationState:
        with self._session() as s:
            row = s.get(ConversationRow, conversation_id)
            if row is None:
                raise ConversationNotFound(conversation_id)
            return ConversationState.model_validate(row.state)

    def get_summary(self, conversation_id: str) -> dict | None:
        with self._session() as s:
            row = s.get(ConversationRow, conversation_id)
            return row.summary if row else None

    def transcript(self, conversation_id: str) -> list[ChatMessage]:
        with self._session() as s:
            rows = s.scalars(
                select(MessageRow).where(MessageRow.conversation_id == conversation_id).order_by(MessageRow.id)
            )
            return [ChatMessage(role=r.role, text=r.text) for r in rows]

    def messages(self, conversation_id: str) -> list[MessageRow]:
        with self._session() as s:
            return list(
                s.scalars(select(MessageRow).where(MessageRow.conversation_id == conversation_id).order_by(MessageRow.id))
            )

    def all_messages(self) -> list[MessageRow]:
        with self._session() as s:
            return list(s.scalars(select(MessageRow).order_by(MessageRow.id)))

    def events(self, conversation_id: str | None = None) -> list[EventRow]:
        with self._session() as s:
            query = select(EventRow).order_by(EventRow.id)
            if conversation_id:
                query = query.where(EventRow.conversation_id == conversation_id)
            return list(s.scalars(query))

    def conversations(self) -> list[ConversationRow]:
        with self._session() as s:
            return list(s.scalars(select(ConversationRow).order_by(ConversationRow.created_at.desc())))


def _review_dict(review: ReviewRow) -> dict:
    return {
        "status": review.status,
        "note": review.note,
        "updated_by": review.updated_by,
        "updated_at": review.updated_at.isoformat() if review.updated_at else None,
    }


def _jsonable(value):
    """Enums, dates and pydantic models -> JSON-safe primitives."""
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(v) for v in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if hasattr(value, "value"):  # Enum
        return value.value
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return str(value)
