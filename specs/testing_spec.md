# Testing Specification

## 1. Overview

### 1.1 Testing Philosophy
- Test early, test often
- Automate everything possible
- Tests should be fast, reliable, and maintainable
- Tests serve as living documentation
- Aim for high coverage without sacrificing quality

### 1.2 Testing Pyramid

```
┌─────────────────────────────────────────────────────────────────┐
│                      TESTING PYRAMID                            │
└─────────────────────────────────────────────────────────────────┘

                    ┌─────────────┐
                    │  E2E Tests  │  ← 10% (Slow, expensive)
                    │   (Playwright)│
                    └──────┬──────┘
                           │
              ┌────────────┴────────────┐
              │                         │
        ┌─────┴─────┐           ┌──────┴──────┐
        │Integration │           │Integration │
        │  Tests    │           │   Tests    │
        │ (Backend) │           │  (Flutter)  │
        └─────┬─────┘           └──────┬──────┘
              │                         │
              └────────────┬────────────┘
                           │
              ┌────────────┴────────────┐
              │                         │
        ┌─────┴─────┐           ┌──────┴──────┐
        │  Unit     │           │   Widget    │
        │  Tests    │           │   Tests     │
        │ (Backend) │           │  (Flutter)  │
        └───────────┘           └─────────────┘
              │                         │
              └────────────┬────────────┘
                           │
                    ┌──────┴──────┐
                    │ Unit Tests  │  ← 70% (Fast, cheap)
                    │ (Dart)     │
                    └─────────────┘
```

### 1.3 Coverage Targets

| Test Type | Target Coverage | Priority |
|-----------|----------------|----------|
| Unit Tests | 90%+ | High |
| Integration Tests | 80%+ | High |
| Widget Tests | 70%+ | Medium |
| E2E Tests | Critical paths | Medium |

---

## 2. Backend Testing (Python)

### 2.1 Test Structure

```
tests/
├── __init__.py
├── conftest.py                 # Shared fixtures and configuration
├── unit/
│   ├── __init__.py
│   ├── test_services/
│   │   ├── __init__.py
│   │   ├── test_auth_service.py
│   │   ├── test_scenario_service.py
│   │   ├── test_dialogue_service.py
│   │   ├── test_practice_service.py
│   │   └── test_evaluation_service.py
│   ├── test_repositories/
│   │   ├── __init__.py
│   │   ├── test_user_repo.py
│   │   ├── test_scenario_repo.py
│   │   └── test_practice_repo.py
│   └── test_utils/
│       ├── __init__.py
│       ├── test_cache.py
│       └── test_logger.py
├── integration/
│   ├── __init__.py
│   ├── test_api/
│   │   ├── __init__.py
│   │   ├── test_auth_endpoints.py
│   │   ├── test_scenario_endpoints.py
│   │   ├── test_dialogue_endpoints.py
│   │   ├── test_practice_endpoints.py
│   │   ├── test_evaluation_endpoints.py
│   │   ├── test_report_endpoints.py
│   │   └── test_payment_endpoints.py
│   └── test_ai/
│       ├── __init__.py
│       ├── test_llm_client.py
│       ├── test_tts_client.py
│       ├── test_stt_client.py
│       └── test_pronunciation_evaluator.py
└── e2e/
    ├── __init__.py
    ├── test_user_journey.py
    └── test_payment_flow.py
```

### 2.2 Unit Testing

#### Test Configuration (conftest.py)

```python
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.config import settings
from app.models.base import Base
from app.core.dependencies import get_db

# Test database
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestingSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


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
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
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
def auth_headers(client: AsyncClient, mock_user: dict):
    response = await client.post("/v1/auth/register", json=mock_user)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
```

#### Service Unit Test Example

