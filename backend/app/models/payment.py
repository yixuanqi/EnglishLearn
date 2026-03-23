"""Payment model matching database_schema.md."""

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import CheckConstraint, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class Payment(Base):
    """Payment model for recording transactions."""

    __tablename__ = "payments"

    user_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    stripe_payment_intent_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        index=True,
    )
    stripe_subscription_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        index=True,
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )
    currency: Mapped[str] = mapped_column(
        String(3),
        default="USD",
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(30),
        default="pending",
        nullable=False,
        index=True,
    )
    plan_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )
    billing_period: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    payment_metadata: Mapped[dict] = mapped_column(
        JSONB,
        default=dict,
        nullable=False,
    )

    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'succeeded', 'failed', 'refunded', 'cancelled')",
            name="chk_payment_status",
        ),
        CheckConstraint(
            "plan_type IN ('premium_monthly', 'premium_annual')",
            name="chk_plan_type",
        ),
        CheckConstraint(
            "billing_period IN ('monthly', 'annual') OR billing_period IS NULL",
            name="chk_billing_period",
        ),
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="payments",
    )
