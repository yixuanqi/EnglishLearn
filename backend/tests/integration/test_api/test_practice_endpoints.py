import pytest
from httpx import AsyncClient
from uuid import uuid4


class TestPracticeEndpoints:
    @pytest.mark.asyncio
    async def test_start_practice_session_success(
        self,
        client: AsyncClient,
        auth_headers: dict,
        mock_scenario: dict
    ):
        scenario_response = await client.post(
            "/v1/scenarios",
            json=mock_scenario,
            headers=auth_headers
        )
        scenario_id = scenario_response.json()["id"]
        
        response = await client.post(
            "/v1/practice/start",
            json={"scenario_id": scenario_id},
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert "session_id" in data
        assert data["scenario_id"] == scenario_id

    @pytest.mark.asyncio
    async def test_start_practice_session_unauthorized(
        self,
        client: AsyncClient,
        mock_scenario: dict
    ):
        response = await client.post(
            "/v1/practice/start",
            json={"scenario_id": str(uuid4())}
        )
        
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_start_practice_session_invalid_scenario(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        response = await client.post(
            "/v1/practice/start",
            json={"scenario_id": str(uuid4())},
            headers=auth_headers
        )
        
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_submit_practice_success(
        self,
        client: AsyncClient,
        auth_headers: dict,
        mock_scenario: dict
    ):
        scenario_response = await client.post(
            "/v1/scenarios",
            json=mock_scenario,
            headers=auth_headers
        )
        scenario_id = scenario_response.json()["id"]
        
        session_response = await client.post(
            "/v1/practice/start",
            json={"scenario_id": scenario_id},
            headers=auth_headers
        )
        session_id = session_response.json()["session_id"]
        
        response = await client.post(
            "/v1/practice/submit",
            json={
                "session_id": session_id,
                "recordings": [
                    {
                        "dialogue_line_id": 1,
                        "audio_data": "base64_encoded_audio_data",
                        "duration": 5.2
                    }
                ]
            },
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "evaluation" in data

    @pytest.mark.asyncio
    async def test_submit_practice_unauthorized(
        self,
        client: AsyncClient
    ):
        response = await client.post(
            "/v1/practice/submit",
            json={
                "session_id": str(uuid4()),
                "recordings": []
            }
        )
        
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_submit_practice_invalid_session(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        response = await client.post(
            "/v1/practice/submit",
            json={
                "session_id": str(uuid4()),
                "recordings": []
            },
            headers=auth_headers
        )
        
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_practice_session(
        self,
        client: AsyncClient,
        auth_headers: dict,
        mock_scenario: dict
    ):
        scenario_response = await client.post(
            "/v1/scenarios",
            json=mock_scenario,
            headers=auth_headers
        )
        scenario_id = scenario_response.json()["id"]
        
        session_response = await client.post(
            "/v1/practice/start",
            json={"scenario_id": scenario_id},
            headers=auth_headers
        )
        session_id = session_response.json()["session_id"]
        
        response = await client.get(
            f"/v1/practice/sessions/{session_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == session_id

    @pytest.mark.asyncio
    async def test_get_practice_session_not_found(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        response = await client.get(
            f"/v1/practice/sessions/{uuid4()}",
            headers=auth_headers
        )
        
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_list_practice_sessions(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        response = await client.get(
            "/v1/practice/sessions",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data

    @pytest.mark.asyncio
    async def test_list_practice_sessions_with_filters(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        response = await client.get(
            "/v1/practice/sessions?status=completed",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data

    @pytest.mark.asyncio
    async def test_cancel_practice_session(
        self,
        client: AsyncClient,
        auth_headers: dict,
        mock_scenario: dict
    ):
        scenario_response = await client.post(
            "/v1/scenarios",
            json=mock_scenario,
            headers=auth_headers
        )
        scenario_id = scenario_response.json()["id"]
        
        session_response = await client.post(
            "/v1/practice/start",
            json={"scenario_id": scenario_id},
            headers=auth_headers
        )
        session_id = session_response.json()["session_id"]
        
        response = await client.post(
            f"/v1/practice/sessions/{session_id}/cancel",
            headers=auth_headers
        )
        
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_cancel_practice_session_not_found(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        response = await client.post(
            f"/v1/practice/sessions/{uuid4()}/cancel",
            headers=auth_headers
        )
        
        assert response.status_code == 404
