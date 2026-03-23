"""Core module."""

from app.core.config import settings
from app.core.dependencies import get_db

__all__ = ["settings", "get_db"]
