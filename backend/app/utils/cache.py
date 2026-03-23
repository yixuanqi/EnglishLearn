"""Cache utilities using Redis."""

import json
from typing import Any, Optional

import redis.asyncio as redis

from app.core.config import settings


class CacheService:
    """Redis cache service."""

    def __init__(self) -> None:
        self.client: Optional[redis.Redis] = None

    async def initialize(self) -> None:
        """Initialize Redis connection."""
        self.client = redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
        )

    async def close(self) -> None:
        """Close Redis connection."""
        if self.client:
            await self.client.close()

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if not self.client:
            return None
        value = await self.client.get(key)
        if value:
            return json.loads(value)
        return None

    async def set(
        self,
        key: str,
        value: Any,
        expire: int = 3600,
    ) -> bool:
        """Set value in cache with expiration."""
        if not self.client:
            return False
        return await self.client.setex(
            key,
            expire,
            json.dumps(value),
        )

    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        if not self.client:
            return False
        return await self.client.delete(key) > 0

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        if not self.client:
            return False
        return await self.client.exists(key) > 0


cache = CacheService()
