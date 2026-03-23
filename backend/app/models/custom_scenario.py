"""Custom scenario model matching database_schema.md."""

from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class CustomScenario(Base):
    """Custom scenario model for user-created scenarios."""

    __tablename__ = "custom_scenarios"

    user_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    category: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
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
    difficulty: Mapped[str] = mapped_column(
        String(20),
        default="intermediate",
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    usage_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    __table_args__ = (
        CheckConstraint(
            "category IN ('exhibition', 'technical', 'business', 'daily_life')",
            name="chk_custom_category",
        ),
        CheckConstraint(
            "difficulty IN ('beginner', 'intermediate', 'advanced')",
            name="chk_custom_difficulty",
        ),
    )

    user: Mapped["User"] = relationship(
        "User",
    )
