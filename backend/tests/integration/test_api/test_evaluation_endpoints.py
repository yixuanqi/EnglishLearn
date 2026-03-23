import pytest
from httpx import AsyncClient
from uuid import uuid4


class TestEvaluationEndpoints:
    @pytest.mark.asyncio
    async def test_evaluate_speech_success(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        response = await client.post(
            "/v1/evaluation/evaluate",
            json={
                "audio_data": "base64_encoded_audio_data",
                "reference_text": "Hello, how are you?",
                "language": "en-US"
            },
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "overall_score" in data
        assert "pronunciation_score" in data
        assert "fluency_score" in data

    @pytest.mark.asyncio
    async def test_evaluate_speech_unauthorized(
        self,
        client: AsyncClient
    ):
        response = await client.post(
            "/v1/evaluation/evaluate",
            json={
                "audio_data": "base64_encoded_audio_data",
                "reference_text": "Hello, how are you?",
                "language": "en-US"
            }
        )
        
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_evaluate_speech_invalid_audio(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        response = await client.post(
            "/v1/evaluation/evaluate",
            json={
                "audio_data": "",
                "reference_text": "Hello, how are you?",
                "language": "en-US"
            },
            headers=auth_headers
        )
        
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_get_evaluation_detail(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        response = await client.post(
            "/v1/evaluation/evaluate",
            json={
                "audio_data": "base64_encoded_audio_data",
                "reference_text": "Hello, how are you?",
                "language": "en-US"
            },
            headers=auth_headers
        )
        evaluation_id = response.json()["id"]
        
        response = await client.get(
            f"/v1/evaluation/{evaluation_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == evaluation_id

    @pytest.mark.asyncio
    async def test_get_evaluation_not_found(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        response = await client.get(
            f"/v1/evaluation/{uuid4()}",
            headers=auth_headers
        )
        
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_list_evaluations(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        response = await client.get(
            "/v1/evaluation/history",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data

    @pytest.mark.asyncio
    async def test_list_evaluations_with_filters(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        response = await client.get(
            "/v1/evaluation/history?min_score=80",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data

    @pytest.mark.asyncio
    async def test_get_word_level_analysis(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        response = await client.post(
            "/v1/evaluation/evaluate",
            json={
                "audio_data": "base64_encoded_audio_data",
                "reference_text": "Hello, how are you?",
                "language": "en-US",
                "include_word_analysis": True
            },
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "word_details" in data
        assert isinstance(data["word_details"], list)

    @pytest.mark.asyncio
    async def test_get_phoneme_level_analysis(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        response = await client.post(
            "/v1/evaluation/evaluate",
            json={
                "audio_data": "base64_encoded_audio_data",
                "reference_text": "Hello",
                "language": "en-US",
                "include_phoneme_analysis": True
            },
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "phoneme_details" in data
        assert isinstance(data["phoneme_details"], list)

    @pytest.mark.asyncio
    async def test_get_feedback_suggestions(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        response = await client.post(
            "/v1/evaluation/evaluate",
            json={
                "audio_data": "base64_encoded_audio_data",
                "reference_text": "Hello, how are you?",
                "language": "en-US",
                "include_feedback": True
            },
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "feedback" in data
        assert "suggestions" in data["feedback"]

    @pytest.mark.asyncio
    async def test_batch_evaluate(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        response = await client.post(
            "/v1/evaluation/batch",
            json={
                "evaluations": [
                    {
                        "audio_data": "base64_audio_1",
                        "reference_text": "Hello",
                        "language": "en-US"
                    },
                    {
                        "audio_data": "base64_audio_2",
                        "reference_text": "How are you?",
                        "language": "en-US"
                    }
                ]
            },
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert len(data["results"]) == 2

    @pytest.mark.asyncio
    async def test_batch_evaluate_unauthorized(
        self,
        client: AsyncClient
    ):
        response = await client.post(
            "/v1/evaluation/batch",
            json={
                "evaluations": [
                    {
                        "audio_data": "base64_audio",
                        "reference_text": "Hello",
                        "language": "en-US"
                    }
                ]
            }
        )
        
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_evaluation_statistics(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        response = await client.get(
            "/v1/evaluation/statistics",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "total_evaluations" in data
        assert "average_score" in data
        assert "score_distribution" in data
