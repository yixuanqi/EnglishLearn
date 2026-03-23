"""User repository for database operations."""

from datetime import datetime
from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository for User model operations."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(User, session)

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email address."""
        result = await self.session.execute(
            select(User).where(User.email == email.lower())
        )
        return result.scalar_one_or_none()

    async def get_by_stripe_customer_id(self, stripe_customer_id: str) -> Optional[User]:
        """Get user by Stripe customer ID."""
        result = await self.session.execute(
            select(User).where(User.stripe_customer_id == stripe_customer_id)
        )
        return result.scalar_one_or_none()

    async def get_active_users(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> list[User]:
        """Get all active users."""
        result = await self.session.execute(
            select(User)
            .where(User.is_active == True)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_premium_users(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> list[User]:
        """Get all premium users."""
        result = await self.session.execute(
            select(User)
            .where(User.subscription_plan != "free")
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def update_last_login(self, user_id: str) -> None:
        """Update user's last login timestamp."""
        await self.session.execute(
            update(User)
            .where(User.id == user_id)
            .values(last_login_at=datetime.utcnow())
        )

    async def update_subscription(
        self,
        user_id: str,
        plan: str,
        expires_at: Optional[datetime] = None,
    ) -> Optional[User]:
        """Update user's subscription plan."""
        return await self.update(
            user_id,
            {
                "subscription_plan": plan,
                "subscription_expires_at": expires_at,
            },
        )

    async def set_stripe_customer_id(
        self,
        user_id: str,
        stripe_customer_id: str,
    ) -> Optional[User]:
        """Set Stripe customer ID for user."""
        return await self.update(
            user_id,
            {"stripe_customer_id": stripe_customer_id},
        )

    async def verify_email(self, user_id: str) -> Optional[User]:
        """Mark user's email as verified."""
        return await self.update(user_id, {"is_email_verified": True})

    async def deactivate(self, user_id: str) -> Optional[User]:
        """Deactivate user account."""
        return await self.update(user_id, {"is_active": False})

    async def activate(self, user_id: str) -> Optional[User]:
        """Activate user account."""
        return await self.update(user_id, {"is_active": True})

    async def email_exists(self, email: str) -> bool:
        """Check if email is already registered."""
        result = await self.session.execute(
            select(User.id).where(User.email == email.lower())
        )
        return result.scalar_one_or_none() is not None
