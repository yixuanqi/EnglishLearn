"""Scenario model matching database_schema.md."""

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, CheckConstraint, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.dialogue import Dialogue


class Scenario(Base):
    """Scenario model for practice scenarios."""

    __tablename__ = "scenarios"

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    category: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        index=True,
    )
    difficulty: Mapped[str] = mapped_column(
        String(20),
        default="intermediate",
        nullable=False,
        index=True,
    )
    context: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    user_role: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )
    ai_role: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )
    key_vocabulary: Mapped[dict] = mapped_column(
        JSONB,
        default=list,
        nullable=False,
    )
    tips: Mapped[dict] = mapped_column(
        JSONB,
        default=list,
        nullable=False,
    )
    estimated_duration: Mapped[int] = mapped_column(
        Integer,
        default=10,
        nullable=False,
    )
    is_premium: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
    )
    thumbnail_url: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    __table_args__ = (
        CheckConstraint(
            "category IN ('exhibition', 'technical', 'business', 'daily_life')",
            name="chk_category",
        ),
        CheckConstraint(
            "difficulty IN ('beginner', 'intermediate', 'advanced')",
            name="chk_difficulty",
        ),
    )

    dialogues: Mapped[list["Dialogue"]] = relationship(
        "Dialogue",
        back_populates="scenario",
        cascade="all, delete-orphan",
    )
