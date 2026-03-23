"""Unit tests for base repository."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Column, String, select, func
from sqlalchemy.orm import declarative_base

from app.repositories.base import BaseRepository

TestBase = declarative_base()


class MockModel(TestBase):
    """Mock model for testing."""
    
    __tablename__ = "mock_table"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=True)


class TestBaseRepository:
    """Tests for BaseRepository."""

    @pytest.fixture
    def mock_session(self):
        """Create mock database session."""
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def repository(self, mock_session):
        """Create repository instance."""
        return BaseRepository(MockModel, mock_session)

    @pytest.mark.asyncio
    async def test_create_success(self, repository, mock_session):
        """Test successful record creation."""
        mock_session.flush = AsyncMock()
        mock_session.refresh = AsyncMock()
        
        data = {"id": str(uuid4()), "name": "Test"}
        result = await repository.create(data)
        
        assert isinstance(result, MockModel)
        mock_session.add.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_id_found(self, repository, mock_session):
        """Test getting record by ID when found."""
        test_id = str(uuid4())
        mock_instance = MockModel(id=test_id, name="Test")
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_instance
        mock_session.execute.return_value = mock_result
        
        result = await repository.get_by_id(test_id)
        
        assert result == mock_instance

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, repository, mock_session):
        """Test getting record by ID when not found."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result
        
        result = await repository.get_by_id("nonexistent-id")
        
        assert result is None

    @pytest.mark.asyncio
    async def test_get_by_id_with_uuid(self, repository, mock_session):
        """Test getting record by UUID."""
        test_uuid = uuid4()
        mock_instance = MockModel(id=str(test_uuid), name="Test")
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_instance
        mock_session.execute.return_value = mock_result
        
        result = await repository.get_by_id(test_uuid)
        
        assert result == mock_instance

    @pytest.mark.asyncio
    async def test_get_by_ids_multiple(self, repository, mock_session):
        """Test getting multiple records by IDs."""
        id1 = str(uuid4())
        id2 = str(uuid4())
        mock_instances = [MockModel(id=id1, name="Test1"), MockModel(id=id2, name="Test2")]
        
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_instances
        mock_session.execute.return_value = mock_result
        
        result = await repository.get_by_ids([id1, id2])
        
        assert len(result) == 2
        assert result == mock_instances

    @pytest.mark.asyncio
    async def test_get_by_ids_empty(self, repository, mock_session):
        """Test getting records by empty ID list."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute.return_value = mock_result
        
        result = await repository.get_by_ids([])
        
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_get_all_with_pagination(self, repository, mock_session):
        """Test getting all records with pagination."""
        mock_instances = [MockModel(id=str(uuid4()), name=f"Test{i}") for i in range(5)]
        
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_instances
        mock_session.execute.return_value = mock_result
        
        result = await repository.get_all(skip=10, limit=5)
        
        assert len(result) == 5

    @pytest.mark.asyncio
    async def test_get_all_default_pagination(self, repository, mock_session):
        """Test getting all records with default pagination."""
        mock_instances = [MockModel(id=str(uuid4()), name=f"Test{i}") for i in range(100)]
        
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_instances
        mock_session.execute.return_value = mock_result
        
        result = await repository.get_all()
        
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_count_returns_integer(self, repository, mock_session):
        """Test count returns integer."""
        mock_result = MagicMock()
        mock_result.scalar.return_value = 42
        mock_session.execute.return_value = mock_result
        
        result = await repository.count()
        
        assert result == 42

    @pytest.mark.asyncio
    async def test_count_zero(self, repository, mock_session):
        """Test count returns zero for empty table."""
        mock_result = MagicMock()
        mock_result.scalar.return_value = 0
        mock_session.execute.return_value = mock_result
        
        result = await repository.count()
        
        assert result == 0

    @pytest.mark.asyncio
    async def test_update_found(self, repository, mock_session):
        """Test updating record when found."""
        test_id = str(uuid4())
        mock_instance = MockModel(id=test_id, name="Old Name")
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_instance
        mock_session.execute.return_value = mock_result
        mock_session.flush = AsyncMock()
        mock_session.refresh = AsyncMock()
        
        result = await repository.update(test_id, {"name": "New Name"})
        
        assert result == mock_instance
        mock_session.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_not_found(self, repository, mock_session):
        """Test updating record when not found."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result
        
        result = await repository.update("nonexistent-id", {"name": "New Name"})
        
        assert result is None

    @pytest.mark.asyncio
    async def test_delete_found(self, repository, mock_session):
        """Test deleting record when found."""
        test_id = str(uuid4())
        mock_instance = MockModel(id=test_id, name="Test")
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_instance
        mock_session.execute.return_value = mock_result
        mock_session.delete = AsyncMock()
        mock_session.flush = AsyncMock()
        
        result = await repository.delete(test_id)
        
        assert result is True

    @pytest.mark.asyncio
    async def test_delete_not_found(self, repository, mock_session):
        """Test deleting record when not found."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result
        
        result = await repository.delete("nonexistent-id")
        
        assert result is False

    @pytest.mark.asyncio
    async def test_exists_true(self, repository, mock_session):
        """Test exists returns True when record exists."""
        mock_result = MagicMock()
        mock_result.scalar.return_value = 1
        mock_session.execute.return_value = mock_result
        
        result = await repository.exists("existing-id")
        
        assert result is True

    @pytest.mark.asyncio
    async def test_exists_false(self, repository, mock_session):
        """Test exists returns False when record does not exist."""
        mock_result = MagicMock()
        mock_result.scalar.return_value = 0
        mock_session.execute.return_value = mock_result
        
        result = await repository.exists("nonexistent-id")
        
        assert result is False

    @pytest.mark.asyncio
    async def test_create_many_success(self, repository, mock_session):
        """Test creating multiple records."""
        mock_session.flush = AsyncMock()
        mock_session.refresh = AsyncMock()
        mock_session.add_all = MagicMock()
        
        data_list = [
            {"id": str(uuid4()), "name": "Test1"},
            {"id": str(uuid4()), "name": "Test2"},
            {"id": str(uuid4()), "name": "Test3"},
        ]
        
        result = await repository.create_many(data_list)
        
        assert len(result) == 3
        mock_session.add_all.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_many_empty(self, repository, mock_session):
        """Test creating empty list of records."""
        mock_session.flush = AsyncMock()
        mock_session.refresh = AsyncMock()
        
        result = await repository.create_many([])
        
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_delete_many_success(self, repository, mock_session):
        """Test deleting multiple records."""
        id1 = str(uuid4())
        id2 = str(uuid4())
        mock_instances = [MockModel(id=id1, name="Test1"), MockModel(id=id2, name="Test2")]
        
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_instances
        mock_session.execute.return_value = mock_result
        mock_session.delete = AsyncMock()
        mock_session.flush = AsyncMock()
        
        result = await repository.delete_many([id1, id2])
        
        assert result == 2

    @pytest.mark.asyncio
    async def test_delete_many_not_found(self, repository, mock_session):
        """Test deleting records when none found."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute.return_value = mock_result
        mock_session.flush = AsyncMock()
        
        result = await repository.delete_many(["nonexistent1", "nonexistent2"])
        
        assert result == 0


