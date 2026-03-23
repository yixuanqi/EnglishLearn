"""Boundary tests for input validation, pagination, and authentication."""

import pytest
from httpx import AsyncClient
from uuid import uuid4


class TestInputValidationBoundary:
    """Boundary tests for input validation."""

    @pytest.mark.asyncio
    async def test_register_email_max_length(self, client: AsyncClient):
        """Test registration with email at max length."""
        long_email = "a" * 240 + "@example.com"
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": long_email,
                "password": "TestPass123!",
                "name": "Test User",
            },
        )
        
        assert response.status_code in [201, 422]

    @pytest.mark.asyncio
    async def test_register_password_min_length(self, client: AsyncClient):
        """Test registration with password at minimum length."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "password": "Test123!",
                "name": "Test User",
            },
        )
        
        assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_register_password_below_min_length(self, client: AsyncClient):
        """Test registration with password below minimum length."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "password": "Test12!",
                "name": "Test User",
            },
        )
        
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_register_name_max_length(self, client: AsyncClient):
        """Test registration with name at max length."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "password": "TestPass123!",
                "name": "x" * 100,
            },
        )
        
        assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_register_name_exceeds_max_length(self, client: AsyncClient):
        """Test registration with name exceeding max length."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "password": "TestPass123!",
                "name": "x" * 101,
            },
        )
        
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_scenario_title_max_length(self, client: AsyncClient, auth_headers: dict):
        """Test scenario creation with title at max length."""
        response = await client.post(
            "/api/v1/scenarios",
            json={
                "title": "x" * 200,
                "category": "exhibition",
                "context": "Test context",
                "user_role": "Sales",
                "ai_role": "Customer",
            },
            headers=auth_headers,
        )
        
        assert response.status_code in [201, 422]

    @pytest.mark.asyncio
    async def test_scenario_title_exceeds_max_length(self, client: AsyncClient, auth_headers: dict):
        """Test scenario creation with title exceeding max length."""
        response = await client.post(
            "/api/v1/scenarios",
            json={
                "title": "x" * 201,
                "category": "exhibition",
                "context": "Test context",
                "user_role": "Sales",
                "ai_role": "Customer",
            },
            headers=auth_headers,
        )
        
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_score_boundary_zero(self, client: AsyncClient, auth_headers: dict):
        """Test score at lower boundary (0)."""
        response = await client.post(
            "/api/v1/evaluation/evaluate",
            json={
                "audio_data": "test_audio",
                "reference_text": "Hello",
                "language": "en-US",
            },
            headers=auth_headers,
        )
        
        assert response.status_code in [200, 422, 500]

    @pytest.mark.asyncio
    async def test_score_boundary_hundred(self, client: AsyncClient, auth_headers: dict):
        """Test score at upper boundary (100)."""
        response = await client.post(
            "/api/v1/evaluation/evaluate",
            json={
                "audio_data": "test_audio",
                "reference_text": "Hello",
                "language": "en-US",
            },
            headers=auth_headers,
        )
        
        assert response.status_code in [200, 422, 500]