```python
import pytest
from unittest.mock import AsyncMock, patch
from app.services.auth_service import AuthService
from app.core.exceptions import NotFoundError, AuthenticationError


class TestAuthService:
    @pytest.mark.asyncio
    async def test_login_success(self, db_session, mock_user):
        service = AuthService(db_session)
        
        # Create user first
        await service.register(**mock_user)
        
        # Test login
        result = await service.login(
            email=mock_user["email"],
            password=mock_user["password"]
        )
        
        assert result.access_token is not None
        assert result.refresh_token is not None
        assert result.user.email == mock_user["email"]

    @pytest.mark.asyncio
    async def test_login_invalid_password(self, db_session, mock_user):
        service = AuthService(db_session)
        await service.register(**mock_user)
        
        with pytest.raises(AuthenticationError):
            await service.login(
                email=mock_user["email"],
                password="WrongPassword123!"
            )

    @pytest.mark.asyncio
    async def test_login_user_not_found(self, db_session):
        service = AuthService(db_session)
        
        with pytest.raises(NotFoundError):
            await service.login(
                email="nonexistent@example.com",
                password="TestPass123!"
            )

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, db_session, mock_user):
        service = AuthService(db_session)
        await service.register(**mock_user)
        
        with pytest.raises(ValueError):
            await service.register(**mock_user)
```

#### Repository Unit Test Example

```python
import pytest
from app.repositories.user_repo import UserRepository
from app.models.user import User


class TestUserRepository:
    @pytest.mark.asyncio
    async def test_create_user(self, db_session):
        repo = UserRepository(db_session)
        user = await repo.create(
            email="test@example.com",
            password_hash="hashed_password",
            name="Test User"
        )
        
        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.is_active is True

    @pytest.mark.asyncio
    async def test_get_by_email(self, db_session):
        repo = UserRepository(db_session)
        created = await repo.create(
            email="test@example.com",
            password_hash="hashed_password",
            name="Test User"
        )
        
        user = await repo.get_by_email("test@example.com")
        
        assert user.id == created.id
        assert user.email == "test@example.com"

    @pytest.mark.asyncio
    async def test_get_by_email_not_found(self, db_session):
        repo = UserRepository(db_session)
        user = await repo.get_by_email("nonexistent@example.com")
        
        assert user is None
```

### 2.3 Integration Testing

#### API Endpoint Test Example

```python
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
    async def test_login_success(self, client: AsyncClient, mock_user):
        # Register first
        await client.post("/v1/auth/register", json=mock_user)
        
        # Login
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
```

#### Scenario API Test Example

```python
class TestScenarioEndpoints:
    @pytest.mark.asyncio
    async def test_list_scenarios(self, client: AsyncClient, auth_headers):
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
        auth_headers
    ):
        response = await client.get(
            "/v1/scenarios?category=exhibition&difficulty=intermediate",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        for scenario in data["items"]:
            assert scenario["category"] == "exhibition"
            assert scenario["difficulty"] == "intermediate"

    @pytest.mark.asyncio
    async def test_get_scenario_detail(
        self,
        client: AsyncClient,
        auth_headers,
        db_session
    ):
        # Create a scenario
        from app.models.scenario import Scenario
        from uuid import uuid4
        
        scenario = Scenario(
            id=uuid4(),
            title="Test Scenario",
            description="Test description",
            category="exhibition",
            difficulty="intermediate",
            context="Test context",
            user_role="Sales",
            ai_role="Customer",
            estimated_duration=10
        )
        db_session.add(scenario)
        await db_session.commit()
        
        response = await client.get(
            f"/v1/scenarios/{scenario.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(scenario.id)
        assert data["title"] == "Test Scenario"
```

### 2.4 Mocking AI Services

```python
import pytest
from unittest.mock import AsyncMock, patch


class TestDialogueService:
    @pytest.mark.asyncio
    async def test_generate_dialogue_success(self, db_session):
        from app.services.dialogue_service import DialogueService
        
        service = DialogueService(db_session)
        
        # Mock LLM client
        with patch.object(
            service.llm_client,
            'generate_dialogue',
            new_callable=AsyncMock,
            return_value={
                "lines": [
                    {"id": 1, "speaker": "ai", "text": "Hello!"},
                    {"id": 2, "speaker": "user", "text": "Hi there!"}
                ]
            }
        ):
            result = await service.generate_dialogue(
                scenario_id=uuid4(),
                variation=1
            )
            
            assert result.lines is not None
            assert len(result.lines) == 2
            service.llm_client.generate_dialogue.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_dialogue_llm_failure(self, db_session):
        from app.services.dialogue_service import DialogueService
        from app.core.exceptions import AIServiceError
        
        service = DialogueService(db_session)
        
        with patch.object(
            service.llm_client,
            'generate_dialogue',
            new_callable=AsyncMock,
            side_effect=Exception("LLM API error")
        ):
            with pytest.raises(AIServiceError):
                await service.generate_dialogue(
                    scenario_id=uuid4(),
                    variation=1
                )
```

