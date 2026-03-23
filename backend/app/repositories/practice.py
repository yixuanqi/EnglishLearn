"""Practice session repository for database operations."""

from datetime import datetime
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.practice import PracticeSession, SpeechResult
from app.repositories.base import BaseRepository


class PracticeSessionRepository(BaseRepository[PracticeSession]):
    """Repository for PracticeSession model operations."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(PracticeSession, session)

    async def get_by_user(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
    ) -> list[PracticeSession]:
        """Get practice sessions by user ID."""
        query = select(PracticeSession).where(PracticeSession.user_id == user_id)

        if status:
            query = query.where(PracticeSession.status == status)

        query = query.order_by(PracticeSession.started_at.desc()).offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_active_session(self, user_id: str) -> Optional[PracticeSession]:
        """Get user's active practice session."""
        result = await self.session.execute(
            select(PracticeSession).where(
                PracticeSession.user_id == user_id,
                PracticeSession.status == "active",
            )
        )
        return result.scalar_one_or_none()

    async def get_completed_sessions(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 100,
    ) -> list[PracticeSession]:
        """Get user's completed practice sessions."""
        result = await self.session.execute(
            select(PracticeSession)
            .where(
                PracticeSession.user_id == user_id,
                PracticeSession.status == "completed",
            )
            .order_by(PracticeSession.started_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def count_by_user(self, user_id: str) -> int:
        """Count sessions for a user."""
        result = await self.session.execute(
            select(func.count()).where(PracticeSession.user_id == user_id)
        )
        return result.scalar() or 0

    async def count_completed_by_user(self, user_id: str) -> int:
        """Count completed sessions for a user."""
        result = await self.session.execute(
            select(func.count()).where(
                PracticeSession.user_id == user_id,
                PracticeSession.status == "completed",
            )
        )
        return result.scalar() or 0

    async def get_sessions_by_date_range(
        self,
        user_id: str,
        start_date: datetime,
        end_date: datetime,
    ) -> list[PracticeSession]:
        """Get sessions within a date range."""
        result = await self.session.execute(
            select(PracticeSession).where(
                PracticeSession.user_id == user_id,
                PracticeSession.started_at >= start_date,
                PracticeSession.started_at <= end_date,
            )
        )
        return list(result.scalars().all())

    async def complete_session(
        self,
        session_id: str,
        overall_score: float,
        average_accuracy: float,
        average_fluency: float,
        average_completeness: float,
        duration_seconds: int,
        feedback: Optional[str] = None,
    ) -> Optional[PracticeSession]:
        """Mark session as completed with scores."""
        return await self.update(
            session_id,
            {
                "status": "completed",
                "ended_at": datetime.utcnow(),
                "duration_seconds": duration_seconds,
                "overall_score": overall_score,
                "average_accuracy": average_accuracy,
                "average_fluency": average_fluency,
                "average_completeness": average_completeness,
                "feedback": feedback,
            },
        )

    async def abandon_session(self, session_id: str) -> Optional[PracticeSession]:
        """Mark session as abandoned."""
        return await self.update(
            session_id,
            {
                "status": "abandoned",
                "ended_at": datetime.utcnow(),
            },
        )

    async def get_user_average_score(self, user_id: str) -> Optional[float]:
        """Get user's average practice score."""
        result = await self.session.execute(
            select(func.avg(PracticeSession.overall_score)).where(
                PracticeSession.user_id == user_id,
                PracticeSession.status == "completed",
            )
        )
        return result.scalar()


class SpeechResultRepository(BaseRepository[SpeechResult]):
    """Repository for SpeechResult model operations."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(SpeechResult, session)

    async def get_by_session(
        self,
        session_id: str,
        skip: int = 0,
        limit: int = 100,
    ) -> list[SpeechResult]:
        """Get speech results by practice session ID."""
        result = await self.session.execute(
            select(SpeechResult)
            .where(SpeechResult.session_id == session_id)
            .order_by(SpeechResult.turn_index)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_session_and_turn(
        self,
        session_id: str,
        turn_index: int,
    ) -> Optional[SpeechResult]:
        """Get speech result for a specific turn."""
        result = await self.session.execute(
            select(SpeechResult).where(
                SpeechResult.session_id == session_id,
                SpeechResult.turn_index == turn_index,
            )
        )
        return result.scalar_one_or_none()

    async def count_by_session(self, session_id: str) -> int:
        """Count speech results for a session."""
        result = await self.session.execute(
            select(func.count()).where(SpeechResult.session_id == session_id)
        )
        return result.scalar() or 0

    async def get_session_average_scores(
        self,
        session_id: str,
    ) -> dict[str, Optional[float]]:
        """Get average scores for a session."""
        result = await self.session.execute(
            select(
                func.avg(SpeechResult.pronunciation_score).label("pronunciation"),
                func.avg(SpeechResult.accuracy_score).label("accuracy"),
                func.avg(SpeechResult.fluency_score).label("fluency"),
                func.avg(SpeechResult.completeness_score).label("completeness"),
            ).where(SpeechResult.session_id == session_id)
        )
        row = result.one()
        return {
            "pronunciation": row.pronunciation,
            "accuracy": row.accuracy,
            "fluency": row.fluency,
            "completeness": row.completeness,
        }
