"""Scenario repository for database operations."""

from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.scenario import Scenario
from app.repositories.base import BaseRepository


class ScenarioRepository(BaseRepository[Scenario]):
    """Repository for Scenario model operations."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Scenario, session)

    async def get_by_category(
        self,
        category: str,
        skip: int = 0,
        limit: int = 100,
        include_premium: bool = True,
    ) -> list[Scenario]:
        """Get scenarios by category."""
        query = select(Scenario).where(
            Scenario.category == category,
            Scenario.is_active == True,
        )

        if not include_premium:
            query = query.where(Scenario.is_premium == False)

        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_difficulty(
        self,
        difficulty: str,
        skip: int = 0,
        limit: int = 100,
        include_premium: bool = True,
    ) -> list[Scenario]:
        """Get scenarios by difficulty level."""
        query = select(Scenario).where(
            Scenario.difficulty == difficulty,
            Scenario.is_active == True,
        )

        if not include_premium:
            query = query.where(Scenario.is_premium == False)

        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_free_scenarios(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Scenario]:
        """Get free (non-premium) scenarios."""
        result = await self.session.execute(
            select(Scenario)
            .where(
                Scenario.is_premium == False,
                Scenario.is_active == True,
            )
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_premium_scenarios(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Scenario]:
        """Get premium scenarios."""
        result = await self.session.execute(
            select(Scenario)
            .where(
                Scenario.is_premium == True,
                Scenario.is_active == True,
            )
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_active_scenarios(
        self,
        skip: int = 0,
        limit: int = 100,
        include_premium: bool = True,
    ) -> list[Scenario]:
        """Get all active scenarios."""
        query = select(Scenario).where(Scenario.is_active == True)

        if not include_premium:
            query = query.where(Scenario.is_premium == False)

        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def search(
        self,
        query_text: str,
        skip: int = 0,
        limit: int = 100,
        include_premium: bool = True,
    ) -> list[Scenario]:
        """Search scenarios by title or description."""
        query = select(Scenario).where(
            Scenario.is_active == True,
            Scenario.title.ilike(f"%{query_text}%")
            | Scenario.description.ilike(f"%{query_text}%"),
        )

        if not include_premium:
            query = query.where(Scenario.is_premium == False)

        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def count_by_category(self, category: str) -> int:
        """Count scenarios in a category."""
        result = await self.session.execute(
            select(func.count()).where(
                Scenario.category == category,
                Scenario.is_active == True,
            )
        )
        return result.scalar() or 0

    async def count_by_difficulty(self, difficulty: str) -> int:
        """Count scenarios by difficulty."""
        result = await self.session.execute(
            select(func.count()).where(
                Scenario.difficulty == difficulty,
                Scenario.is_active == True,
            )
        )
        return result.scalar() or 0

    async def deactivate(self, scenario_id: str) -> Optional[Scenario]:
        """Deactivate a scenario."""
        return await self.update(scenario_id, {"is_active": False})

    async def activate(self, scenario_id: str) -> Optional[Scenario]:
        """Activate a scenario."""
        return await self.update(scenario_id, {"is_active": True})
