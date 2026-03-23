"""Dialogue schemas following api_spec.yaml."""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.base import BaseSchema


class SpeakerType(str, Enum):
    """Speaker type in dialogue."""

    USER = "user"
    AI = "ai"


class VocabularyItem(BaseSchema):
    """Vocabulary item in dialogue."""

    word: str
    definition: str
    example: str


class DialogueLine(BaseSchema):
    """Single dialogue line."""

    id: int = Field(..., description="Line ID")
    speaker: SpeakerType = Field(..., description="Speaker type")
    text: str = Field(..., description="Dialogue text")
    translation: Optional[str] = Field(None, description="Translation")
    audio_url: Optional[str] = Field(None, description="Audio URL")


class DialogueCreate(BaseSchema):
    """Dialogue creation schema."""

    id: UUID
    scenario_id: UUID
    variation: int = 1
    lines: list[DialogueLine] = Field(default_factory=list)
    key_vocabulary: list[VocabularyItem] = Field(default_factory=list)
    total_turns: int = 0
    estimated_duration: int = 5


class GenerateDialogueRequest(BaseModel):
    """Generate dialogue request."""

    scenario_id: UUID = Field(..., description="Scenario UUID")
    variation: int = Field(
        default=1,
        ge=1,
        le=5,
        description="Dialogue variation number",
    )


class DialogueResponse(BaseSchema):
    """Dialogue response."""

    id: str = Field(..., description="Dialogue UUID")
    scenario_id: str = Field(..., description="Scenario UUID")
    lines: list[DialogueLine] = Field(..., description="Dialogue lines")
    key_vocabulary: list[VocabularyItem] = Field(default_factory=list)
    total_turns: int = Field(..., description="Total dialogue turns")
    estimated_duration: int = Field(..., description="Estimated duration in minutes")
    created_at: datetime = Field(..., description="Creation timestamp")


class TTSRequest(BaseModel):
    """Text-to-speech request."""

    voice: str = Field(default="default", description="Voice ID")
    speed: float = Field(
        default=1.0,
        ge=0.5,
        le=2.0,
        description="Speech speed",
    )


class TTSResponse(BaseSchema):
    """Text-to-speech response."""

    audio_url: str = Field(..., description="Audio URL")
    duration: float = Field(..., description="Audio duration in seconds")
