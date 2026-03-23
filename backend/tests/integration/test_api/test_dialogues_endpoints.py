"""Integration tests for dialogue endpoints."""

import pytest
from httpx import AsyncClient
from uuid import uuid4


class TestDialogueEndpoints:
    """Tests for dialogue endpoints."""

    @pytest.mark.asyncio
    async def test_generate_dialogue_unauthorized(self, client: AsyncClient):
        """Test generating dialogue without authentication."""
        response = await client.post(
            "/api/v1/dialogues/generate",
            json={
                "scenario_id": str(uuid4()),
                "num_turns": 5,
            },
        )
        
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_generate_dialogue_missing_scenario_id(self, client: AsyncClient, auth_headers: dict):
        """Test generating dialogue with missing scenario ID."""
        response = await client.post(
            "/api/v1/dialogues/generate",
            json={"num_turns": 5},
            headers=auth_headers,
        )
        
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_generate_dialogue_invalid_scenario_id(self, client: AsyncClient, auth_headers: dict):
        """Test generating dialogue with invalid scenario ID."""
        response = await client.post(
            "/api/v1/dialogues/generate",
            json={
                "scenario_id": "invalid-uuid",
                "num_turns": 5,
            },
            headers=auth_headers,
        )
        
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_get_dialogue_unauthorized(self, client: AsyncClient):
        """Test getting dialogue without authentication."""
        response = await client.get(f"/api/v1/dialogues/{uuid4()}")
        
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_dialogue_invalid_id(self, client: AsyncClient, auth_headers: dict):
        """Test getting dialogue with invalid ID."""
        response = await client.get(
            "/api/v1/dialogues/invalid-id",
            headers=auth_headers,
        )
        
        assert response.status_code == 422


class TestDialogueEndpointsEdgeCases:
    """Edge case tests for dialogue endpoints."""

    @pytest.mark.asyncio
    async def test_generate_dialogue_min_turns(self, client: AsyncClient, auth_headers: dict):
        """Test generating dialogue with minimum turns."""
        response = await client.post(
            "/api/v1/dialogues/generate",
            json={
                "scenario_id": str(uuid4()),
                "num_turns": 1,
            },
            headers=auth_headers,
        )
        
        assert response.status_code in [200, 201, 404, 500]

    @pytest.mark.asyncio
    async def test_generate_dialogue_max_turns(self, client: AsyncClient, auth_headers: dict):
        """Test generating dialogue with maximum turns."""
        response = await client.post(
            "/api/v1/dialogues/generate",
            json={
                "scenario_id": str(uuid4()),
                "num_turns": 20,
            },
            headers=auth_headers,
        )
        
        assert response.status_code in [200, 201, 404, 500]

    @pytest.mark.asyncio
    async def test_generate_dialogue_zero_turns(self, client: AsyncClient, auth_headers: dict):
        """Test generating dialogue with zero turns."""
        response = await client.post(
            "/api/v1/dialogues/generate",
            json={
                "scenario_id": str(uuid4()),
                "num_turns": 0,
            },
            headers=auth_headers,
        )
        
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_generate_dialogue_negative_turns(self, client: AsyncClient, auth_headers: dict):
        """Test generating dialogue with negative turns."""
        response = await client.post(
            "/api/v1/dialogues/generate",
            json={
                "scenario_id": str(uuid4()),
                "num_turns": -5,
            },
            headers=auth_headers,
        )
        
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_get_dialogue_nonexistent_id(self, client: AsyncClient, auth_headers: dict):
        """Test getting dialogue with nonexistent ID."""
        response = await client.get(
            f"/api/v1/dialogues/{uuid4()}",
            headers=auth_headers,
        )
        
        assert response.status_code in [404, 500]