class TestBaseRepositoryEdgeCases:
    """Edge case tests for BaseRepository."""

    @pytest.fixture
    def mock_session(self):
        """Create mock database session."""
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def repository(self, mock_session):
        """Create repository instance."""
        return BaseRepository(MockModel, mock_session)

    @pytest.mark.asyncio
    async def test_get_all_large_limit(self, repository, mock_session):
        """Test getting all records with large limit."""
        mock_instances = [MockModel(id=str(uuid4()), name=f"Test{i}") for i in range(1000)]
        
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_instances
        mock_session.execute.return_value = mock_result
        
        result = await repository.get_all(limit=1000)
        
        assert len(result) == 1000

    @pytest.mark.asyncio
    async def test_get_all_large_skip(self, repository, mock_session):
        """Test getting all records with large skip."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute.return_value = mock_result
        
        result = await repository.get_all(skip=10000)
        
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_update_with_empty_data(self, repository, mock_session):
        """Test updating with empty data dict."""
        test_id = str(uuid4())
        mock_instance = MockModel(id=test_id, name="Test")
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_instance
        mock_session.execute.return_value = mock_result
        mock_session.flush = AsyncMock()
        mock_session.refresh = AsyncMock()
        
        result = await repository.update(test_id, {})
        
        assert result == mock_instance

    @pytest.mark.asyncio
    async def test_create_with_many_fields(self, repository, mock_session):
        """Test creating record with many fields."""
        mock_session.flush = AsyncMock()
        mock_session.refresh = AsyncMock()
        
        data = {"id": str(uuid4()), "name": "Test"}
        result = await repository.create(data)
        
        assert isinstance(result, MockModel)

    @pytest.mark.asyncio
    async def test_get_by_ids_single_id(self, repository, mock_session):
        """Test getting records with single ID."""
        test_id = str(uuid4())
        mock_instance = MockModel(id=test_id, name="Test")
        
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_instance]
        mock_session.execute.return_value = mock_result
        
        result = await repository.get_by_ids([test_id])
        
        assert len(result) == 1
        assert result[0] == mock_instance
