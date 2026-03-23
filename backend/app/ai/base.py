"""Base AI client."""

from abc import ABC, abstractmethod
from typing import Any, Optional


class BaseAIClient(ABC):
    """Base class for AI service clients."""

    def __init__(self, api_key: Optional[str] = None, **kwargs: Any) -> None:
        self.api_key = api_key
        self.config = kwargs

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the AI client."""
        pass

    @abstractmethod
    async def close(self) -> None:
        """Close the AI client connection."""
        pass
