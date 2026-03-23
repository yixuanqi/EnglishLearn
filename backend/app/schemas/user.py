"""User schemas following api_spec.yaml."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator
import re

from app.schemas.base import BaseSchema


class SubscriptionPlan(str, Enum):
    """Subscription plan types."""

    FREE = "free"
    PREMIUM_MONTHLY = "premium_monthly"
    PREMIUM_ANNUAL = "premium_annual"


class EnglishLevel(str, Enum):
    """English proficiency levels."""

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class UserRegistrationRequest(BaseModel):
    """User registration request schema."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="User password (min 8 characters)",
    )
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="User display name",
    )

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        return v


class LoginRequest(BaseModel):
    """Login request schema."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema."""

    refresh_token: str = Field(..., description="Refresh token")


class UpdateProfileRequest(BaseModel):
    """Update profile request schema."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    avatar_url: Optional[str] = Field(None, description="Avatar URL")
    english_level: Optional[EnglishLevel] = Field(None, description="English level")
    interests: Optional[list[str]] = Field(None, description="User interests")


class UserProfile(BaseSchema):
    """User profile response schema."""

    id: str = Field(..., description="User UUID")
    email: str = Field(..., description="User email")
    name: str = Field(..., description="User display name")
    avatar_url: Optional[str] = Field(None, description="Avatar URL")
    english_level: EnglishLevel = Field(
        default=EnglishLevel.INTERMEDIATE,
        description="English proficiency level",
    )
    subscription_plan: SubscriptionPlan = Field(
        default=SubscriptionPlan.FREE,
        description="Current subscription plan",
    )
    subscription_expires_at: Optional[datetime] = Field(
        None,
        description="Subscription expiry date",
    )
    created_at: datetime = Field(..., description="Account creation date")
    updated_at: datetime = Field(..., description="Last update date")


class TokenResponse(BaseSchema):
    """Token response schema."""

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiry in seconds")


class AuthResponse(BaseSchema):
    """Authentication response schema."""

    access_token: str = Field(..., description="JWT access token (15 min expiry)")
    refresh_token: str = Field(..., description="Refresh token (7 days expiry)")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiry in seconds")
    user: UserProfile = Field(..., description="User profile")
