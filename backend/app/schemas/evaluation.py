"""Evaluation schemas following api_spec.yaml."""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.base import BaseSchema


class ErrorType(str, Enum):
    """Pronunciation error types."""

    NONE = "none"
    MISPRONUNCIATION = "mispronunciation"
    OMISSION = "omission"
    INSERTION = "insertion"


class PhonemeEvaluation(BaseModel):
    """Phoneme level evaluation."""

    phoneme: str = Field(..., description="Phoneme symbol")
    accuracy_score: float = Field(..., ge=0, le=100, description="Accuracy score")


class WordEvaluation(BaseSchema):
    """Word level evaluation."""

    word: str = Field(..., description="Word")
    accuracy_score: float = Field(..., ge=0, le=100, description="Accuracy score")
    error_type: Optional[ErrorType] = Field(None, description="Error type")
    phonemes: list[PhonemeEvaluation] = Field(
        default_factory=list,
        description="Phoneme evaluations",
    )


class BasicEvaluationResult(BaseSchema):
    """Basic pronunciation evaluation result."""

    transcription: str = Field(..., description="Speech transcription")
    overall_score: float = Field(..., ge=0, le=100, description="Overall score")
    accuracy_score: float = Field(..., ge=0, le=100, description="Accuracy score")
    fluency_score: float = Field(..., ge=0, le=100, description="Fluency score")
    completeness_score: float = Field(
        ...,
        ge=0,
        le=100,
        description="Completeness score",
    )
    feedback: Optional[str] = Field(None, description="Feedback")


class AdvancedEvaluationResult(BasicEvaluationResult):
    """Advanced pronunciation evaluation result with word-level details."""

    word_evaluations: list[WordEvaluation] = Field(
        default_factory=list,
        description="Word-level evaluations",
    )


class EvaluationResponse(BaseSchema):
    """Evaluation response."""

    session_id: str = Field(..., description="Session UUID")
    is_correct: bool = Field(..., description="Whether pronunciation is correct")
    score: float = Field(..., ge=0, le=100, description="Score")
    feedback: str = Field(..., description="Feedback")
    suggested_corrections: list[str] = Field(
        default_factory=list,
        description="Suggested corrections",
    )
    detailed_result: Optional[AdvancedEvaluationResult] = Field(
        None, description="Detailed evaluation result"
    )
