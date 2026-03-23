"""Practice repository."""

from typing import Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.practice import PracticeSession
from app.repositories.base import BaseRepository


class PracticeRepository(BaseRepository[PracticeSession]):
    """Repository for PracticeSession model."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(PracticeSession, db)

    async def get_user_sessions(
        self,
        user_id: UUID,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[PracticeSession], int]:
        """Get practice sessions for a user."""
        query = select(PracticeSession).where(
            PracticeSession.user_id == user_id
        ).order_by(PracticeSession.created_at.desc())

        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.db.execute(count_query)).scalar()

        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await self.db.execute(query)
        sessions = list(result.scalars().all())

        return sessions, total

    async def get_session_by_id(
        self,
        session_id: UUID,
        user_id: UUID,
    ) -> Optional[PracticeSession]:
        """Get practice session by ID for a specific user."""
        result = await self.db.execute(
            select(PracticeSession).where(
                PracticeSession.id == session_id,
                PracticeSession.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()
