"""Base schema with common fields."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class BaseSchema(BaseModel):
    """Base schema with common configuration."""

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        use_enum_values=True,
    )


class MessageResponse(BaseModel):
    """Standard message response."""

    message: str = Field(..., description="Response message")


class ErrorDetail(BaseModel):
    """Error detail schema."""

    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    details: Optional[dict] = Field(None, description="Additional error details")


class ErrorResponse(BaseModel):
    """Standard error response."""

    error: ErrorDetail = Field(..., description="Error information")


class PaginationMeta(BaseModel):
    """Pagination metadata."""

    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Items per page")
    total_pages: Optional[int] = Field(None, description="Total number of pages")
