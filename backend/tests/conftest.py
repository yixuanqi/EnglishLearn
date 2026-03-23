import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import JSON
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects import sqlite

sqlite.base.JSONB = JSON

from app.main import app
from app.core.config import settings
from app.models.base import Base
from app.core.dependencies import get_db

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestingSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


@pytest.fixture(scope="session", autouse=True)
def setup_jsonb_for_sqlite():
    import app.models.scenario
    import app.models.practice
    import app.models.dialogue
    import app.models.payment
    import app.models.custom_scenario
    
    modules = [
        app.models.scenario,
        app.models.practice,
        app.models.dialogue,
        app.models.payment,
        app.models.custom_scenario,
    ]
    
    for module in modules:
        for name in dir(module):
            obj = getattr(module, name)
            if isinstance(obj, type) and hasattr(obj, '__table__'):
                for column in obj.__table__.columns:
                    if hasattr(column.type, '__class__') and column.type.__class__.__name__ == 'JSONB':
                        column.type = JSON()


@pytest.fixture
async def db_session():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestingSessionLocal() as session:
        yield session
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def client(db_session: AsyncSession):
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
def mock_user():
    return {
        "email": "test@example.com",
        "password": "TestPass123!",
        "name": "Test User"
    }


@pytest.fixture
async def auth_headers(client: AsyncClient, mock_user: dict):
    response = await client.post("/v1/auth/register", json=mock_user)
    data = response.json()
    if "access_token" in data:
        token = data["access_token"]
    else:
        token = data.get("data", {}).get("access_token", "")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def mock_scenario():
    return {
        "title": "Test Scenario",
        "description": "Test description",
        "category": "exhibition",
        "difficulty": "intermediate",
        "context": "Test context",
        "user_role": "Sales",
        "ai_role": "Customer",
        "estimated_duration": 10
    }
