"""Custom exceptions for the application."""

from typing import Any, Optional


class AppException(Exception):
    """Base exception for application errors."""

    def __init__(
        self,
        status_code: int = 500,
        detail: str = "Internal server error",
        headers: Optional[dict[str, Any]] = None,
    ) -> None:
        self.status_code = status_code
        self.detail = detail
        self.headers = headers
        super().__init__(detail)


class NotFoundError(AppException):
    """Resource not found exception."""

    def __init__(self, detail: str = "Resource not found") -> None:
        super().__init__(status_code=404, detail=detail)


class BadRequestError(AppException):
    """Bad request exception."""

    def __init__(self, detail: str = "Bad request") -> None:
        super().__init__(status_code=400, detail=detail)


class UnauthorizedError(AppException):
    """Unauthorized exception."""

    def __init__(self, detail: str = "Unauthorized") -> None:
        super().__init__(status_code=401, detail=detail)


class ForbiddenError(AppException):
    """Forbidden exception."""

    def __init__(self, detail: str = "Forbidden") -> None:
        super().__init__(status_code=403, detail=detail)


class ConflictError(AppException):
    """Conflict exception."""

    def __init__(self, detail: str = "Conflict") -> None:
        super().__init__(status_code=409, detail=detail)


class ValidationError(AppException):
    """Validation exception."""

    def __init__(self, detail: str = "Validation error") -> None:
        super().__init__(status_code=422, detail=detail)


class AIGenerationError(AppException):
    """AI generation exception."""

    def __init__(self, detail: str = "AI generation failed") -> None:
        super().__init__(status_code=500, detail=detail)


class ExternalServiceError(AppException):
    """External service exception."""

    def __init__(self, detail: str = "External service error") -> None:
        super().__init__(status_code=503, detail=detail)
