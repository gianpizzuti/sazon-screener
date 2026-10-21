"""Persistence: conversations, messages and events.

SQLite through SQLAlchemy: zero setup for whoever runs the project, real SQL for the
recruiter dashboard, and Postgres is a connection-string change away.

Three tables, three jobs:
  conversations: current state (JSON) + a few denormalised columns to filter on
  messages:      the full transcript, each message with its "why" (analysis / directive)
  events:        append-only audit trail; analytics are computed from it
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

    def events(self, conversation_id: str | None = None) -> list[EventRow]:
        with self._session() as s:
            query = select(EventRow).order_by(EventRow.id)
            if conversation_id:
                query = query.where(EventRow.conversation_id == conversation_id)
            return list(s.scalars(query))

    def conversations(self) -> list[ConversationRow]:
        with self._session() as s:
            return list(s.scalars(select(ConversationRow).order_by(ConversationRow.created_at.desc())))


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
