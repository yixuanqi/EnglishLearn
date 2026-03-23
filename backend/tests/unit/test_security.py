"""Unit tests for security module."""

import pytest
from datetime import datetime, timedelta, timezone

from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_token,
)


class TestPasswordHashing:
    """Tests for password hashing functions."""

    def test_get_password_hash_returns_string(self):
        """Test that password hash returns a string."""
        password = "TestPassword123!"
        hashed = get_password_hash(password)
        assert isinstance(hashed, str)
        assert len(hashed) > 0

    def test_get_password_hash_different_passwords(self):
        """Test that different passwords produce different hashes."""
        hash1 = get_password_hash("password1")
        hash2 = get_password_hash("password2")
        assert hash1 != hash2

    def test_get_password_hash_same_password_different_hashes(self):
        """Test that same password produces different hashes (bcrypt salt)."""
        password = "TestPassword123!"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        assert hash1 != hash2

    def test_verify_password_correct(self):
        """Test password verification with correct password."""
        password = "TestPassword123!"
        hashed = get_password_hash(password)
        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password."""
        password = "TestPassword123!"
        hashed = get_password_hash(password)
        assert verify_password("WrongPassword", hashed) is False

    def test_verify_password_empty(self):
        """Test password verification with empty password."""
        password = "TestPassword123!"
        hashed = get_password_hash(password)
        assert verify_password("", hashed) is False

    def test_verify_password_case_sensitive(self):
        """Test that password verification is case sensitive."""
        password = "TestPassword123!"
        hashed = get_password_hash(password)
        assert verify_password("testpassword123!", hashed) is False


class TestAccessToken:
    """Tests for access token functions."""

    def test_create_access_token_returns_string(self):
        """Test that access token creation returns a string."""
        token = create_access_token(
            subject="user-123",
            email="test@example.com",
        )
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_access_token_with_custom_expiry(self):
        """Test access token creation with custom expiry."""
        expires = timedelta(hours=2)
        token = create_access_token(
            subject="user-123",
            email="test@example.com",
            expires_delta=expires,
        )
        payload = decode_token(token)
        assert payload is not None
        exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        expected_exp = datetime.now(timezone.utc) + expires
        delta = abs((exp - expected_exp).total_seconds())
        assert delta < 5

    def test_create_access_token_contains_subject(self):
        """Test that access token contains subject."""
        token = create_access_token(
            subject="user-123",
            email="test@example.com",
        )
        payload = decode_token(token)
        assert payload is not None
        assert payload["sub"] == "user-123"

    def test_create_access_token_contains_email(self):
        """Test that access token contains email."""
        token = create_access_token(
            subject="user-123",
            email="test@example.com",
        )
        payload = decode_token(token)
        assert payload is not None
        assert payload["email"] == "test@example.com"

    def test_create_access_token_contains_subscription(self):
        """Test that access token contains subscription."""
        token = create_access_token(
            subject="user-123",
            email="test@example.com",
            subscription="premium_monthly",
        )
        payload = decode_token(token)
        assert payload is not None
        assert payload["subscription"] == "premium_monthly"

    def test_create_access_token_contains_role(self):
        """Test that access token contains role."""
        token = create_access_token(
            subject="user-123",
            email="test@example.com",
        )
        payload = decode_token(token)
        assert payload is not None
        assert payload["role"] == "user"

    def test_create_access_token_has_jti(self):
        """Test that access token has unique identifier."""
        token = create_access_token(
            subject="user-123",
            email="test@example.com",
        )
        payload = decode_token(token)
        assert payload is not None
        assert "jti" in payload

    def test_create_access_token_unique_jti(self):
        """Test that each access token has unique jti."""
        token1 = create_access_token(
            subject="user-123",
            email="test@example.com",
        )
        token2 = create_access_token(
            subject="user-123",
            email="test@example.com",
        )
        payload1 = decode_token(token1)
        payload2 = decode_token(token2)
        assert payload1["jti"] != payload2["jti"]


class TestRefreshToken:
    """Tests for refresh token functions."""

    def test_create_refresh_token_returns_string(self):
        """Test that refresh token creation returns a string."""
        token = create_refresh_token(subject="user-123")
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_refresh_token_contains_subject(self):
        """Test that refresh token contains subject."""
        token = create_refresh_token(subject="user-123")
        payload = decode_token(token)
        assert payload is not None
        assert payload["sub"] == "user-123"

    def test_create_refresh_token_contains_type(self):
        """Test that refresh token contains type."""
        token = create_refresh_token(subject="user-123")
        payload = decode_token(token)
        assert payload is not None
        assert payload["type"] == "refresh"

    def test_create_refresh_token_with_custom_expiry(self):
        """Test refresh token creation with custom expiry."""
        expires = timedelta(days=14)
        token = create_refresh_token(
            subject="user-123",
            expires_delta=expires,
        )
        payload = decode_token(token)
        assert payload is not None
        exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        expected_exp = datetime.now(timezone.utc) + expires
        delta = abs((exp - expected_exp).total_seconds())
        assert delta < 5

    def test_create_refresh_token_has_jti(self):
        """Test that refresh token has unique identifier."""
        token = create_refresh_token(subject="user-123")
        payload = decode_token(token)
        assert payload is not None
        assert "jti" in payload


class TestDecodeToken:
    """Tests for token decoding."""

    def test_decode_valid_access_token(self):
        """Test decoding valid access token."""
        token = create_access_token(
            subject="user-123",
            email="test@example.com",
        )
        payload = decode_token(token)
        assert payload is not None
        assert payload["sub"] == "user-123"

    def test_decode_valid_refresh_token(self):
        """Test decoding valid refresh token."""
        token = create_refresh_token(subject="user-123")
        payload = decode_token(token)
        assert payload is not None
        assert payload["sub"] == "user-123"

    def test_decode_invalid_token(self):
        """Test decoding invalid token returns None."""
        payload = decode_token("invalid_token")
        assert payload is None

    def test_decode_empty_token(self):
        """Test decoding empty token returns None."""
        payload = decode_token("")
        assert payload is None

    def test_decode_malformed_token(self):
        """Test decoding malformed token returns None."""
        payload = decode_token("a.b.c")
        assert payload is None


class TestHashToken:
    """Tests for token hashing."""

    def test_hash_token_returns_string(self):
        """Test that token hash returns a string."""
        hashed = hash_token("some_token_value")
        assert isinstance(hashed, str)

    def test_hash_token_consistent(self):
        """Test that same token produces same hash."""
        token = "some_token_value"
        hash1 = hash_token(token)
        hash2 = hash_token(token)
        assert hash1 == hash2

    def test_hash_token_different_tokens(self):
        """Test that different tokens produce different hashes."""
        hash1 = hash_token("token1")
        hash2 = hash_token("token2")
        assert hash1 != hash2

    def test_hash_token_length(self):
        """Test that hash has expected length (SHA-256 = 64 hex chars)."""
        hashed = hash_token("some_token_value")
        assert len(hashed) == 64

    def test_hash_token_empty(self):
        """Test hashing empty token."""
        hashed = hash_token("")
        assert isinstance(hashed, str)
        assert len(hashed) == 64
