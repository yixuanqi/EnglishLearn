import pytest
from httpx import AsyncClient
from uuid import uuid4


class TestScenarioEndpoints:
    @pytest.mark.asyncio
    async def test_list_scenarios(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        response = await client.get(
            "/v1/scenarios",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert isinstance(data["items"], list)

    @pytest.mark.asyncio
    async def test_list_scenarios_with_filters(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        response = await client.get(
            "/v1/scenarios?category=exhibition&difficulty=intermediate",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data

    @pytest.mark.asyncio
    async def test_list_scenarios_pagination(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        response = await client.get(
            "/v1/scenarios?page=1&page_size=10",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["page_size"] == 10

    @pytest.mark.asyncio
    async def test_create_scenario_success(
        self,
        client: AsyncClient,
        auth_headers: dict,
        mock_scenario: dict
    ):
        response = await client.post(
            "/v1/scenarios",
            json=mock_scenario,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == mock_scenario["title"]
        assert data["category"] == mock_scenario["category"]

    @pytest.mark.asyncio
    async def test_create_scenario_unauthorized(
        self,
        client: AsyncClient,
        mock_scenario: dict
    ):
        response = await client.post(
            "/v1/scenarios",
            json=mock_scenario
        )
        
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_create_scenario_invalid_data(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        response = await client.post(
            "/v1/scenarios",
            json={
                "title": "Test"
            },
            headers=auth_headers
        )
        
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_get_scenario_detail(
        self,
        client: AsyncClient,
        auth_headers: dict,
        mock_scenario: dict
    ):
        create_response = await client.post(
            "/v1/scenarios",
            json=mock_scenario,
            headers=auth_headers
        )
        scenario_id = create_response.json()["id"]
        
        response = await client.get(
            f"/v1/scenarios/{scenario_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == scenario_id
        assert data["title"] == mock_scenario["title"]

    @pytest.mark.asyncio
    async def test_get_scenario_not_found(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        response = await client.get(
            f"/v1/scenarios/{uuid4()}",
            headers=auth_headers
        )
        
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_scenario_success(
        self,
        client: AsyncClient,
        auth_headers: dict,
        mock_scenario: dict
    ):
        create_response = await client.post(
            "/v1/scenarios",
            json=mock_scenario,
            headers=auth_headers
        )
        scenario_id = create_response.json()["id"]
        
        update_data = {
            "title": "Updated Title",
            "description": "Updated description"
        }
        
        response = await client.put(
            f"/v1/scenarios/{scenario_id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == update_data["title"]
        assert data["description"] == update_data["description"]

    @pytest.mark.asyncio
    async def test_update_scenario_unauthorized(
        self,
        client: AsyncClient,
        auth_headers: dict,
        mock_scenario: dict
    ):
        create_response = await client.post(
            "/v1/scenarios",
            json=mock_scenario,
            headers=auth_headers
        )
        scenario_id = create_response.json()["id"]
        
        response = await client.put(
            f"/v1/scenarios/{scenario_id}",
            json={"title": "Updated"}
        )
        
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_delete_scenario_success(
        self,
        client: AsyncClient,
        auth_headers: dict,
        mock_scenario: dict
    ):
        create_response = await client.post(
            "/v1/scenarios",
            json=mock_scenario,
            headers=auth_headers
        )
        scenario_id = create_response.json()["id"]
        
        response = await client.delete(
            f"/v1/scenarios/{scenario_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_delete_scenario_not_found(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        response = await client.delete(
            f"/v1/scenarios/{uuid4()}",
            headers=auth_headers
        )
        
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_generate_custom_scenario(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        response = await client.post(
            "/v1/scenarios/generate",
            json={
                "industry": "Technology",
                "scenario": "Product Demo",
                "participants": 2,
                "difficulty": "advanced"
            },
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert "title" in data

    @pytest.mark.asyncio
    async def test_generate_custom_scenario_unauthorized(
        self,
        client: AsyncClient
    ):
        response = await client.post(
            "/v1/scenarios/generate",
            json={
                "industry": "Technology",
                "scenario": "Product Demo",
                "participants": 2,
                "difficulty": "advanced"
            }
        )
        
        assert response.status_code == 401