### 2.5 Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html --cov-report=term

# Run specific test file
pytest tests/unit/test_services/test_auth_service.py

# Run specific test
pytest tests/unit/test_services/test_auth_service.py::TestAuthService::test_login_success

# Run with verbose output
pytest -v

# Run only unit tests
pytest tests/unit/

# Run only integration tests
pytest tests/integration/

# Run tests matching a pattern
pytest -k "login"

# Run tests with markers
pytest -m "not slow"
```

---

## 3. Frontend Testing (Flutter)

### 3.1 Test Structure

```
test/
├── unit/
│   ├── features/
│   │   ├── auth/
│   │   │   ├── bloc/
│   │   │   │   ├── auth_bloc_test.dart
│   │   │   │   ├── auth_event_test.dart
│   │   │   │   └── auth_state_test.dart
│   │   │   ├── domain/
│   │   │   │   ├── entities/
│   │   │   │   │   └── user_test.dart
│   │   │   │   └── usecases/
│   │   │   │       ├── login_test.dart
│   │   │   │       └── logout_test.dart
│   │   │   └── data/
│   │   │       ├── models/
│   │   │       │   └── user_model_test.dart
│   │   │       └── repositories/
│   │   │           └── auth_repository_impl_test.dart
│   │   ├── scenarios/
│   │   ├── practice/
│   │   └── profile/
│   └── shared/
│       ├── utils/
│       │   ├── validators_test.dart
│       │   └── formatters_test.dart
│       └── services/
│           ├── audio_service_test.dart
│           └── storage_service_test.dart
├── widget/
│   ├── features/
│   │   ├── auth/
│   │   │   ├── pages/
│   │   │   │   ├── login_page_test.dart
│   │   │   │   └── register_page_test.dart
│   │   │   └── widgets/
│   │   │       └── auth_form_test.dart
│   │   ├── scenarios/
│   │   ├── practice/
│   │   └── profile/
│   └── shared/
│       └── widgets/
│           ├── buttons/
│           ├── inputs/
│           └── cards/
└── integration/
    ├── app_test.dart
    └── features/
        ├── auth/
        │   └── auth_flow_test.dart
        └── practice/
            └── practice_session_test.dart
```

### 3.2 Unit Testing

#### BLoC Test Example

```dart
import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/annotations.dart';
import 'package:mockito/mockito.dart';
import 'package:bloc_test/bloc_test.dart';

import 'package:english_speaking_trainer/features/auth/domain/entities/user.dart';
import 'package:english_speaking_trainer/features/auth/domain/usecases/login.dart';
import 'package:english_speaking_trainer/features/auth/domain/repositories/auth_repository.dart';
import 'package:english_speaking_trainer/features/auth/presentation/bloc/auth_bloc.dart';
import 'package:english_speaking_trainer/core/errors/failures.dart';

@GenerateMocks([AuthRepository])
import 'auth_bloc_test.mocks.dart';

