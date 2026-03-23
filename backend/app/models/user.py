"""User model matching database_schema.md."""
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, DateTime, String, Text, CheckConstraint
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.practice import PracticeSession
    from app.models.payment import Payment
    from app.models.refresh_token import RefreshToken


class User(Base):
    """User model for authentication and profile."""

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    avatar_url: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    english_level: Mapped[str] = mapped_column(
        String(20),
        default="intermediate",
        nullable=False,
    )
    subscription_plan: Mapped[str] = mapped_column(
        String(30),
        default="free",
        nullable=False,
        index=True,
    )
    subscription_expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    stripe_customer_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        index=True,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    is_email_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    last_login_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    __table_args__ = (
        CheckConstraint(
            "english_level IN ('beginner', 'intermediate', 'advanced')",
            name="chk_english_level",
        ),
        CheckConstraint(
            "subscription_plan IN ('free', 'premium_monthly', 'premium_annual')",
            name="chk_subscription_plan",
        ),
    )

    practice_sessions: Mapped[list["PracticeSession"]] = relationship(
        "PracticeSession",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    payments: Mapped[list["Payment"]] = relationship(
        "Payment",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(
        "RefreshToken",
        back_populates="user",
        cascade="all, delete-orphan",
    )
