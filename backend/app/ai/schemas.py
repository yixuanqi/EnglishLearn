"""Base schemas for AI services."""

from typing import Literal, Optional

from pydantic import BaseModel, Field


class DialogueLine(BaseModel):
    """Single line in a dialogue."""

    id: int
    speaker: Literal["user", "ai"]
    text: str
    translation: Optional[str] = None


class VocabularyItem(BaseModel):
    """Vocabulary item with definition and example."""

    word: str
    definition: str
    example: str


class DialogueContent(BaseModel):
    """Complete dialogue content."""

    lines: list[DialogueLine]
    key_vocabulary: list[VocabularyItem] = Field(default_factory=list)
    total_turns: int
    estimated_duration_minutes: int = 5


class AIResponseContent(BaseModel):
    """AI response content."""

    text: str
    translation: Optional[str] = None
    correction: Optional[str] = None
    encouragement: Optional[str] = None


class WordTimestamp(BaseModel):
    """Word timestamp for STT."""

    word: str
    start_time: float
    end_time: float
    confidence: float


class PhonemeEvaluation(BaseModel):
    """Phoneme-level evaluation."""

    phoneme: str
    accuracy_score: float
    error_type: Optional[Literal["none", "substitution", "insertion", "omission"]] = None


class WordEvaluation(BaseModel):
    """Word-level evaluation."""

    word: str
    accuracy_score: float
    error_type: Optional[Literal["none", "mispronunciation", "omission", "insertion"]] = None
    phonemes: list[PhonemeEvaluation] = Field(default_factory=list)
