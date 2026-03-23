"""Integration tests for payment endpoints."""

import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock


class TestPaymentEndpoints:
    """Tests for payment endpoints."""

    @pytest.mark.asyncio
    async def test_get_subscription_plans_success(self, client: AsyncClient):
        """Test getting subscription plans."""
        response = await client.get("/api/v1/payments/plans")
        
        assert response.status_code == 200
        data = response.json()
        assert "plans" in data
        assert len(data["plans"]) == 3

    @pytest.mark.asyncio
    async def test_get_subscription_plans_contains_free(self, client: AsyncClient):
        """Test that subscription plans include free plan."""
        response = await client.get("/api/v1/payments/plans")
        
        assert response.status_code == 200
        data = response.json()
        plan_ids = [p["id"] for p in data["plans"]]
        assert "free" in plan_ids

    @pytest.mark.asyncio
    async def test_get_subscription_plans_contains_premium(self, client: AsyncClient):
        """Test that subscription plans include premium plans."""
        response = await client.get("/api/v1/payments/plans")
        
        assert response.status_code == 200
        data = response.json()
        plan_ids = [p["id"] for p in data["plans"]]
        assert "premium_monthly" in plan_ids
        assert "premium_annual" in plan_ids

    @pytest.mark.asyncio
    async def test_get_subscription_status_unauthorized(self, client: AsyncClient):
        """Test getting subscription status without authentication."""
        response = await client.get("/api/v1/payments/subscription")
        
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_subscription_status_success(self, client: AsyncClient, auth_headers: dict):
        """Test getting subscription status with authentication."""
        response = await client.get(
            "/api/v1/payments/subscription",
            headers=auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "plan" in data
        assert "is_active" in data
        assert "is_premium" in data

    @pytest.mark.asyncio
    async def test_get_subscription_status_free_user(self, client: AsyncClient, auth_headers: dict):
        """Test getting subscription status for free user."""
        response = await client.get(
            "/api/v1/payments/subscription",
            headers=auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["plan"] == "free"
        assert data["is_premium"] is False

    @pytest.mark.asyncio
    async def test_verify_receipt_unauthorized(self, client: AsyncClient):
        """Test verifying receipt without authentication."""
        response = await client.post(
            "/api/v1/payments/verify",
            json={
                "platform": "ios",
                "receipt_data": "test_receipt",
            },
        )
        
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_verify_receipt_missing_platform(self, client: AsyncClient, auth_headers: dict):
        """Test verifying receipt with missing platform."""
        response = await client.post(
            "/api/v1/payments/verify",
            json={"receipt_data": "test_receipt"},
            headers=auth_headers,
        )
        
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_verify_receipt_missing_receipt_data(self, client: AsyncClient, auth_headers: dict):
        """Test verifying receipt with missing receipt data."""
        response = await client.post(
            "/api/v1/payments/verify",
            json={"platform": "ios"},
            headers=auth_headers,
        )
        
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_cancel_subscription_unauthorized(self, client: AsyncClient):
        """Test canceling subscription without authentication."""
        response = await client.post("/api/v1/payments/subscription/cancel")
        
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_cancel_subscription_free_user(self, client: AsyncClient, auth_headers: dict):
        """Test canceling subscription for free user."""
        response = await client.post(
            "/api/v1/payments/subscription/cancel",
            headers=auth_headers,
        )
        
        assert response.status_code == 400


class TestPaymentEndpointsEdgeCases:
    """Edge case tests for payment endpoints."""

    @pytest.mark.asyncio
    async def test_get_subscription_plans_structure(self, client: AsyncClient):
        """Test subscription plans response structure."""
        response = await client.get("/api/v1/payments/plans")
        
        assert response.status_code == 200
        data = response.json()
        
        for plan in data["plans"]:
            assert "id" in plan
            assert "name" in plan
            assert "description" in plan
            assert "features" in plan
            assert isinstance(plan["features"], list)

    @pytest.mark.asyncio
    async def test_get_subscription_plans_pricing(self, client: AsyncClient):
        """Test subscription plans pricing."""
        response = await client.get("/api/v1/payments/plans")
        
        assert response.status_code == 200
        data = response.json()
        
        for plan in data["plans"]:
            if plan["id"] == "free":
                assert plan["monthly_price"] == 0.0
            elif plan["id"] == "premium_monthly":
                assert plan["monthly_price"] > 0
            elif plan["id"] == "premium_annual":
                assert plan["annual_price"] > 0

    @pytest.mark.asyncio
    async def test_verify_receipt_invalid_platform(self, client: AsyncClient, auth_headers: dict):
        """Test verifying receipt with invalid platform."""
        response = await client.post(
            "/api/v1/payments/verify",
            json={
                "platform": "invalid_platform",
                "receipt_data": "test_receipt",
            },
            headers=auth_headers,
        )
        
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_verify_receipt_empty_receipt_data(self, client: AsyncClient, auth_headers: dict):
        """Test verifying receipt with empty receipt data."""
        response = await client.post(
            "/api/v1/payments/verify",
            json={
                "platform": "ios",
                "receipt_data": "",
            },
            headers=auth_headers,
        )
        
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_get_subscription_status_features(self, client: AsyncClient, auth_headers: dict):
        """Test subscription status includes features."""
        response = await client.get(
            "/api/v1/payments/subscription",
            headers=auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "features" in data
        assert isinstance(data["features"], list)

    @pytest.mark.asyncio
    async def test_subscription_plans_popular_flag(self, client: AsyncClient):
        """Test subscription plans popular flag."""
        response = await client.get("/api/v1/payments/plans")
        
        assert response.status_code == 200
        data = response.json()
        
        popular_plans = [p for p in data["plans"] if p.get("is_popular")]
        assert len(popular_plans) >= 1