void main() {
  late AuthBloc authBloc;
  late MockAuthRepository mockAuthRepository;

  setUp(() {
    mockAuthRepository = MockAuthRepository();
    authBloc = AuthBloc(
      login: Login(mockAuthRepository),
      logout: Logout(mockAuthRepository),
      getCurrentUser: GetCurrentUser(mockAuthRepository),
    );
  });

  tearDown(() {
    authBloc.close();
  });

  test('initial state should be AuthInitial', () {
    expect(authBloc.state, equals(AuthInitial()));
  });

  group('LoginRequested', () {
    const tEmail = 'test@example.com';
    const tPassword = 'TestPass123!';
    const tUser = User(
      id: '1',
      email: tEmail,
      name: 'Test User',
    );

    blocTest<AuthBloc, AuthState>(
      'emits [AuthLoading, Authenticated] when login is successful',
      build: () {
        when(mockAuthRepository.login(
          email: anyNamed('email'),
          password: anyNamed('password'),
        )).thenAnswer((_) async => Right(tUser));
        return authBloc;
      },
      act: (bloc) => bloc.add(const LoginRequested(
        email: tEmail,
        password: tPassword,
      )),
      expect: () => [
        AuthLoading(),
        Authenticated(tUser),
      ],
      verify: (_) {
        verify(mockAuthRepository.login(
          email: tEmail,
          password: tPassword,
        ));
      },
    );

    blocTest<AuthBloc, AuthState>(
      'emits [AuthLoading, AuthError] when login fails',
      build: () {
        when(mockAuthRepository.login(
          email: anyNamed('email'),
          password: anyNamed('password'),
        )).thenAnswer((_) async => Left(ServerFailure('Server error')));
        return authBloc;
      },
      act: (bloc) => bloc.add(const LoginRequested(
        email: tEmail,
        password: tPassword,
      )),
      expect: () => [
        AuthLoading(),
        const AuthError('Server error'),
      ],
    );
  });
}
```

#### Use Case Test Example

```dart
import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/annotations.dart';
import 'package:mockito/mockito.dart';
import 'package:dartz/dartz.dart';

import 'package:english_speaking_trainer/features/auth/domain/entities/user.dart';
import 'package:english_speaking_trainer/features/auth/domain/usecases/login.dart';
import 'package:english_speaking_trainer/features/auth/domain/repositories/auth_repository.dart';
import 'package:english_speaking_trainer/core/errors/failures.dart';

@GenerateMocks([AuthRepository])
import 'login_test.mocks.dart';

void main() {
  late Login usecase;
  late MockAuthRepository mockAuthRepository;

  setUp(() {
    mockAuthRepository = MockAuthRepository();
    usecase = Login(mockAuthRepository);
  });

  const tEmail = 'test@example.com';
  const tPassword = 'TestPass123!';
  const tUser = User(
    id: '1',
    email: tEmail,
    name: 'Test User',
  );

  test('should get User from the repository', () async {
    when(mockAuthRepository.login(
      email: anyNamed('email'),
      password: anyNamed('password'),
    )).thenAnswer((_) async => const Right(tUser));

    final result = await usecase(
      const LoginParams(
        email: tEmail,
        password: tPassword,
      ),
    );

    expect(result, const Right(tUser));
    verify(mockAuthRepository.login(
      email: tEmail,
      password: tPassword,
    ));
    verifyNoMoreInteractions(mockAuthRepository);
  });

  test('should return ServerFailure when login fails', () async {
    when(mockAuthRepository.login(
      email: anyNamed('email'),
      password: anyNamed('password'),
    )).thenAnswer((_) async => const Left(ServerFailure('Server error')));

    final result = await usecase(
      const LoginParams(
        email: tEmail,
        password: tPassword,
      ),
    );

    expect(result, const Left(ServerFailure('Server error')));
  });
}
```

### 3.3 Widget Testing

```dart
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:english_speaking_trainer/features/auth/presentation/pages/login_page.dart';
import 'package:english_speaking_trainer/features/auth/presentation/bloc/auth_bloc.dart';
import 'package:mockito/mockito.dart';

class MockAuthBloc extends Mock implements AuthBloc {}

