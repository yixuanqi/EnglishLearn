"""Dialogue repository for database operations."""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dialogue import Dialogue
from app.repositories.base import BaseRepository


class DialogueRepository(BaseRepository[Dialogue]):
    """Repository for Dialogue model operations."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Dialogue, session)

    async def get_by_scenario(
        self,
        scenario_id: str,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Dialogue]:
        """Get dialogues by scenario ID."""
        result = await self.session.execute(
            select(Dialogue)
            .where(Dialogue.scenario_id == scenario_id)
            .order_by(Dialogue.variation)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_scenario_and_variation(
        self,
        scenario_id: str,
        variation: int,
    ) -> Optional[Dialogue]:
        """Get a specific dialogue variation for a scenario."""
        result = await self.session.execute(
            select(Dialogue).where(
                Dialogue.scenario_id == scenario_id,
                Dialogue.variation == variation,
            )
        )
        return result.scalar_one_or_none()

    async def get_first_variation(self, scenario_id: str) -> Optional[Dialogue]:
        """Get the first dialogue variation for a scenario."""
        result = await self.session.execute(
            select(Dialogue)
            .where(Dialogue.scenario_id == scenario_id)
            .order_by(Dialogue.variation)
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_random_variation(self, scenario_id: str) -> Optional[Dialogue]:
        """Get a random dialogue variation for a scenario."""
        result = await self.session.execute(
            select(Dialogue)
            .where(Dialogue.scenario_id == scenario_id)
            .order_by(Dialogue.variation)
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def count_by_scenario(self, scenario_id: str) -> int:
        """Count dialogues for a scenario."""
        from sqlalchemy import func

        result = await self.session.execute(
            select(func.count()).where(Dialogue.scenario_id == scenario_id)
        )
        return result.scalar() or 0

    async def exists_variation(
        self,
        scenario_id: str,
        variation: int,
    ) -> bool:
        """Check if a variation exists for a scenario."""
        result = await self.session.execute(
            select(Dialogue.id).where(
                Dialogue.scenario_id == scenario_id,
                Dialogue.variation == variation,
            )
        )
        return result.scalar_one_or_none() is not None
