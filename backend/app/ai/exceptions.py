"""AI service exceptions and error handling."""

from typing import Any, Optional


class AIServiceError(Exception):
    """Base exception for AI services."""

    def __init__(
        self,
        service: str,
        message: str,
        details: Optional[Any] = None,
    ) -> None:
        self.service = service
        self.message = message
        self.details = details
        super().__init__(f"[{service}] {message}")


class LLMServiceError(AIServiceError):
    """Exception for LLM service errors."""

    def __init__(self, message: str, details: Optional[Any] = None) -> None:
        super().__init__("LLM", message, details)


class TTSServiceError(AIServiceError):
    """Exception for TTS service errors."""

    def __init__(self, message: str, details: Optional[Any] = None) -> None:
        super().__init__("TTS", message, details)


class STTServiceError(AIServiceError):
    """Exception for STT service errors."""

    def __init__(self, message: str, details: Optional[Any] = None) -> None:
        super().__init__("STT", message, details)


class PronunciationError(AIServiceError):
    """Exception for pronunciation evaluation errors."""

    def __init__(self, message: str, details: Optional[Any] = None) -> None:
        super().__init__("Pronunciation", message, details)


class RateLimitError(AIServiceError):
    """Exception for rate limiting errors."""

    def __init__(
        self,
        service: str,
        retry_after: Optional[int] = None,
    ) -> None:
        self.retry_after = retry_after
        super().__init__(service, "Rate limit exceeded", {"retry_after": retry_after})


class ServiceUnavailableError(AIServiceError):
    """Exception for service unavailability."""

    def __init__(self, service: str, details: Optional[Any] = None) -> None:
        super().__init__(service, "Service temporarily unavailable", details)


class QuotaExceededError(AIServiceError):
    """Exception for quota exceeded errors."""

    def __init__(self, service: str) -> None:
        super().__init__(service, "API quota exceeded")