void main() {
  group('LoginPage', () {
    late MockAuthBloc mockAuthBloc;

    setUp(() {
      mockAuthBloc = MockAuthBloc();
    });

    testWidgets('should render email and password fields',
        (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: BlocProvider<AuthBloc>.value(
            value: mockAuthBloc,
            child: const LoginPage(),
          ),
        ),
      );

      expect(find.byKey(const Key('email_field')), findsOneWidget);
      expect(find.byKey(const Key('password_field')), findsOneWidget);
      expect(find.byKey(const Key('login_button')), findsOneWidget);
    });

    testWidgets('should enable login button when form is valid',
        (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: BlocProvider<AuthBloc>.value(
            value: mockAuthBloc,
            child: const LoginPage(),
          ),
        ),
      );

      final emailField = find.byKey(const Key('email_field'));
      final passwordField = find.byKey(const Key('password_field'));
      final loginButton = find.byKey(const Key('login_button'));

      await tester.enterText(emailField, 'test@example.com');
      await tester.enterText(passwordField, 'TestPass123!');
      await tester.pump();

      final button = tester.widget<ElevatedButton>(loginButton);
      expect(button.enabled, isTrue);
    });

    testWidgets('should call login when button is pressed',
        (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: BlocProvider<AuthBloc>.value(
            value: mockAuthBloc,
            child: const LoginPage(),
          ),
        ),
      );

      final emailField = find.byKey(const Key('email_field'));
      final passwordField = find.byKey(const Key('password_field'));
      final loginButton = find.byKey(const Key('login_button'));

      await tester.enterText(emailField, 'test@example.com');
      await tester.enterText(passwordField, 'TestPass123!');
      await tester.tap(loginButton);
      await tester.pump();

      verify(mockAuthBloc.add(const LoginRequested(
        email: 'test@example.com',
        password: 'TestPass123!',
      ))).called(1);
    });
  });
}
```

### 3.4 Integration Testing

```dart
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:english_speaking_trainer/main.dart' as app;
import 'package:english_speaking_trainer/injection_container.dart' as di;

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  setUpAll(() async {
    await di.init();
  });

  testWidgets('full login flow', (WidgetTester tester) async {
    app.main();
    await tester.pumpAndSettle();

    // Navigate to login
    await tester.tap(find.text('Login'));
    await tester.pumpAndSettle();

    // Enter credentials
    await tester.enterText(
      find.byKey(const Key('email_field')),
      'test@example.com',
    );
    await tester.enterText(
      find.byKey(const Key('password_field')),
      'TestPass123!',
    );

    // Tap login button
    await tester.tap(find.byKey(const Key('login_button')));
    await tester.pumpAndSettle();

    // Verify navigation to home
    expect(find.text('Welcome'), findsOneWidget);
  });

  testWidgets('start practice session', (WidgetTester tester) async {
    app.main();
    await tester.pumpAndSettle();

    // Login first
    await tester.tap(find.text('Login'));
    await tester.pumpAndSettle();
    
    await tester.enterText(
      find.byKey(const Key('email_field')),
      'test@example.com',
    );
    await tester.enterText(
      find.byKey(const Key('password_field')),
      'TestPass123!',
    );
    await tester.tap(find.byKey(const Key('login_button')));
    await tester.pumpAndSettle();

    // Select scenario
    await tester.tap(find.text('Scenarios'));
    await tester.pumpAndSettle();
    
    await tester.tap(find.text('Product Introduction'));
    await tester.pumpAndSettle();

    // Start practice
    await tester.tap(find.text('Start Practice'));
    await tester.pumpAndSettle();

    // Verify practice screen
    expect(find.text('AI is speaking...'), findsOneWidget);
  });
}
```

### 3.5 Running Flutter Tests

```bash
# Run all tests
flutter test

# Run with coverage
flutter test --coverage

# Run specific test file
flutter test test/unit/features/auth/bloc/auth_bloc_test.dart

# Run specific test
flutter test test/unit/features/auth/bloc/auth_bloc_test.dart --name="login success"

# Run widget tests
flutter test test/widget/

# Run integration tests
flutter test integration_test/

# Run tests on specific platform
flutter test -d chrome
flutter test -d emulator-5554

# Run tests with verbose output
flutter test --verbose
```

---

## 4. Test Data Management

### 4.1 Fixtures

```python
# tests/fixtures/user_fixtures.py

import pytest
from uuid import uuid4
from app.models.user import User


@pytest.fixture
def user_data():
    return {
        "email": "test@example.com",
        "password": "TestPass123!",
        "name": "Test User",
        "english_level": "intermediate"
    }


@pytest.fixture
def user_entity(user_data):
    return User(
        id=uuid4(),
        email=user_data["email"],
        password_hash="hashed_password",
        name=user_data["name"],
        english_level=user_data["english_level"],
        subscription_plan="free",
        is_active=True,
    )


