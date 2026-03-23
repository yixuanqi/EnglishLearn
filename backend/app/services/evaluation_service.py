"""Evaluation service for pronunciation assessment."""

from typing import Optional

from app.schemas.practice import EvaluationResponse


class EvaluationService:
    """Service for pronunciation evaluation."""

    async def evaluate_pronunciation(
        self,
        audio_data: bytes,
        reference_text: str,
        language: str = "en-US",
    ) -> EvaluationResponse:
        """Evaluate pronunciation from audio data."""
        pass
