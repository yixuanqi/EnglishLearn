"""Payment service."""

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.payment import Payment
from app.schemas.payment import PaymentIntentCreate


class PaymentService:
    """Service for payment operations."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_payment_intent(
        self,
        user_id: str,
        payment_data: PaymentIntentCreate,
    ) -> dict:
        """Create a Stripe payment intent."""
        pass

    async def confirm_payment(self, payment_intent_id: str) -> Optional[Payment]:
        """Confirm a payment after successful Stripe webhook."""
        pass
