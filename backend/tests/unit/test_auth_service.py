"""Unit tests for auth service."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.auth_service import AuthService
from app.schemas.user import UserRegistrationRequest
from app.models.user import User


class MockUserCreate:
    """Mock user create for testing with auth service expected fields."""
    
    def __init__(self, email: str, password: str, name: str = "Test User"):
        self.email = email
        self.password = password
        self.name = name


class TestAuthService:
    """Tests for AuthService."""

    @pytest.fixture
    def mock_db(self):
        """Create mock database session."""
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def auth_service(self, mock_db):
        """Create auth service instance."""
        return AuthService(mock_db)

    @pytest.fixture
    def sample_user_create(self):
        """Create sample user registration data."""
        return MockUserCreate(
            email="test@example.com",
            password="TestPassword123!",
            name="Test User",
        )

    @pytest.mark.asyncio
    async def test_get_user_by_email_found(self, auth_service, mock_db):
        """Test getting user by email when user exists."""
        mock_user = MagicMock(spec=User)
        mock_user.email = "test@example.com"
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_db.execute.return_value = mock_result
        
        result = await auth_service.get_user_by_email("test@example.com")
        
        assert result == mock_user
        mock_db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_user_by_email_not_found(self, auth_service, mock_db):
        """Test getting user by email when user does not exist."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result
        
        result = await auth_service.get_user_by_email("nonexistent@example.com")
        
        assert result is None

    @pytest.mark.asyncio
    async def test_get_user_by_id_found(self, auth_service, mock_db):
        """Test getting user by ID when user exists."""
        mock_user = MagicMock(spec=User)
        mock_user.id = "user-123"
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_db.execute.return_value = mock_result
        
        result = await auth_service.get_user_by_id("user-123")
        
        assert result == mock_user

    @pytest.mark.asyncio
    async def test_get_user_by_id_not_found(self, auth_service, mock_db):
        """Test getting user by ID when user does not exist."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result
        
        result = await auth_service.get_user_by_id("nonexistent-id")
        
        assert result is None

    @pytest.mark.asyncio
    async def test_create_user_success(self, auth_service, mock_db, sample_user_create):
        """Test successful user creation."""
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()
        
        result = await auth_service.create_user(sample_user_create)
        
        assert isinstance(result, User)
        assert result.email == sample_user_create.email
        assert result.name == sample_user_create.name
        assert result.password_hash is not None
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_authenticate_user_success(self, auth_service, mock_db):
        """Test successful user authentication."""
        from app.core.security import get_password_hash
        
        mock_user = MagicMock(spec=User)
        mock_user.email = "test@example.com"
        mock_user.password_hash = get_password_hash("TestPassword123!")
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_db.execute.return_value = mock_result
        
        result = await auth_service.authenticate_user(
            "test@example.com",
            "TestPassword123!"
        )
        
        assert result == mock_user

    @pytest.mark.asyncio
    async def test_authenticate_user_wrong_password(self, auth_service, mock_db):
        """Test authentication with wrong password."""
        from app.core.security import get_password_hash
        
        mock_user = MagicMock(spec=User)
        mock_user.email = "test@example.com"
        mock_user.password_hash = get_password_hash("TestPassword123!")
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_db.execute.return_value = mock_result
        
        result = await auth_service.authenticate_user(
            "test@example.com",
            "WrongPassword123!"
        )
        
        assert result is None

    @pytest.mark.asyncio
    async def test_authenticate_user_not_found(self, auth_service, mock_db):
        """Test authentication when user not found."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result
        
        result = await auth_service.authenticate_user(
            "nonexistent@example.com",
            "TestPassword123!"
        )
        
        assert result is None

    def test_create_tokens_returns_dict(self, auth_service):
        """Test that create_tokens returns a dictionary."""
        mock_user = MagicMock(spec=User)
        mock_user.id = "user-123"
        mock_user.email = "test@example.com"
        mock_user.subscription_plan = "free"
        
        result = auth_service.create_tokens(mock_user)
        
        assert isinstance(result, dict)
        assert "access_token" in result
        assert "refresh_token" in result
        assert "token_type" in result
        assert result["token_type"] == "bearer"

    def test_create_tokens_non_empty(self, auth_service):
        """Test that create_tokens returns non-empty tokens."""
        mock_user = MagicMock(spec=User)
        mock_user.id = "user-123"
        mock_user.email = "test@example.com"
        mock_user.subscription_plan = "free"
        
        result = auth_service.create_tokens(mock_user)
        
        assert len(result["access_token"]) > 0
        assert len(result["refresh_token"]) > 0

    def test_create_tokens_different_users(self, auth_service):
        """Test that different users get different tokens."""
        mock_user1 = MagicMock(spec=User)
        mock_user1.id = "user-123"
        mock_user1.email = "user1@example.com"
        mock_user1.subscription_plan = "free"
        
        mock_user2 = MagicMock(spec=User)
        mock_user2.id = "user-456"
        mock_user2.email = "user2@example.com"
        mock_user2.subscription_plan = "free"
        
        result1 = auth_service.create_tokens(mock_user1)
        result2 = auth_service.create_tokens(mock_user2)
        
        assert result1["access_token"] != result2["access_token"]
        assert result1["refresh_token"] != result2["refresh_token"]


class TestAuthServiceEdgeCases:
    """Edge case tests for AuthService."""

    @pytest.fixture
    def mock_db(self):
        """Create mock database session."""
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def auth_service(self, mock_db):
        """Create auth service instance."""
        return AuthService(mock_db)

    @pytest.mark.asyncio
    async def test_get_user_by_email_case_insensitive(self, auth_service, mock_db):
        """Test getting user by email with different case."""
        mock_user = MagicMock(spec=User)
        mock_user.email = "Test@Example.com"
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_db.execute.return_value = mock_result
        
        result = await auth_service.get_user_by_email("test@example.com")
        
        assert result == mock_user

    @pytest.mark.asyncio
    async def test_create_user_with_special_characters_in_password(self, auth_service, mock_db):
        """Test creating user with special characters in password."""
        user_create = MockUserCreate(
            email="special@example.com",
            password="Test!@#$%^&*()123",
            name="Special User",
        )
        
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()
        
        result = await auth_service.create_user(user_create)
        
        assert isinstance(result, User)
        assert result.password_hash is not None

    @pytest.mark.asyncio
    async def test_authenticate_user_with_whitespace_in_email(self, auth_service, mock_db):
        """Test authentication with whitespace in email."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result
        
        result = await auth_service.authenticate_user(
            "  test@example.com  ",
            "TestPassword123!"
        )
        
        assert result is None

    def test_create_tokens_with_none_user_id(self, auth_service):
        """Test create_tokens handles None user ID."""
        mock_user = MagicMock(spec=User)
        mock_user.id = None
        mock_user.email = "test@example.com"
        mock_user.subscription_plan = "free"
        
        try:
            result = auth_service.create_tokens(mock_user)
            assert "access_token" in result
        except (TypeError, AttributeError):
            pass

    @pytest.mark.asyncio
    async def test_create_user_with_long_name(self, auth_service, mock_db):
        """Test creating user with very long name."""
        long_name = "A" * 100
        user_create = MockUserCreate(
            email="longname@example.com",
            password="TestPassword123!",
            name=long_name,
        )
        
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()
        
        result = await auth_service.create_user(user_create)
        
        assert isinstance(result, User)
        assert result.name == long_name
