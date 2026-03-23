"""Refresh token repository for database operations."""

from datetime import datetime
from typing import Optional

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.refresh_token import RefreshToken
from app.repositories.base import BaseRepository


class RefreshTokenRepository(BaseRepository[RefreshToken]):
    """Repository for RefreshToken model operations."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(RefreshToken, session)

    async def get_by_token_hash(self, token_hash: str) -> Optional[RefreshToken]:
        """Get refresh token by hash."""
        result = await self.session.execute(
            select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        )
        return result.scalar_one_or_none()

    async def get_active_by_user(self, user_id: str) -> list[RefreshToken]:
        """Get all active refresh tokens for a user."""
        result = await self.session.execute(
            select(RefreshToken).where(
                RefreshToken.user_id == user_id,
                RefreshToken.revoked == False,
                RefreshToken.expires_at > datetime.utcnow(),
            )
        )
        return list(result.scalars().all())

    async def revoke(self, token_hash: str) -> bool:
        """Revoke a refresh token."""
        result = await self.session.execute(
            update(RefreshToken)
            .where(RefreshToken.token_hash == token_hash)
            .values(revoked=True, revoked_at=datetime.utcnow())
        )
        return result.rowcount > 0

    async def revoke_all_for_user(self, user_id: str) -> int:
        """Revoke all refresh tokens for a user."""
        result = await self.session.execute(
            update(RefreshToken)
            .where(
                RefreshToken.user_id == user_id,
                RefreshToken.revoked == False,
            )
            .values(revoked=True, revoked_at=datetime.utcnow())
        )
        return result.rowcount

    async def delete_expired(self) -> int:
        """Delete all expired refresh tokens."""
        result = await self.session.execute(
            delete(RefreshToken).where(
                RefreshToken.expires_at < datetime.utcnow()
            )
        )
        return result.rowcount

    async def is_valid(self, token_hash: str) -> bool:
        """Check if a refresh token is valid."""
        result = await self.session.execute(
            select(RefreshToken).where(
                RefreshToken.token_hash == token_hash,
                RefreshToken.revoked == False,
                RefreshToken.expires_at > datetime.utcnow(),
            )
        )
        return result.scalar_one_or_none() is not None

    async def count_active_for_user(self, user_id: str) -> int:
        """Count active refresh tokens for a user."""
        from sqlalchemy import func

        result = await self.session.execute(
            select(func.count()).where(
                RefreshToken.user_id == user_id,
                RefreshToken.revoked == False,
                RefreshToken.expires_at > datetime.utcnow(),
            )
        )
        return result.scalar() or 0
