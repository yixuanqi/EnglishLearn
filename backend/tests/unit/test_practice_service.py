"""Unit tests for practice service."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.practice_service import PracticeService
from app.schemas.practice import StartSessionRequest, SessionStatus
from app.models.practice import PracticeSession


class MockPracticeSessionUpdate:
    """Mock update request for testing."""
    
    def __init__(self, **kwargs):
        self._data = kwargs
    
    def model_dump(self, exclude_unset=False):
        return self._data


class TestPracticeService:
    """Tests for PracticeService."""

    @pytest.fixture
    def mock_db(self):
        """Create mock database session."""
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def practice_service(self, mock_db):
        """Create practice service instance."""
        return PracticeService(mock_db)

    @pytest.fixture
    def sample_session_create(self):
        """Create sample practice session creation data."""
        return StartSessionRequest(
            dialogue_id=uuid4(),
        )

    @pytest.fixture
    def sample_session_update(self):
        """Create sample practice session update data."""
        return MockPracticeSessionUpdate(
            status=SessionStatus.COMPLETED,
        )

    @pytest.mark.asyncio
    async def test_get_session_found(self, practice_service, mock_db):
        """Test getting practice session by ID when found."""
        mock_session = MagicMock(spec=PracticeSession)
        mock_session.id = str(uuid4())
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_session
        mock_db.execute.return_value = mock_result
        
        result = await practice_service.get_session(mock_session.id)
        
        assert result == mock_session

    @pytest.mark.asyncio
    async def test_get_session_not_found(self, practice_service, mock_db):
        """Test getting practice session by ID when not found."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result
        
        result = await practice_service.get_session(str(uuid4()))
        
        assert result is None

    @pytest.mark.asyncio
    async def test_create_session_success(self, practice_service, mock_db, sample_session_create):
        """Test successful practice session creation."""
        user_id = uuid4()
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()
        
        result = await practice_service.create_session(user_id, sample_session_create)
        
        assert isinstance(result, PracticeSession)
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_session_found(self, practice_service, mock_db, sample_session_update):
        """Test updating practice session when found."""
        session_id = uuid4()
        mock_session = MagicMock(spec=PracticeSession)
        mock_session.id = str(session_id)
        mock_session.status = SessionStatus.ACTIVE
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_session
        mock_db.execute.return_value = mock_result
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()
        
        result = await practice_service.update_session(
            session_id,
            sample_session_update
        )
        
        assert result == mock_session
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_session_not_found(self, practice_service, mock_db, sample_session_update):
        """Test updating practice session when not found."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result
        
        result = await practice_service.update_session(
            uuid4(),
            sample_session_update
        )
        
        assert result is None

    @pytest.mark.asyncio
    async def test_update_session_partial(self, practice_service, mock_db):
        """Test partial practice session update."""
        session_id = uuid4()
        mock_session = MagicMock(spec=PracticeSession)
        mock_session.id = str(session_id)
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_session
        mock_db.execute.return_value = mock_result
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()
        
        partial_update = MockPracticeSessionUpdate(current_turn=5)
        
        result = await practice_service.update_session(
            session_id,
            partial_update
        )
        
        assert result == mock_session


class TestPracticeServiceEdgeCases:
    """Edge case tests for PracticeService."""

    @pytest.fixture
    def mock_db(self):
        """Create mock database session."""
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def practice_service(self, mock_db):
        """Create practice service instance."""
        return PracticeService(mock_db)

    @pytest.mark.asyncio
    async def test_get_session_with_invalid_uuid_format(self, practice_service, mock_db):
        """Test getting session with invalid UUID format."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result
        
        result = await practice_service.get_session("invalid-uuid")
        
        assert result is None

    @pytest.mark.asyncio
    async def test_create_session_with_valid_uuid(self, practice_service, mock_db):
        """Test creating session with valid UUID."""
        user_id = uuid4()
        dialogue_id = uuid4()
        
        session_create = StartSessionRequest(
            dialogue_id=dialogue_id,
        )
        
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()
        
        result = await practice_service.create_session(user_id, session_create)
        
        assert isinstance(result, PracticeSession)

    @pytest.mark.asyncio
    async def test_update_session_status_transitions(self, practice_service, mock_db):
        """Test updating session status through transitions."""
        session_id = uuid4()
        
        for status in [SessionStatus.ACTIVE, SessionStatus.COMPLETED, SessionStatus.ABANDONED]:
            mock_session = MagicMock(spec=PracticeSession)
            mock_session.id = str(session_id)
            mock_session.status = status
            
            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = mock_session
            mock_db.execute.return_value = mock_result
            mock_db.commit = AsyncMock()
            mock_db.refresh = AsyncMock()
            
            update_data = MockPracticeSessionUpdate(status=status)
            result = await practice_service.update_session(session_id, update_data)
            
            assert result == mock_session

    @pytest.mark.asyncio
    async def test_update_session_multiple_fields(self, practice_service, mock_db):
        """Test updating multiple fields at once."""
        session_id = uuid4()
        mock_session = MagicMock(spec=PracticeSession)
        mock_session.id = str(session_id)
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_session
        mock_db.execute.return_value = mock_result
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()
        
        update_data = MockPracticeSessionUpdate(
            status=SessionStatus.COMPLETED,
            current_turn=10,
        )
        
        result = await practice_service.update_session(session_id, update_data)
        
        assert result == mock_session