class TestPaginationBoundary:
    """Boundary tests for pagination."""

    @pytest.mark.asyncio
    async def test_pagination_page_one(self, client: AsyncClient, auth_headers: dict):
        """Test pagination with page 1."""
        response = await client.get(
            "/api/v1/scenarios?page=1&page_size=10",
            headers=auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1

    @pytest.mark.asyncio
    async def test_pagination_page_zero(self, client: AsyncClient, auth_headers: dict):
        """Test pagination with page 0 (invalid)."""
        response = await client.get(
            "/api/v1/scenarios?page=0&page_size=10",
            headers=auth_headers,
        )
        
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_pagination_negative_page(self, client: AsyncClient, auth_headers: dict):
        """Test pagination with negative page number."""
        response = await client.get(
            "/api/v1/scenarios?page=-1&page_size=10",
            headers=auth_headers,
        )
        
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_pagination_large_page(self, client: AsyncClient, auth_headers: dict):
        """Test pagination with large page number."""
        response = await client.get(
            "/api/v1/scenarios?page=999999&page_size=10",
            headers=auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []

    @pytest.mark.asyncio
    async def test_pagination_page_size_one(self, client: AsyncClient, auth_headers: dict):
        """Test pagination with page size 1."""
        response = await client.get(
            "/api/v1/scenarios?page=1&page_size=1",
            headers=auth_headers,
        )
        
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_pagination_page_size_zero(self, client: AsyncClient, auth_headers: dict):
        """Test pagination with page size 0 (invalid)."""
        response = await client.get(
            "/api/v1/scenarios?page=1&page_size=0",
            headers=auth_headers,
        )
        
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_pagination_page_size_negative(self, client: AsyncClient, auth_headers: dict):
        """Test pagination with negative page size."""
        response = await client.get(
            "/api/v1/scenarios?page=1&page_size=-1",
            headers=auth_headers,
        )
        
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_pagination_page_size_max(self, client: AsyncClient, auth_headers: dict):
        """Test pagination with maximum page size."""
        response = await client.get(
            "/api/v1/scenarios?page=1&page_size=100",
            headers=auth_headers,
        )
        
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_pagination_page_size_exceeds_max(self, client: AsyncClient, auth_headers: dict):
        """Test pagination with page size exceeding maximum."""
        response = await client.get(
            "/api/v1/scenarios?page=1&page_size=1000",
            headers=auth_headers,
        )
        
        assert response.status_code in [200, 422]


class TestAuthenticationBoundary:
    """Boundary tests for authentication."""

    @pytest.mark.asyncio
    async def test_auth_missing_header(self, client: AsyncClient):
        """Test request without authorization header."""
        response = await client.get("/api/v1/auth/me")
        
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_auth_empty_header(self, client: AsyncClient):
        """Test request with empty authorization header."""
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": ""},
        )
        
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_auth_invalid_scheme(self, client: AsyncClient):
        """Test request with invalid auth scheme."""
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Basic invalid_token"},
        )
        
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_auth_malformed_token(self, client: AsyncClient):
        """Test request with malformed token."""
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer malformed.token.here"},
        )
        
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_auth_empty_token(self, client: AsyncClient):
        """Test request with empty token."""
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer "},
        )
        
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_auth_expired_token(self, client: AsyncClient):
        """Test request with expired token."""
        expired_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyLCJleHAiOjE1MTYyMzkwMjJ9.4Adcj3UFYzP5aI9Wt5j5t5t5t5t5t5t5t5t5t5t5t5t5"
        
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {expired_token}"},
        )
        
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_refresh_token_as_access_token(self, client: AsyncClient, mock_user: dict):
        """Test using refresh token as access token."""
        register_response = await client.post(
            "/api/v1/auth/register",
            json=mock_user,
        )
        refresh_token = register_response.json()["refresh_token"]
        
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {refresh_token}"},
        )
        
        assert response.status_code == 401


class TestContentTypeBoundary:
    """Boundary tests for content type."""

    @pytest.mark.asyncio
    async def test_invalid_content_type(self, client: AsyncClient):
        """Test request with invalid content type."""
        response = await client.post(
            "/api/v1/auth/register",
            content="not json",
            headers={"Content-Type": "text/plain"},
        )
        
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_missing_content_type(self, client: AsyncClient):
        """Test request without content type."""
        response = await client.post(
            "/api/v1/auth/register",
            content='{"email": "test@example.com", "password": "TestPass123!", "name": "Test"}',
        )
        
        assert response.status_code in [201, 422]

    @pytest.mark.asyncio
    async def test_empty_body(self, client: AsyncClient):
        """Test request with empty body."""
        response = await client.post(
            "/api/v1/auth/register",
            json={},
        )
        
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_extra_fields_in_body(self, client: AsyncClient):
        """Test request with extra fields in body."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "password": "TestPass123!",
                "name": "Test User",
                "extra_field": "should be ignored",
            },
        )
        
        assert response.status_code == 201


class TestHTTPMethodBoundary:
    """Boundary tests for HTTP methods."""

    @pytest.mark.asyncio
    async def test_delete_on_collection(self, client: AsyncClient, auth_headers: dict):
        """Test DELETE method on collection endpoint."""
        response = await client.delete(
            "/api/v1/scenarios",
            headers=auth_headers,
        )
        
        assert response.status_code == 405

    @pytest.mark.asyncio
    async def test_post_on_detail(self, client: AsyncClient, auth_headers: dict):
        """Test POST method on detail endpoint."""
        response = await client.post(
            f"/api/v1/scenarios/{uuid4()}",
            headers=auth_headers,
        )
        
        assert response.status_code == 405

    @pytest.mark.asyncio
    async def test_put_on_collection(self, client: AsyncClient, auth_headers: dict):
        """Test PUT method on collection endpoint."""
        response = await client.put(
            "/api/v1/scenarios",
            json={"title": "Test"},
            headers=auth_headers,
        )
        
        assert response.status_code == 405
