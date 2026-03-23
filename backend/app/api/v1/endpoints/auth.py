"""Authentication endpoints."""

from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.dependencies import get_db
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    hash_token,
    verify_password,
)
from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.schemas import (
    AuthResponse,
    LoginRequest,
    MessageResponse,
    RefreshTokenRequest,
    TokenResponse,
    UpdateProfileRequest,
    UserProfile,
    UserRegistrationRequest,
)

router = APIRouter()


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
async def register(
    user_data: UserRegistrationRequest,
    db: AsyncSession = Depends(get_db),
) -> AuthResponse:
    """Create a new user account with email and password."""
    existing_user = await db.execute(
        select(User).where(User.email == user_data.email)
    )
    if existing_user.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "EMAIL_EXISTS",
                "message": "Email already registered",
            },
        )

    password_hash = get_password_hash(user_data.password)
    user = User(
        email=user_data.email,
        password_hash=password_hash,
        name=user_data.name,
    )
    db.add(user)
    await db.flush()

    access_token = create_access_token(
        subject=str(user.id),
        email=user.email,
        subscription=user.subscription_plan,
    )
    refresh_token = create_refresh_token(str(user.id))

    token_record = RefreshToken(
        user_id=user.id,
        token_hash=hash_token(refresh_token),
        expires_at=datetime.now(timezone.utc)
        + timedelta(days=settings.jwt_refresh_token_expire_days),
    )
    db.add(token_record)
    await db.commit()

    return AuthResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.jwt_access_token_expire_minutes * 60,
        user=UserProfile(
            id=str(user.id),
            email=user.email,
            name=user.name,
            avatar_url=user.avatar_url,
            english_level=user.english_level,
            subscription_plan=user.subscription_plan,
            subscription_expires_at=user.subscription_expires_at,
            created_at=user.created_at,
            updated_at=user.updated_at,
        ),
    )


@router.post(
    "/login",
    response_model=AuthResponse,
    summary="User login",
)
async def login(
    credentials: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> AuthResponse:
    """Authenticate user and return access tokens."""
    result = await db.execute(
        select(User).where(User.email == credentials.email)
    )
    user = result.scalar_one_or_none()

    if user is None or not verify_password(
        credentials.password, user.hashed_password or ""
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "INVALID_CREDENTIALS",
                "message": "Invalid email or password",
            },
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "ACCOUNT_DISABLED",
                "message": "Account is disabled",
            },
        )

    access_token = create_access_token(
        subject=str(user.id),
        email=user.email,
        subscription=user.subscription_plan,
    )
    refresh_token = create_refresh_token(str(user.id))

    token_record = RefreshToken(
        user_id=user.id,
        token_hash=hash_token(refresh_token),
        expires_at=datetime.now(timezone.utc)
        + timedelta(days=settings.jwt_refresh_token_expire_days),
    )
    db.add(token_record)
    await db.commit()

    return AuthResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.jwt_access_token_expire_minutes * 60,
        user=UserProfile(
            id=str(user.id),
            email=user.email,
            name=user.name,
            avatar_url=user.avatar_url,
            english_level=user.english_level,
            subscription_plan=user.subscription_plan,
            subscription_expires_at=user.subscription_expires_at,
            created_at=user.created_at,
            updated_at=user.updated_at,
        ),
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token",
)
async def refresh_token(
    token_data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Get a new access token using refresh token."""
    payload = decode_token(token_data.refresh_token)

    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "INVALID_REFRESH_TOKEN",
                "message": "Invalid or expired refresh token",
            },
        )

    token_hash = hash_token(token_data.refresh_token)
    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.token_hash == token_hash,
            RefreshToken.revoked == False,
        )
    )
    stored_token = result.scalar_one_or_none()

    if stored_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "TOKEN_REVOKED",
                "message": "Refresh token has been revoked",
            },
        )

    if stored_token.expires_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "TOKEN_EXPIRED",
                "message": "Refresh token has expired",
            },
        )

    user_result = await db.execute(
        select(User).where(User.id == payload["sub"])
    )
    user = user_result.scalar_one_or_none()

    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "USER_NOT_FOUND",
                "message": "User not found or inactive",
            },
        )

    await db.execute(
        update(RefreshToken)
        .where(RefreshToken.token_hash == token_hash)
        .values(revoked=True, revoked_at=datetime.now(timezone.utc))
    )

    access_token = create_access_token(
        subject=str(user.id),
        email=user.email,
        subscription=user.subscription_plan,
    )
    new_refresh_token = create_refresh_token(str(user.id))

    new_token_record = RefreshToken(
        user_id=user.id,
        token_hash=hash_token(new_refresh_token),
        expires_at=datetime.now(timezone.utc)
        + timedelta(days=settings.jwt_refresh_token_expire_days),
    )
    db.add(new_token_record)
    await db.commit()

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.jwt_access_token_expire_minutes * 60,
    )


@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="User logout",
)
async def logout(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """Invalidate current session."""
    return MessageResponse(message="Successfully logged out")


@router.get(
    "/me",
    response_model=UserProfile,
    summary="Get current user",
)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
) -> UserProfile:
    """Retrieve the authenticated user's profile."""
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


@router.patch(
    "/me",
    response_model=UserProfile,
    summary="Update user profile",
)
async def update_user_profile(
    profile_data: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserProfile:
    """Update the authenticated user's profile information."""
    update_data = profile_data.model_dump(exclude_unset=True)

    if "interests" in update_data:
        current_user.interests = update_data["interests"]
    if "name" in update_data:
        current_user.name = update_data["name"]
    if "avatar_url" in update_data:
        current_user.avatar_url = update_data["avatar_url"]
    if "english_level" in update_data:
        current_user.english_level = update_data["english_level"]

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
