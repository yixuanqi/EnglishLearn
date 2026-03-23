"""Integration tests for report endpoints."""

import pytest
from httpx import AsyncClient
from uuid import uuid4
from datetime import date, timedelta


class TestReportEndpoints:
    """Tests for report endpoints."""

    @pytest.mark.asyncio
    async def test_get_practice_history_unauthorized(self, client: AsyncClient):
        """Test getting practice history without authentication."""
        response = await client.get("/api/v1/reports/history")
        
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_practice_history_success(self, client: AsyncClient, auth_headers: dict):
        """Test getting practice history successfully."""
        response = await client.get(
            "/api/v1/reports/history",
            headers=auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "limit" in data

    @pytest.mark.asyncio
    async def test_get_practice_history_pagination(self, client: AsyncClient, auth_headers: dict):
        """Test getting practice history with pagination."""
        response = await client.get(
            "/api/v1/reports/history?page=1&limit=5",
            headers=auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["limit"] == 5

    @pytest.mark.asyncio
    async def test_get_practice_history_with_date_filter(self, client: AsyncClient, auth_headers: dict):
        """Test getting practice history with date filter."""
        today = date.today()
        start_date = (today - timedelta(days=7)).isoformat()
        end_date = today.isoformat()
        
        response = await client.get(
            f"/api/v1/reports/history?start_date={start_date}&end_date={end_date}",
            headers=auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data

    @pytest.mark.asyncio
    async def test_get_practice_report_unauthorized(self, client: AsyncClient):
        """Test getting practice report without authentication."""
        response = await client.get(f"/api/v1/reports/{uuid4()}")
        
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_practice_report_not_found(self, client: AsyncClient, auth_headers: dict):
        """Test getting practice report that does not exist."""
        response = await client.get(
            f"/api/v1/reports/{uuid4()}",
            headers=auth_headers,
        )
        
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_practice_report_invalid_id(self, client: AsyncClient, auth_headers: dict):
        """Test getting practice report with invalid ID."""
        response = await client.get(
            "/api/v1/reports/invalid-id",
            headers=auth_headers,
        )
        
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_get_weekly_report_unauthorized(self, client: AsyncClient):
        """Test getting weekly report without authentication."""
        response = await client.get("/api/v1/reports/weekly")
        
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_weekly_report_success(self, client: AsyncClient, auth_headers: dict):
        """Test getting weekly report successfully."""
        response = await client.get(
            "/api/v1/reports/weekly",
            headers=auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "week_start" in data
        assert "week_end" in data
        assert "total_sessions" in data
        assert "total_duration_minutes" in data
        assert "average_score" in data

    @pytest.mark.asyncio
    async def test_get_weekly_report_with_date(self, client: AsyncClient, auth_headers: dict):
        """Test getting weekly report with specific date."""
        week_start = date.today() - timedelta(days=date.today().weekday())
        
        response = await client.get(
            f"/api/v1/reports/weekly?week_start={week_start.isoformat()}",
            headers=auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["week_start"] == week_start.isoformat()


class TestReportEndpointsEdgeCases:
    """Edge case tests for report endpoints."""

    @pytest.mark.asyncio
    async def test_get_practice_history_large_page(self, client: AsyncClient, auth_headers: dict):
        """Test getting practice history with large page number."""
        response = await client.get(
            "/api/v1/reports/history?page=1000",
            headers=auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []

    @pytest.mark.asyncio
    async def test_get_practice_history_max_limit(self, client: AsyncClient, auth_headers: dict):
        """Test getting practice history with max limit."""
        response = await client.get(
            "/api/v1/reports/history?limit=50",
            headers=auth_headers,
        )
        
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_practice_history_limit_exceeds_max(self, client: AsyncClient, auth_headers: dict):
        """Test getting practice history with limit exceeding max."""
        response = await client.get(
            "/api/v1/reports/history?limit=100",
            headers=auth_headers,
        )
        
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_get_practice_history_invalid_page(self, client: AsyncClient, auth_headers: dict):
        """Test getting practice history with invalid page."""
        response = await client.get(
            "/api/v1/reports/history?page=0",
            headers=auth_headers,
        )
        
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_get_practice_history_invalid_limit(self, client: AsyncClient, auth_headers: dict):
        """Test getting practice history with invalid limit."""
        response = await client.get(
            "/api/v1/reports/history?limit=0",
            headers=auth_headers,
        )
        
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_get_practice_history_negative_limit(self, client: AsyncClient, auth_headers: dict):
        """Test getting practice history with negative limit."""
        response = await client.get(
            "/api/v1/reports/history?limit=-1",
            headers=auth_headers,
        )
        
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_get_practice_history_invalid_date_format(self, client: AsyncClient, auth_headers: dict):
        """Test getting practice history with invalid date format."""
        response = await client.get(
            "/api/v1/reports/history?start_date=invalid-date",
            headers=auth_headers,
        )
        
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_get_weekly_report_future_date(self, client: AsyncClient, auth_headers: dict):
        """Test getting weekly report with future date."""
        future_date = date.today() + timedelta(days=30)
        
        response = await client.get(
            f"/api/v1/reports/weekly?week_start={future_date.isoformat()}",
            headers=auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_sessions"] == 0

    @pytest.mark.asyncio
    async def test_get_weekly_report_invalid_date_format(self, client: AsyncClient, auth_headers: dict):
        """Test getting weekly report with invalid date format."""
        response = await client.get(
            "/api/v1/reports/weekly?week_start=invalid-date",
            headers=auth_headers,
        )
        
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_get_practice_history_structure(self, client: AsyncClient, auth_headers: dict):
        """Test practice history response structure."""
        response = await client.get(
            "/api/v1/reports/history",
            headers=auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "limit" in data
        assert "pages" in data

    @pytest.mark.asyncio
    async def test_get_weekly_report_structure(self, client: AsyncClient, auth_headers: dict):
        """Test weekly report response structure."""
        response = await client.get(
            "/api/v1/reports/weekly",
            headers=auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "week_start" in data
        assert "week_end" in data
        assert "total_sessions" in data
        assert "total_duration_minutes" in data
        assert "average_score" in data
        assert "scenarios_practiced" in data
        assert "improvement_percentage" in data
        assert "daily_breakdown" in data