@pytest.fixture
def premium_user(user_data):
    return User(
        id=uuid4(),
        email=user_data["email"],
        password_hash="hashed_password",
        name=user_data["name"],
        english_level=user_data["english_level"],
        subscription_plan="premium_monthly",
        is_active=True,
    )
```

### 4.2 Test Factories

```python
# tests/factories.py

import random
from uuid import uuid4
from datetime import datetime, timedelta
from app.models.user import User
from app.models.scenario import Scenario
from app.models.practice import PracticeSession


class UserFactory:
    @staticmethod
    def create(**kwargs):
        defaults = {
            "id": uuid4(),
            "email": f"user{random.randint(1000, 9999)}@example.com",
            "password_hash": "hashed_password",
            "name": f"User {random.randint(1000, 9999)}",
            "english_level": random.choice(["beginner", "intermediate", "advanced"]),
            "subscription_plan": "free",
            "is_active": True,
        }
        defaults.update(kwargs)
        return User(**defaults)


class ScenarioFactory:
    @staticmethod
    def create(**kwargs):
        defaults = {
            "id": uuid4(),
            "title": f"Scenario {random.randint(1000, 9999)}",
            "description": "Test scenario description",
            "category": random.choice(["exhibition", "technical", "business", "daily_life"]),
            "difficulty": random.choice(["beginner", "intermediate", "advanced"]),
            "context": "Test context",
            "user_role": "User",
            "ai_role": "AI",
            "estimated_duration": 10,
            "is_premium": False,
            "is_active": True,
        }
        defaults.update(kwargs)
        return Scenario(**defaults)


class PracticeSessionFactory:
    @staticmethod
    def create(**kwargs):
        defaults = {
            "id": uuid4(),
            "user_id": uuid4(),
            "dialogue_id": uuid4(),
            "status": "completed",
            "current_turn": 5,
            "total_turns": 10,
            "started_at": datetime.utcnow() - timedelta(minutes=10),
            "ended_at": datetime.utcnow(),
            "duration_seconds": 600,
            "overall_score": random.uniform(60, 100),
        }
        defaults.update(kwargs)
        return PracticeSession(**defaults)
```

---

## 5. Test Automation & CI/CD

### 5.1 GitHub Actions Workflow

```yaml
# .github/workflows/test.yml

name: Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements/development.txt
      
      - name: Run tests
        run: |
          pytest --cov=app --cov-report=xml --cov-report=term
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml

  frontend-tests:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Flutter
        uses: subosito/flutter-action@v2
        with:
          flutter-version: '3.16.0'
      
      - name: Install dependencies
        run: flutter pub get
      
      - name: Run tests
        run: flutter test --coverage
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage/lcov.info
```

---

## 6. Test Metrics & Reporting

### 6.1 Coverage Requirements

| Component | Target | Minimum |
|-----------|--------|---------|
| Backend Services | 95% | 85% |
| Backend Repositories | 90% | 80% |
| Backend API Endpoints | 80% | 70% |
| Frontend Use Cases | 90% | 80% |
| Frontend BLoCs | 95% | 85% |
| Frontend Widgets | 70% | 60% |

### 6.2 Quality Gates

| Metric | Threshold | Action |
|--------|-----------|--------|
| Code Coverage | < 80% | Block merge |
| Test Failure Rate | > 5% | Block merge |
| Flaky Tests | > 2% | Investigate |
| Test Duration | > 10 min | Optimize |

---

## 7. Best Practices

### 7.1 General

- Write tests before or alongside code (TDD when possible)
- Keep tests independent and isolated
- Use descriptive test names
- One assertion per test when possible
- Mock external dependencies
- Test edge cases and error conditions
- Keep tests fast (unit tests < 1s)

### 7.2 Backend

- Use pytest fixtures for setup
- Mock database in unit tests
- Use test database for integration tests
- Clean up after each test
- Test async code properly
- Verify database state changes

### 7.3 Frontend

- Use widget tests for UI components
- Use integration tests for user flows
- Mock network calls
- Test loading and error states
- Verify navigation
- Test accessibility
