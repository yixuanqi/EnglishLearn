"""Unit tests for scenario service."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.services.scenario_service import ScenarioService
from app.schemas.scenario import CreateScenarioRequest, ScenarioCategory, DifficultyLevel
from app.models.scenario import Scenario


class MockScenarioUpdate:
    """Mock update request for testing."""
    
    def __init__(self, **kwargs):
        self._data = kwargs
    
    def model_dump(self, exclude_unset=False):
        return self._data


class TestScenarioService:
    """Tests for ScenarioService."""

    @pytest.fixture
    def mock_db(self):
        """Create mock database session."""
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def scenario_service(self, mock_db):
        """Create scenario service instance."""
        return ScenarioService(mock_db)

    @pytest.fixture
    def sample_scenario_create(self):
        """Create sample scenario creation data."""
        return CreateScenarioRequest(
            title="Test Scenario",
            description="Test description",
            category=ScenarioCategory.EXHIBITION,
            difficulty=DifficultyLevel.INTERMEDIATE,
            context="Test context",
            user_role="Sales Representative",
            ai_role="Customer",
            estimated_duration=15,
        )

    @pytest.fixture
    def sample_scenario_update(self):
        """Create sample scenario update data."""
        return MockScenarioUpdate(
            title="Updated Scenario",
            description="Updated description",
        )

    @pytest.mark.asyncio
    async def test_list_scenarios_no_filters(self, scenario_service, mock_db):
        """Test listing scenarios without filters."""
        mock_scenario1 = MagicMock(spec=Scenario)
        mock_scenario2 = MagicMock(spec=Scenario)
        mock_scenarios = [mock_scenario1, mock_scenario2]
        
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = mock_scenarios
        
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        
        mock_count_result = MagicMock()
        mock_count_result.scalar.return_value = 2
        
        mock_db.execute.side_effect = [mock_count_result, mock_result]
        
        scenarios, total = await scenario_service.list_scenarios()
        
        assert len(scenarios) == 2
        assert total == 2

    @pytest.mark.asyncio
    async def test_list_scenarios_with_category_filter(self, scenario_service, mock_db):
        """Test listing scenarios with category filter."""
        mock_scenario = MagicMock(spec=Scenario)
        mock_scenarios = [mock_scenario]
        
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = mock_scenarios
        
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        
        mock_count_result = MagicMock()
        mock_count_result.scalar.return_value = 1
        
        mock_db.execute.side_effect = [mock_count_result, mock_result]
        
        scenarios, total = await scenario_service.list_scenarios(
            category="exhibition"
        )
        
        assert len(scenarios) == 1
        assert total == 1

    @pytest.mark.asyncio
    async def test_list_scenarios_with_difficulty_filter(self, scenario_service, mock_db):
        """Test listing scenarios with difficulty filter."""
        mock_scenario = MagicMock(spec=Scenario)
        mock_scenarios = [mock_scenario]
        
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = mock_scenarios
        
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        
        mock_count_result = MagicMock()
        mock_count_result.scalar.return_value = 1
        
        mock_db.execute.side_effect = [mock_count_result, mock_result]
        
        scenarios, total = await scenario_service.list_scenarios(
            difficulty="intermediate"
        )
        
        assert len(scenarios) == 1
        assert total == 1

    @pytest.mark.asyncio
    async def test_list_scenarios_with_pagination(self, scenario_service, mock_db):
        """Test listing scenarios with pagination."""
        mock_scenario = MagicMock(spec=Scenario)
        mock_scenarios = [mock_scenario]
        
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = mock_scenarios
        
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        
        mock_count_result = MagicMock()
        mock_count_result.scalar.return_value = 10
        
        mock_db.execute.side_effect = [mock_count_result, mock_result]
        
        scenarios, total = await scenario_service.list_scenarios(
            page=2,
            page_size=5
        )
        
        assert len(scenarios) == 1
        assert total == 10

    @pytest.mark.asyncio
    async def test_list_scenarios_empty(self, scenario_service, mock_db):
        """Test listing scenarios when empty."""
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        
        mock_count_result = MagicMock()
        mock_count_result.scalar.return_value = 0
        
        mock_db.execute.side_effect = [mock_count_result, mock_result]
        
        scenarios, total = await scenario_service.list_scenarios()
        
        assert len(scenarios) == 0
        assert total == 0

    @pytest.mark.asyncio
    async def test_get_scenario_found(self, scenario_service, mock_db):
        """Test getting scenario by ID when found."""
        mock_scenario = MagicMock(spec=Scenario)
        mock_scenario.id = "scenario-123"
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_scenario
        mock_db.execute.return_value = mock_result
        
        result = await scenario_service.get_scenario("scenario-123")
        
        assert result == mock_scenario

    @pytest.mark.asyncio
    async def test_get_scenario_not_found(self, scenario_service, mock_db):
        """Test getting scenario by ID when not found."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result
        
        result = await scenario_service.get_scenario("nonexistent-id")
        
        assert result is None

    @pytest.mark.asyncio
    async def test_create_scenario_success(self, scenario_service, mock_db, sample_scenario_create):
        """Test successful scenario creation."""
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()
        
        result = await scenario_service.create_scenario(sample_scenario_create)
        
        assert isinstance(result, Scenario)
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_scenario_found(self, scenario_service, mock_db, sample_scenario_update):
        """Test updating scenario when found."""
        mock_scenario = MagicMock(spec=Scenario)
        mock_scenario.id = "scenario-123"
        mock_scenario.title = "Old Title"
        mock_scenario.description = "Old description"
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_scenario
        mock_db.execute.return_value = mock_result
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()
        
        result = await scenario_service.update_scenario(
            "scenario-123",
            sample_scenario_update
        )
        
        assert result == mock_scenario
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_scenario_not_found(self, scenario_service, mock_db, sample_scenario_update):
        """Test updating scenario when not found."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result
        
        result = await scenario_service.update_scenario(
            "nonexistent-id",
            sample_scenario_update
        )
        
        assert result is None

    @pytest.mark.asyncio
    async def test_update_scenario_partial(self, scenario_service, mock_db):
        """Test partial scenario update."""
        mock_scenario = MagicMock(spec=Scenario)
        mock_scenario.id = "scenario-123"
        mock_scenario.title = "Old Title"
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_scenario
        mock_db.execute.return_value = mock_result
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()
        
        partial_update = MockScenarioUpdate(title="New Title")
        
        result = await scenario_service.update_scenario(
            "scenario-123",
            partial_update
        )
        
        assert result == mock_scenario


class TestScenarioServiceEdgeCases:
    """Edge case tests for ScenarioService."""

    @pytest.fixture
    def mock_db(self):
        """Create mock database session."""
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def scenario_service(self, mock_db):
        """Create scenario service instance."""
        return ScenarioService(mock_db)

    @pytest.mark.asyncio
    async def test_list_scenarios_large_page_number(self, scenario_service, mock_db):
        """Test listing scenarios with large page number."""
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        
        mock_count_result = MagicMock()
        mock_count_result.scalar.return_value = 5
        
        mock_db.execute.side_effect = [mock_count_result, mock_result]
        
        scenarios, total = await scenario_service.list_scenarios(
            page=100,
            page_size=10
        )
        
        assert len(scenarios) == 0
        assert total == 5

    @pytest.mark.asyncio
    async def test_list_scenarios_page_size_one(self, scenario_service, mock_db):
        """Test listing scenarios with page size of 1."""
        mock_scenario = MagicMock(spec=Scenario)
        
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [mock_scenario]
        
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        
        mock_count_result = MagicMock()
        mock_count_result.scalar.return_value = 50
        
        mock_db.execute.side_effect = [mock_count_result, mock_result]
        
        scenarios, total = await scenario_service.list_scenarios(
            page=1,
            page_size=1
        )
        
        assert len(scenarios) == 1
        assert total == 50

    @pytest.mark.asyncio
    async def test_create_scenario_with_all_fields(self, scenario_service, mock_db):
        """Test creating scenario with all fields."""
        scenario_create = CreateScenarioRequest(
            title="Full Scenario",
            description="Complete description",
            category=ScenarioCategory.BUSINESS,
            difficulty=DifficultyLevel.ADVANCED,
            context="Business meeting context",
            user_role="Manager",
            ai_role="Client",
            estimated_duration=30,
        )
        
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()
        
        result = await scenario_service.create_scenario(scenario_create)
        
        assert isinstance(result, Scenario)
        mock_db.add.assert_called_once()
