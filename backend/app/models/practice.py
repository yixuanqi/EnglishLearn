"""Practice session and speech result models matching database_schema.md."""

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.dialogue import Dialogue
    from app.models.user import User


class PracticeSession(Base):
    """Practice session model for tracking user practice."""

    __tablename__ = "practice_sessions"

    user_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    dialogue_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=False),
        ForeignKey("dialogues.id", ondelete="CASCADE"),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        default="active",
        nullable=False,
        index=True,
    )
    current_turn: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    total_turns: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    started_at: Mapped[datetime] = mapped_column(
        nullable=False,
        index=True,
    )
    ended_at: Mapped[Optional[datetime]] = mapped_column(
        nullable=True,
    )
    duration_seconds: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )
    overall_score: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2),
        nullable=True,
    )
    average_accuracy: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2),
        nullable=True,
    )
    average_fluency: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2),
        nullable=True,
    )
    average_completeness: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2),
        nullable=True,
    )
    feedback: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    __table_args__ = (
        CheckConstraint(
            "status IN ('active', 'completed', 'abandoned')",
            name="chk_session_status",
        ),
        CheckConstraint(
            "current_turn >= 0",
            name="chk_current_turn",
        ),
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="practice_sessions",
    )
    dialogue: Mapped["Dialogue"] = relationship(
        "Dialogue",
    )
    speech_results: Mapped[list["SpeechResult"]] = relationship(
        "SpeechResult",
        back_populates="session",
        cascade="all, delete-orphan",
    )


class SpeechResult(Base):
    """Speech result model for individual turn evaluations."""

    __tablename__ = "speech_results"

    session_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=False),
        ForeignKey("practice_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    turn_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    expected_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    transcription: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    pronunciation_score: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2),
        nullable=True,
    )
    accuracy_score: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2),
        nullable=True,
    )
    fluency_score: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2),
        nullable=True,
    )
    completeness_score: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2),
        nullable=True,
    )
    word_evaluations: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
    )
    audio_url: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    audio_duration_seconds: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2),
        nullable=True,
    )
    processing_time_ms: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )
    ai_response_text: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    ai_response_audio_url: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    session: Mapped["PracticeSession"] = relationship(
        "PracticeSession",
        back_populates="speech_results",
    )
