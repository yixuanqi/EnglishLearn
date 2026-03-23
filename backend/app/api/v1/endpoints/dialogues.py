"""Dialogue endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.core.dependencies import get_db
from app.models.user import User
from app.schemas.dialogue import DialogueResponse
from app.services.dialogue_service import DialogueService

router = APIRouter()


@router.post("/generate", response_model=DialogueResponse)
async def generate_dialogue(
    scenario_id: UUID,
    variation: int = 1,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> DialogueResponse:
    """Generate a dialogue for a scenario using AI."""
    try:
        service = DialogueService(db)
        dialogue = await service.generate_dialogue(
            scenario_id=scenario_id,
            variation=variation,
        )
        return dialogue
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate dialogue: {str(e)}",
        )


@router.get("/{dialogue_id}", response_model=DialogueResponse)
async def get_dialogue(
    dialogue_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> DialogueResponse:
    """Get dialogue by ID."""
    service = DialogueService(db)
    dialogue = await service.get_dialogue(dialogue_id)
    if not dialogue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dialogue not found",
        )
    return dialogue
