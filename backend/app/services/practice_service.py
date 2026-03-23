"""Practice service."""

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.practice import PracticeSession
from app.schemas.practice import StartSessionRequest as PracticeSessionCreate, UpdateSessionRequest as PracticeSessionUpdate


class PracticeService:
    """Service for practice session operations."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_session(self, session_id: UUID) -> Optional[PracticeSession]:
        """Get practice session by ID."""
        result = await self.db.execute(
            select(PracticeSession).where(PracticeSession.id == session_id)
        )
        return result.scalar_one_or_none()

    async def create_session(
        self,
        user_id: UUID,
        session_data: PracticeSessionCreate,
    ) -> PracticeSession:
        """Create a new practice session."""
        session = PracticeSession(
            user_id=user_id,
            **session_data.model_dump(),
        )
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        return session

    async def update_session(
        self,
        session_id: UUID,
        session_data: PracticeSessionUpdate,
    ) -> Optional[PracticeSession]:
        """Update an existing practice session."""
        session = await self.get_session(session_id)
        if session is None:
            return None

        update_data = session_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(session, field, value)

        await self.db.commit()
        await self.db.refresh(session)
        return session
