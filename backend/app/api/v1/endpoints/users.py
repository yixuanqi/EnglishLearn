"""User profile endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.dependencies import get_db
from app.models.user import User
from app.schemas import UpdateProfileRequest, UserProfile

router = APIRouter()


@router.get(
    "/profile",
    response_model=UserProfile,
    summary="Get user profile",
)
async def get_profile(
    current_user: User = Depends(get_current_user),
) -> UserProfile:
    """Retrieve the authenticated user's profile information."""
    return UserProfile(
        id=str(current_user.id),
        email=current_user.email,
        name=current_user.name,
        avatar_url=current_user.avatar_url,
        english_level=current_user.english_level,
        subscription_plan=current_user.subscription_plan,
        subscription_expires_at=current_user.subscription_expires_at,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
    )


@router.put(
    "/profile",
    response_model=UserProfile,
    summary="Update user profile",
)
async def update_profile(
    profile_data: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserProfile:
    """Update the authenticated user's profile information."""
    update_data = profile_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(current_user, field, value)

    await db.commit()
    await db.refresh(current_user)

    return UserProfile(
        id=str(current_user.id),
        email=current_user.email,
        name=current_user.name,
        avatar_url=current_user.avatar_url,
        english_level=current_user.english_level,
        subscription_plan=current_user.subscription_plan,
        subscription_expires_at=current_user.subscription_expires_at,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
    )
