import pytest
from httpx import AsyncClient


class TestAuthEndpoints:
    @pytest.mark.asyncio
    async def test_register_success(self, client: AsyncClient):
        response = await client.post(
            "/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "TestPass123!",
                "name": "New User"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["user"]["email"] == "newuser@example.com"

    @pytest.mark.asyncio
    async def test_register_invalid_email(self, client: AsyncClient):
        response = await client.post(
            "/v1/auth/register",
            json={
                "email": "invalid-email",
                "password": "TestPass123!",
                "name": "Test User"
            }
        )
        
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_register_weak_password(self, client: AsyncClient):
        response = await client.post(
            "/v1/auth/register",
            json={
                "email": "test@example.com",
                "password": "weak",
                "name": "Test User"
            }
        )
        
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_register_duplicate_email(
        self,
        client: AsyncClient,
        mock_user: dict
    ):
        await client.post("/v1/auth/register", json=mock_user)
        
        response = await client.post("/v1/auth/register", json=mock_user)
        
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_login_success(self, client: AsyncClient, mock_user: dict):
        await client.post("/v1/auth/register", json=mock_user)
        
        response = await client.post(
            "/v1/auth/login",
            json={
                "email": mock_user["email"],
                "password": mock_user["password"]
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["user"]["email"] == mock_user["email"]

    @pytest.mark.asyncio
    async def test_login_invalid_password(
        self,
        client: AsyncClient,
        mock_user: dict
    ):
        await client.post("/v1/auth/register", json=mock_user)
        
        response = await client.post(
            "/v1/auth/login",
            json={
                "email": mock_user["email"],
                "password": "WrongPassword123!"
            }
        )
        
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_login_user_not_found(self, client: AsyncClient):
        response = await client.post(
            "/v1/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "TestPass123!"
            }
        )
        
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_current_user(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        response = await client.get(
            "/v1/auth/me",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "email" in data
        assert "name" in data

    @pytest.mark.asyncio
    async def test_protected_endpoint_without_token(self, client: AsyncClient):
        response = await client.get("/v1/auth/me")
        
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_protected_endpoint_invalid_token(
        self,
        client: AsyncClient
    ):
        response = await client.get(
            "/v1/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_refresh_token_success(
        self,
        client: AsyncClient,
        mock_user: dict
    ):
        register_response = await client.post(
            "/v1/auth/register",
            json=mock_user
        )
        refresh_token = register_response.json()["refresh_token"]
        
        response = await client.post(
            "/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    @pytest.mark.asyncio
    async def test_refresh_token_invalid(self, client: AsyncClient):
        response = await client.post(
            "/v1/auth/refresh",
            json={"refresh_token": "invalid_token"}
        )
        
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_logout_success(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        response = await client.post(
            "/v1/auth/logout",
            headers=auth_headers
        )
        
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_logout_without_token(self, client: AsyncClient):
        response = await client.post("/v1/auth/logout")
        
        assert response.status_code == 401
