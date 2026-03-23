"""Pronunciation evaluation endpoints."""

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.core.dependencies import get_db
from app.models.user import User
from app.schemas.evaluation import EvaluationResponse

router = APIRouter()


@router.post("/pronunciation", response_model=EvaluationResponse)
async def evaluate_pronunciation(
    audio_file: UploadFile = File(..., description="Audio file for evaluation"),
    reference_text: str = ...,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> EvaluationResponse:
    """Evaluate user pronunciation from audio file."""
    pass
