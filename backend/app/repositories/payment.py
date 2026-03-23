"""Payment repository for database operations."""

from datetime import datetime
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.payment import Payment
from app.repositories.base import BaseRepository


class PaymentRepository(BaseRepository[Payment]):
    """Repository for Payment model operations."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Payment, session)

    async def get_by_user(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Payment]:
        """Get payments by user ID."""
        result = await self.session.execute(
            select(Payment)
            .where(Payment.user_id == user_id)
            .order_by(Payment.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_stripe_payment_intent(
        self,
        stripe_payment_intent_id: str,
    ) -> Optional[Payment]:
        """Get payment by Stripe payment intent ID."""
        result = await self.session.execute(
            select(Payment).where(
                Payment.stripe_payment_intent_id == stripe_payment_intent_id
            )
        )
        return result.scalar_one_or_none()

    async def get_by_stripe_subscription(
        self,
        stripe_subscription_id: str,
    ) -> Optional[Payment]:
        """Get payment by Stripe subscription ID."""
        result = await self.session.execute(
            select(Payment).where(
                Payment.stripe_subscription_id == stripe_subscription_id
            )
        )
        return result.scalar_one_or_none()

    async def get_successful_payments(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Payment]:
        """Get successful payments for a user."""
        result = await self.session.execute(
            select(Payment)
            .where(
                Payment.user_id == user_id,
                Payment.status == "succeeded",
            )
            .order_by(Payment.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_pending_payments(
        self,
        user_id: str,
    ) -> list[Payment]:
        """Get pending payments for a user."""
        result = await self.session.execute(
            select(Payment).where(
                Payment.user_id == user_id,
                Payment.status == "pending",
            )
        )
        return list(result.scalars().all())

    async def count_by_user(self, user_id: str) -> int:
        """Count payments for a user."""
        result = await self.session.execute(
            select(func.count()).where(Payment.user_id == user_id)
        )
        return result.scalar() or 0

    async def get_total_amount_by_user(
        self,
        user_id: str,
        status: str = "succeeded",
    ) -> float:
        """Get total payment amount for a user."""
        result = await self.session.execute(
            select(func.sum(Payment.amount)).where(
                Payment.user_id == user_id,
                Payment.status == status,
            )
        )
        return result.scalar() or 0.0

    async def mark_succeeded(
        self,
        payment_id: str,
        stripe_payment_intent_id: Optional[str] = None,
    ) -> Optional[Payment]:
        """Mark payment as succeeded."""
        update_data = {"status": "succeeded"}
        if stripe_payment_intent_id:
            update_data["stripe_payment_intent_id"] = stripe_payment_intent_id
        return await self.update(payment_id, update_data)

    async def mark_failed(self, payment_id: str) -> Optional[Payment]:
        """Mark payment as failed."""
        return await self.update(payment_id, {"status": "failed"})

    async def mark_refunded(self, payment_id: str) -> Optional[Payment]:
        """Mark payment as refunded."""
        return await self.update(payment_id, {"status": "refunded"})

    async def mark_cancelled(self, payment_id: str) -> Optional[Payment]:
        """Mark payment as cancelled."""
        return await self.update(payment_id, {"status": "cancelled"})

    async def get_payments_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Payment]:
        """Get payments within a date range."""
        result = await self.session.execute(
            select(Payment)
            .where(
                Payment.created_at >= start_date,
                Payment.created_at <= end_date,
            )
            .order_by(Payment.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
