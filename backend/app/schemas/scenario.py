"""Scenario schemas following api_spec.yaml."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.base import BaseSchema, PaginationMeta


class ScenarioCategory(str, Enum):
    """Scenario category types."""

    EXHIBITION = "exhibition"
    TECHNICAL = "technical"
    BUSINESS = "business"
    DAILY_LIFE = "daily_life"


class DifficultyLevel(str, Enum):
    """Difficulty level types."""

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class VocabularyItem(BaseModel):
    """Vocabulary item for scenario."""

    word: str = Field(..., description="Vocabulary word")
    definition: str = Field(..., description="Word definition")
    example: str = Field(..., description="Example sentence")


class ScenarioSummary(BaseSchema):
    """Scenario summary for list view."""

    id: str = Field(..., description="Scenario UUID")
    title: str = Field(..., description="Scenario title")
    description: str = Field(..., description="Brief description")
    category: ScenarioCategory = Field(..., description="Scenario category")
    difficulty: DifficultyLevel = Field(..., description="Difficulty level")
    estimated_duration: int = Field(..., description="Estimated duration in minutes")
    is_premium: bool = Field(default=False, description="Premium only flag")
    thumbnail_url: Optional[str] = Field(None, description="Thumbnail URL")


class ScenarioDetail(ScenarioSummary):
    """Detailed scenario information."""

    context: str = Field(..., description="Detailed scenario context")
    user_role: str = Field(..., description="Role the user will play")
    ai_role: str = Field(..., description="Role the AI will play")
    key_vocabulary: list[VocabularyItem] = Field(
        default_factory=list,
        description="Key vocabulary items",
    )
    tips: list[str] = Field(default_factory=list, description="Practice tips")


class CategoryInfo(BaseSchema):
    """Category information."""

    id: ScenarioCategory = Field(..., description="Category ID")
    name: str = Field(..., description="Category display name")
    description: str = Field(..., description="Category description")
    scenario_count: int = Field(default=0, description="Number of scenarios")
    icon: Optional[str] = Field(None, description="Category icon")


class ScenarioListResponse(BaseModel):
    """Scenario list response with pagination."""

    items: list[ScenarioSummary] = Field(..., description="Scenario list")
    total: int = Field(..., description="Total count")
    page: int = Field(..., description="Current page")
    page_size: int = Field(..., description="Page size")
    total_pages: int = Field(..., description="Total pages")


class PaginatedScenarioResponse(BaseModel):
    """Paginated scenario response."""

    items: list[ScenarioSummary] = Field(..., description="Scenario list")
    total: int = Field(..., description="Total count")
    page: int = Field(..., description="Current page")
    limit: int = Field(..., description="Items per page")
    pages: int = Field(..., description="Total pages")


class CategoryListResponse(BaseModel):
    """Category list response."""

    categories: list[CategoryInfo] = Field(..., description="Category list")


class CreateScenarioRequest(BaseModel):
    """Create scenario request."""

    title: str = Field(..., max_length=200, description="Scenario title")
    description: Optional[str] = Field(None, max_length=500, description="Description")
    category: ScenarioCategory = Field(..., description="Scenario category")
    context: str = Field(..., max_length=2000, description="Scenario context")
    user_role: str = Field(..., max_length=200, description="User role")
    ai_role: str = Field(..., max_length=200, description="AI role")
    difficulty: DifficultyLevel = Field(
        default=DifficultyLevel.INTERMEDIATE,
        description="Difficulty level",
    )
    estimated_duration: int = Field(default=15, description="Estimated duration in minutes")
    key_vocabulary: Optional[list[VocabularyItem]] = Field(
        None, description="Key vocabulary items"
    )
    tips: Optional[list[str]] = Field(None, description="Practice tips")


class UpdateScenarioRequest(BaseModel):
    """Update scenario request."""

    title: Optional[str] = Field(None, max_length=200, description="Scenario title")
    description: Optional[str] = Field(None, max_length=500, description="Description")
    category: Optional[ScenarioCategory] = Field(None, description="Scenario category")
    context: Optional[str] = Field(None, max_length=2000, description="Scenario context")
    user_role: Optional[str] = Field(None, max_length=200, description="User role")
    ai_role: Optional[str] = Field(None, max_length=200, description="AI role")
    difficulty: Optional[DifficultyLevel] = Field(None, description="Difficulty level")
    estimated_duration: Optional[int] = Field(None, description="Estimated duration in minutes")
    key_vocabulary: Optional[list[VocabularyItem]] = Field(None, description="Key vocabulary items")
    tips: Optional[list[str]] = Field(None, description="Practice tips")
    is_active: Optional[bool] = Field(None, description="Is active flag")
