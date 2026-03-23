"""Scenario service."""

from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.scenario import Scenario
from app.schemas.scenario import CreateScenarioRequest as ScenarioCreate, UpdateScenarioRequest as ScenarioUpdate


class ScenarioService:
    """Service for scenario operations."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_scenarios(
        self,
        category: Optional[str] = None,
        difficulty: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Scenario], int]:
        """List scenarios with optional filters."""
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

    async def get_scenario(self, scenario_id: str) -> Optional[Scenario]:
        """Get scenario by ID."""
        result = await self.db.execute(
            select(Scenario).where(Scenario.id == scenario_id)
        )
        return result.scalar_one_or_none()

    async def create_scenario(self, scenario_data: ScenarioCreate) -> Scenario:
        """Create a new scenario."""
        scenario = Scenario(**scenario_data.model_dump())
        self.db.add(scenario)
        await self.db.commit()
        await self.db.refresh(scenario)
        return scenario

    async def update_scenario(
        self,
        scenario_id: str,
        scenario_data: ScenarioUpdate,
    ) -> Optional[Scenario]:
        """Update an existing scenario."""
        scenario = await self.get_scenario(scenario_id)
        if scenario is None:
            return None

        update_data = scenario_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(scenario, field, value)

        await self.db.commit()
        await self.db.refresh(scenario)
        return scenario
