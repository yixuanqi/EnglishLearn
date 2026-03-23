"""Base repository with common CRUD operations."""

from typing import Any, Generic, Optional, TypeVar
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Base repository with common CRUD operations."""

    def __init__(self, model: type[ModelType], session: AsyncSession) -> None:
        self.model = model
        self.session = session

    async def create(self, data: dict[str, Any]) -> ModelType:
        """Create a new record."""
        instance = self.model(**data)
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def get_by_id(self, id: str | UUID) -> Optional[ModelType]:
        """Get a record by ID."""
        result = await self.session.execute(
            select(self.model).where(self.model.id == str(id))
        )
        return result.scalar_one_or_none()

    async def get_by_ids(self, ids: list[str]) -> list[ModelType]:
        """Get multiple records by IDs."""
        result = await self.session.execute(
            select(self.model).where(self.model.id.in_(ids))
        )
        return list(result.scalars().all())

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> list[ModelType]:
        """Get all records with pagination."""
        result = await self.session.execute(
            select(self.model).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def count(self) -> int:
        """Count total records."""
        result = await self.session.execute(
            select(func.count()).select_from(self.model)
        )
        return result.scalar() or 0

    async def update(
        self,
        id: str | UUID,
        data: dict[str, Any],
    ) -> Optional[ModelType]:
        """Update a record by ID."""
        instance = await self.get_by_id(id)
        if instance is None:
            return None

        for key, value in data.items():
            setattr(instance, key, value)

        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def delete(self, id: str | UUID) -> bool:
        """Delete a record by ID."""
        instance = await self.get_by_id(id)
        if instance is None:
            return False

        await self.session.delete(instance)
        await self.session.flush()
        return True

    async def exists(self, id: str | UUID) -> bool:
        """Check if a record exists."""
        result = await self.session.execute(
            select(func.count()).where(self.model.id == str(id))
        )
        return (result.scalar() or 0) > 0

    async def create_many(self, data_list: list[dict[str, Any]]) -> list[ModelType]:
        """Create multiple records."""
        instances = [self.model(**data) for data in data_list]
        self.session.add_all(instances)
        await self.session.flush()
        for instance in instances:
            await self.session.refresh(instance)
        return instances

    async def delete_many(self, ids: list[str]) -> int:
        """Delete multiple records by IDs."""
        instances = await self.get_by_ids(ids)
        count = len(instances)
        for instance in instances:
            await self.session.delete(instance)
        await self.session.flush()
        return count
