"""Scenario endpoints."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_optional_user, require_premium
from app.core.dependencies import get_db
from app.models.scenario import Scenario
from app.models.user import User
from app.schemas import (
    CreateScenarioRequest,
    PaginatedScenarioResponse,
    ScenarioDetail,
    ScenarioSummary,
)
from app.schemas.scenario import DifficultyLevel, ScenarioCategory

router = APIRouter()


@router.get(
    "",
    response_model=PaginatedScenarioResponse,
    summary="List scenarios",
)
async def list_scenarios(
    page: int = Query(default=1, ge=1, description="Page number"),
    limit: int = Query(default=10, ge=1, le=50, description="Items per page"),
    category: Optional[ScenarioCategory] = Query(
        default=None, description="Filter by category"
    ),
    difficulty: Optional[DifficultyLevel] = Query(
        default=None, description="Filter by difficulty"
    ),
    search: Optional[str] = Query(default=None, description="Search query"),
    current_user: Optional[User] = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db),
) -> PaginatedScenarioResponse:
    """Retrieve a paginated list of available scenarios."""
    query = select(Scenario).where(Scenario.is_active == True)

    if category:
        query = query.where(Scenario.category == category.value)

    if difficulty:
        query = query.where(Scenario.difficulty == difficulty.value)

    if search:
        query = query.where(
            Scenario.title.ilike(f"%{search}%")
            | Scenario.description.ilike(f"%{search}%")
        )

    is_premium = current_user and current_user.subscription_plan != "free"
    if not is_premium:
        query = query.where(Scenario.is_premium == False)

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    offset = (page - 1) * limit
    query = query.order_by(Scenario.created_at.desc()).offset(offset).limit(limit)

    result = await db.execute(query)
    scenarios = result.scalars().all()

    items = [
        ScenarioSummary(
            id=str(s.id),
            title=s.title,
            description=s.description or "",
            category=s.category,
            difficulty=s.difficulty,
            estimated_duration=s.estimated_duration,
            is_premium=s.is_premium,
            thumbnail_url=s.thumbnail_url,
        )
        for s in scenarios
    ]

    return PaginatedScenarioResponse(
        items=items,
        total=total,
        page=page,
        limit=limit,
        pages=(total + limit - 1) // limit,
    )


@router.post(
    "",
    response_model=ScenarioDetail,
    status_code=status.HTTP_201_CREATED,
    summary="Create scenario",
)
async def create_scenario(
    scenario_data: CreateScenarioRequest,
    current_user: User = Depends(require_premium),
    db: AsyncSession = Depends(get_db),
) -> ScenarioDetail:
    """Create a new custom scenario (premium feature)."""
    scenario = Scenario(
        title=scenario_data.title,
        description=scenario_data.description,
        category=scenario_data.category.value,
        difficulty=scenario_data.difficulty.value,
        estimated_duration=scenario_data.estimated_duration,
        is_premium=True,
        is_custom=True,
        created_by=current_user.id,
        context=scenario_data.context,
        user_role=scenario_data.user_role,
        ai_role=scenario_data.ai_role,
        key_vocabulary=[v.model_dump() for v in scenario_data.key_vocabulary]
        if scenario_data.key_vocabulary
        else None,
        tips=scenario_data.tips,
    )

    db.add(scenario)
    await db.commit()
    await db.refresh(scenario)

    return ScenarioDetail(
        id=str(scenario.id),
        title=scenario.title,
        description=scenario.description or "",
        category=scenario.category,
        difficulty=scenario.difficulty,
        estimated_duration=scenario.estimated_duration,
        is_premium=scenario.is_premium,
        thumbnail_url=scenario.thumbnail_url,
        context=scenario.context or "",
        user_role=scenario.user_role or "",
        ai_role=scenario.ai_role or "",
        key_vocabulary=scenario.key_vocabulary or [],
        tips=scenario.tips or [],
    )


@router.get(
    "/{scenario_id}",
    response_model=ScenarioDetail,
    summary="Get scenario details",
)
async def get_scenario(
    scenario_id: UUID,
    current_user: Optional[User] = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db),
) -> ScenarioDetail:
    """Retrieve detailed information about a specific scenario."""
    result = await db.execute(
        select(Scenario).where(
            Scenario.id == scenario_id,
            Scenario.is_active == True,
        )
    )
    scenario = result.scalar_one_or_none()

    if scenario is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "SCENARIO_NOT_FOUND",
                "message": "Scenario not found",
            },
        )

    is_premium = current_user and current_user.subscription_plan != "free"
    if scenario.is_premium and not is_premium:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail={
                "code": "PREMIUM_REQUIRED",
                "message": "Premium subscription required for this scenario",
            },
        )

    return ScenarioDetail(
        id=str(scenario.id),
        title=scenario.title,
        description=scenario.description or "",
        category=scenario.category,
        difficulty=scenario.difficulty,
        estimated_duration=scenario.estimated_duration,
        is_premium=scenario.is_premium,
        thumbnail_url=scenario.thumbnail_url,
        context=scenario.context or "",
        user_role=scenario.user_role or "",
        ai_role=scenario.ai_role or "",
        key_vocabulary=scenario.key_vocabulary or [],
        tips=scenario.tips or [],
    )
