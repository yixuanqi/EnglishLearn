"""Scenario repository."""

from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.scenario import Scenario
from app.repositories.base import BaseRepository


class ScenarioRepository(BaseRepository[Scenario]):
    """Repository for Scenario model."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(Scenario, db)

    async def list_active(
        self,
        category: Optional[str] = None,
        difficulty: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Scenario], int]:
        """List active scenarios with filters."""
        query = select(Scenario).where(Scenario.is_active == True)

        if category:
            query = query.where(Scenario.category == category)
        if difficulty:
            query = query.where(Scenario.difficulty == difficulty)

        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.db.execute(count_query)).scalar()

        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await self.db.execute(query)
        scenarios = list(result.scalars().all())

        return scenarios, total
