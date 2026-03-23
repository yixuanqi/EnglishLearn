"""Practice schemas following api_spec.yaml."""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.base import BaseSchema, PaginationMeta


class SessionStatus(str, Enum):
    """Practice session status."""

    ACTIVE = "active"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class StartSessionRequest(BaseModel):
    """Start practice session request."""

    dialogue_id: UUID = Field(..., description="Dialogue UUID")


class UpdateSessionRequest(BaseModel):
    """Update practice session request."""

    status: Optional[SessionStatus] = Field(None, description="Session status")
    current_turn: Optional[int] = Field(None, ge=0, description="Current turn index")
    total_turns: Optional[int] = Field(None, ge=0, description="Total turns")
    ended_at: Optional[datetime] = Field(None, description="End timestamp")


class PracticeSession(BaseSchema):
    """Practice session response."""

    id: str = Field(..., description="Session UUID")
    dialogue_id: str = Field(..., description="Dialogue UUID")
    status: SessionStatus = Field(..., description="Session status")
    current_turn: int = Field(default=0, description="Current turn index")
    total_turns: int = Field(default=0, description="Total turns")
    started_at: datetime = Field(..., description="Start timestamp")
    ended_at: Optional[datetime] = Field(None, description="End timestamp")


class AIResponse(BaseModel):
    """AI response in speech result."""

    text: str = Field(..., description="AI response text")
    audio_url: Optional[str] = Field(None, description="AI audio URL")


class SpeechResult(BaseSchema):
    """Speech submission result."""

    transcription: str = Field(..., description="Speech-to-text transcription")
    expected_text: str = Field(..., description="Expected text from dialogue")
    pronunciation_score: float = Field(
        ...,
        ge=0,
        le=100,
        description="Overall pronunciation score",
    )
    accuracy_score: float = Field(..., ge=0, le=100, description="Accuracy score")
    fluency_score: float = Field(..., ge=0, le=100, description="Fluency score")
    completeness_score: float = Field(
        ...,
        ge=0,
        le=100,
        description="Completeness score",
    )
    feedback: Optional[str] = Field(None, description="Detailed feedback")
    ai_response: Optional[AIResponse] = Field(None, description="AI response")
    next_turn: Optional[int] = Field(None, description="Next turn index")


class SessionResult(BaseSchema):
    """Practice session result."""

    session_id: str = Field(..., description="Session UUID")
    scenario_title: str = Field(..., description="Scenario title")
    duration_seconds: int = Field(..., description="Total duration")
    total_turns: int = Field(..., description="Total turns")
    completed_turns: int = Field(..., description="Completed turns")
    overall_score: float = Field(..., ge=0, le=100, description="Overall score")
    average_accuracy: float = Field(..., description="Average accuracy")
    average_fluency: float = Field(..., description="Average fluency")
    average_completeness: float = Field(..., description="Average completeness")
    strengths: list[str] = Field(default_factory=list, description="Strengths")
    improvements: list[str] = Field(default_factory=list, description="Areas to improve")


class PracticeHistoryResponse(BaseModel):
    """Practice history response."""

    items: list[SessionResult] = Field(..., description="Session results")
    total: int = Field(..., description="Total count")
    page: int = Field(..., description="Current page")
    page_size: int = Field(..., description="Page size")


class PracticeSessionResponse(BaseSchema):
    """Practice session response for start endpoint."""

    session_id: str = Field(..., description="Session UUID")
    scenario_id: str = Field(..., description="Scenario UUID")
    status: SessionStatus = Field(..., description="Session status")
    current_turn: int = Field(default=0, description="Current turn index")
    total_turns: int = Field(default=0, description="Total turns")
    dialogue: list[dict] = Field(default_factory=list, description="Dialogue lines")
    started_at: datetime = Field(..., description="Start timestamp")


class SubmitPracticeRequest(BaseModel):
    """Submit practice turn request."""

    session_id: UUID = Field(..., description="Session UUID")
    transcription: str = Field(..., description="Speech transcription")
    pronunciation_score: float = Field(
        ...,
        ge=0,
        le=100,
        description="Pronunciation score",
    )
    accuracy_score: float = Field(..., ge=0, le=100, description="Accuracy score")
    fluency_score: float = Field(..., ge=0, le=100, description="Fluency score")
    completeness_score: float = Field(
        ...,
        ge=0,
        le=100,
        description="Completeness score",
    )
    feedback: Optional[str] = Field(None, description="Feedback text")


class SubmitPracticeResponse(BaseSchema):
    """Submit practice turn response."""

    session_id: str = Field(..., description="Session UUID")
    turn_index: int = Field(..., description="Turn index")
    result: SpeechResult = Field(..., description="Speech result")
    feedback: Optional[str] = Field(None, description="Feedback text")
    is_completed: bool = Field(..., description="Session completed flag")
    next_turn: Optional[int] = Field(None, description="Next turn index")
