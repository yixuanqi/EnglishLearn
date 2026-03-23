"""Integration tests for user endpoints."""

import pytest
from httpx import AsyncClient


class TestUserEndpoints:
    """Tests for user endpoints."""

    @pytest.mark.asyncio
    async def test_get_profile_success(self, client: AsyncClient, auth_headers: dict):
        """Test getting user profile successfully."""
        response = await client.get(
            "/api/v1/users/profile",
            headers=auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "email" in data
        assert "name" in data

    @pytest.mark.asyncio
    async def test_get_profile_unauthorized(self, client: AsyncClient):
        """Test getting profile without authentication."""
        response = await client.get("/api/v1/users/profile")
        
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_update_profile_name(self, client: AsyncClient, auth_headers: dict):
        """Test updating user profile name."""
        response = await client.put(
            "/api/v1/users/profile",
            json={"name": "Updated Name"},
            headers=auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"

    @pytest.mark.asyncio
    async def test_update_profile_avatar(self, client: AsyncClient, auth_headers: dict):
        """Test updating user profile avatar."""
        response = await client.put(
            "/api/v1/users/profile",
            json={"avatar_url": "https://example.com/avatar.png"},
            headers=auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["avatar_url"] == "https://example.com/avatar.png"

    @pytest.mark.asyncio
    async def test_update_profile_english_level(self, client: AsyncClient, auth_headers: dict):
        """Test updating user English level."""
        response = await client.put(
            "/api/v1/users/profile",
            json={"english_level": "advanced"},
            headers=auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["english_level"] == "advanced"

    @pytest.mark.asyncio
    async def test_update_profile_multiple_fields(self, client: AsyncClient, auth_headers: dict):
        """Test updating multiple profile fields."""
        response = await client.put(
            "/api/v1/users/profile",
            json={
                "name": "New Name",
                "english_level": "beginner",
            },
            headers=auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "New Name"
        assert data["english_level"] == "beginner"

    @pytest.mark.asyncio
    async def test_update_profile_unauthorized(self, client: AsyncClient):
        """Test updating profile without authentication."""
        response = await client.put(
            "/api/v1/users/profile",
            json={"name": "New Name"},
        )
        
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_update_profile_invalid_english_level(self, client: AsyncClient, auth_headers: dict):
        """Test updating profile with invalid English level."""
        response = await client.put(
            "/api/v1/users/profile",
            json={"english_level": "invalid_level"},
            headers=auth_headers,
        )
        
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_update_profile_empty_name(self, client: AsyncClient, auth_headers: dict):
        """Test updating profile with empty name."""
        response = await client.put(
            "/api/v1/users/profile",
            json={"name": ""},
            headers=auth_headers,
        )
        
        assert response.status_code == 422


class TestUserEndpointsEdgeCases:
    """Edge case tests for user endpoints."""

    @pytest.mark.asyncio
    async def test_update_profile_name_max_length(self, client: AsyncClient, auth_headers: dict):
        """Test updating profile with max length name."""
        max_name = "x" * 100
        response = await client.put(
            "/api/v1/users/profile",
            json={"name": max_name},
            headers=auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["name"]) == 100

    @pytest.mark.asyncio
    async def test_update_profile_name_too_long(self, client: AsyncClient, auth_headers: dict):
        """Test updating profile with name too long."""
        long_name = "x" * 101
        response = await client.put(
            "/api/v1/users/profile",
            json={"name": long_name},
            headers=auth_headers,
        )
        
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_get_profile_after_multiple_updates(self, client: AsyncClient, auth_headers: dict):
        """Test getting profile after multiple updates."""
        await client.put(
            "/api/v1/users/profile",
            json={"name": "First Update"},
            headers=auth_headers,
        )
        await client.put(
            "/api/v1/users/profile",
            json={"english_level": "advanced"},
            headers=auth_headers,
        )
        
        response = await client.get(
            "/api/v1/users/profile",
            headers=auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "First Update"
        assert data["english_level"] == "advanced"

    @pytest.mark.asyncio
    async def test_update_profile_with_interests(self, client: AsyncClient, auth_headers: dict):
        """Test updating profile with interests."""
        response = await client.put(
            "/api/v1/users/profile",
            json={"interests": ["business", "technology", "travel"]},
            headers=auth_headers,
        )
        
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_update_profile_empty_update(self, client: AsyncClient, auth_headers: dict):
        """Test updating profile with empty update."""
        response = await client.put(
            "/api/v1/users/profile",
            json={},
            headers=auth_headers,
        )
        
        assert response.status_code == 200
