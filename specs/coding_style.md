# Coding Style Specification

## 1. Overview

This document defines coding standards for the English Speaking Trainer project to ensure:
- Consistent code style across the codebase
- Maintainable and readable code
- AI-assisted coding compatibility
- Long-term project sustainability

---

## 2. Python (FastAPI Backend)

### 2.1 Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application entry point
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py              # Configuration management
│   │   ├── security.py            # Security utilities
│   │   ├── exceptions.py          # Custom exceptions
│   │   └── dependencies.py        # Global dependencies
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py                # API dependencies
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── router.py          # API router aggregation
│   │       └── endpoints/
│   │           ├── __init__.py
│   │           ├── auth.py
│   │           ├── scenarios.py
│   │           ├── dialogues.py
│   │           ├── practice.py
│   │           ├── evaluation.py
│   │           ├── reports.py
│   │           └── payments.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py                # Base model class
│   │   ├── user.py
│   │   ├── scenario.py
│   │   ├── dialogue.py
│   │   ├── practice.py
│   │   └── payment.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── base.py                # Base schema class
│   │   ├── user.py
│   │   ├── scenario.py
│   │   ├── dialogue.py
│   │   ├── practice.py
│   │   └── payment.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── base.py                # Base service class
│   │   ├── auth_service.py
│   │   ├── scenario_service.py
│   │   ├── dialogue_service.py
│   │   ├── practice_service.py
│   │   ├── evaluation_service.py
│   │   └── payment_service.py
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── base.py                # Base repository class
│   │   ├── user_repo.py
│   │   ├── scenario_repo.py
│   │   └── practice_repo.py
│   ├── ai/
│   │   ├── __init__.py
│   │   ├── base.py                # Base AI client
│   │   ├── llm_client.py
│   │   ├── tts_client.py
│   │   ├── stt_client.py
│   │   └── pronunciation_evaluator.py
│   └── utils/
│       ├── __init__.py
│       ├── cache.py
│       └── logger.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── unit/
│   └── integration/
├── migrations/
├── requirements/
│   ├── base.txt
│   ├── development.txt
│   └── production.txt
├── pyproject.toml
├── alembic.ini
└── Dockerfile
```

### 2.2 Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| Modules | snake_case | `auth_service.py` |
| Classes | PascalCase | `UserService` |
| Functions | snake_case | `get_user_by_id` |
| Methods | snake_case | `create_session` |
| Variables | snake_case | `user_id`, `session_data` |
| Constants | UPPER_SNAKE_CASE | `MAX_RETRY_COUNT` |
| Private methods | _leading_underscore | `_validate_token` |
| Protected methods | _leading_underscore | `_process_audio` |

### 2.3 Type Hints

All functions must include type hints:

```python
from typing import Optional, List
from uuid import UUID

async def get_user_by_id(user_id: UUID) -> Optional[User]:
    ...

def create_session(
    user_id: UUID,
    dialogue_id: UUID,
    metadata: Optional[dict] = None
) -> PracticeSession:
    ...

async def list_scenarios(
    category: Optional[str] = None,
    page: int = 1,
    page_size: int = 20
) -> tuple[List[Scenario], int]:
    ...
```

### 2.4 Docstrings

Use Google-style docstrings:

```python
async def generate_dialogue(
    scenario_id: UUID,
    variation: int = 1
) -> Dialogue:
    """Generate a dialogue for a given scenario.
    
    Args:
        scenario_id: The UUID of the scenario.
        variation: The dialogue variation number (1-5).
    
    Returns:
        The generated Dialogue object.
    
    Raises:
        ScenarioNotFoundError: If scenario does not exist.
        AIGenerationError: If dialogue generation fails.
    
    Example:
        >>> dialogue = await generate_dialogue(
        ...     scenario_id=UUID("..."),
        ...     variation=1
        ... )
    """
    ...
```

### 2.5 Import Organization

```python
# Standard library
import asyncio
from typing import Optional, List
from uuid import UUID

# Third-party
from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

# Local imports
from app.core.config import settings
from app.models.scenario import Scenario
from app.schemas.scenario import ScenarioCreate, ScenarioResponse
from app.repositories.scenario_repo import ScenarioRepository
```

### 2.6 Layered Architecture Rules

```
┌─────────────────────────────────────────────────────────────────┐
│                    LAYER DEPENDENCY RULES                        │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────┐
│   Endpoints     │  ← API layer, handles HTTP requests
└────────┬────────┘
         │ depends on
         ▼
┌─────────────────┐
│   Services      │  ← Business logic layer
└────────┬────────┘
         │ depends on
         ▼
┌─────────────────┐
│  Repositories   │  ← Data access layer
└────────┬────────┘
         │ depends on
         ▼
┌─────────────────┐
│    Models       │  ← Database models
└─────────────────┘

RULES:
- Endpoints can only import Services and Schemas
- Services can import Repositories, Models, and other Services
- Repositories can only import Models
- Models should not import from any other layer
```

### 2.7 Error Handling

#### Custom Exceptions

```python
# app/core/exceptions.py

class AppException(Exception):
    """Base exception for application errors."""
    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        details: Optional[List[dict]] = None
    ):
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details or []
        super().__init__(self.message)


class NotFoundError(AppException):
    def __init__(self, resource: str, identifier: str):
        super().__init__(
            status_code=404,
            code="NOT_FOUND",
            message=f"{resource} not found: {identifier}"
        )


class ValidationError(AppException):
    def __init__(self, details: List[dict]):
        super().__init__(
            status_code=400,
            code="VALIDATION_ERROR",
            message="Validation failed",
            details=details
        )


class AuthenticationError(AppException):
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            status_code=401,
            code="AUTHENTICATION_ERROR",
            message=message
        )


class AuthorizationError(AppException):
    def __init__(self, message: str = "Access denied"):
        super().__init__(
            status_code=403,
            code="AUTHORIZATION_ERROR",
            message=message
        )


class AIServiceError(AppException):
    def __init__(self, service: str, message: str):
        super().__init__(
            status_code=502,
            code="AI_SERVICE_ERROR",
            message=f"{service} error: {message}"
        )
```

#### Exception Handler

```python
# app/main.py

from fastapi import Request
from fastapi.responses import JSONResponse
from app.core.exceptions import AppException

@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
                "request_id": request.state.request_id
            }
        }
    )
```

### 2.8 Configuration Management

```python
# app/core/config.py

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "English Speaking Trainer"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: str
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10
    
    # Redis
    REDIS_URL: str
    
    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # AI Services
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4"
    AZURE_SPEECH_KEY: Optional[str] = None
    AZURE_SPEECH_REGION: str = "eastus"
    
    # Stripe
    STRIPE_SECRET_KEY: str
    STRIPE_WEBHOOK_SECRET: str
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
```

### 2.9 Async Patterns

```python
# Use async for I/O operations
async def get_user(user_id: UUID) -> Optional[User]:
    async with get_session() as session:
        result = await session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

# Use asyncio.gather for parallel operations
async def get_dashboard_data(user_id: UUID) -> dict:
    sessions, stats, recommendations = await asyncio.gather(
        get_recent_sessions(user_id),
        get_user_stats(user_id),
        get_recommendations(user_id)
    )
    return {
        "sessions": sessions,
        "stats": stats,
        "recommendations": recommendations
    }
```

### 2.10 Code Quality Tools

#### pyproject.toml

```toml
[tool.black]
line-length = 88
target-version = ['py311']
include = '\.pyi?$'
exclude = '''
/(
    \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | _build
  | buck-out
  | build
  | dist
  | migrations
)/
'''

[tool.isort]
profile = "black"
line_length = 88
skip = ["migrations"]

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
plugins = ["pydantic.mypy"]

[tool.ruff]
line-length = 88
select = ["E", "F", "I", "N", "W", "UP", "B", "C4"]
ignore = ["E501"]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

---

## 3. Flutter (Dart)

### 3.1 Project Structure

```
lib/
├── main.dart
├── core/
│   ├── constants/
│   │   ├── app_constants.dart
│   │   ├── api_constants.dart
│   │   └── asset_constants.dart
│   ├── theme/
│   │   ├── app_theme.dart
│   │   ├── colors.dart
│   │   └── text_styles.dart
│   ├── router/
│   │   ├── app_router.dart
│   │   └── routes.dart
│   ├── utils/
│   │   ├── validators.dart
│   │   ├── formatters.dart
│   │   └── extensions.dart
│   └── errors/
│       ├── exceptions.dart
│       └── failures.dart
├── features/
│   ├── auth/
│   │   ├── data/
│   │   │   ├── datasources/
│   │   │   │   ├── auth_local_datasource.dart
│   │   │   │   └── auth_remote_datasource.dart
│   │   │   ├── models/
│   │   │   │   ├── user_model.dart
│   │   │   │   └── auth_response_model.dart
│   │   │   └── repositories/
│   │   │       └── auth_repository_impl.dart
│   │   ├── domain/
│   │   │   ├── entities/
│   │   │   │   └── user.dart
│   │   │   ├── repositories/
│   │   │   │   └── auth_repository.dart
│   │   │   └── usecases/
│   │   │       ├── login.dart
│   │   │       ├── register.dart
│   │   │       └── logout.dart
│   │   └── presentation/
│   │       ├── bloc/
│   │       │   ├── auth_bloc.dart
│   │       │   ├── auth_event.dart
│   │       │   └── auth_state.dart
│   │       ├── pages/
│   │       │   ├── login_page.dart
│   │       │   └── register_page.dart
│   │       └── widgets/
│   │           └── auth_form.dart
│   ├── scenarios/
│   │   ├── data/
│   │   ├── domain/
│   │   └── presentation/
│   ├── practice/
│   │   ├── data/
│   │   ├── domain/
│   │   └── presentation/
│   └── profile/
│       ├── data/
│       ├── domain/
│       └── presentation/
├── shared/
│   ├── widgets/
│   │   ├── buttons/
│   │   ├── inputs/
│   │   ├── cards/
│   │   └── dialogs/
│   └── services/
│       ├── audio_service.dart
│       ├── storage_service.dart
│       └── connectivity_service.dart
└── injection_container.dart
```

### 3.2 Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| Files | snake_case.dart | `auth_bloc.dart` |
| Classes | PascalCase | `AuthBloc`, `UserModel` |
| Variables | camelCase | `userId`, `sessionData` |
| Constants | camelCase | `maxRetryCount` |
| Private members | _leadingUnderscore | `_userRepository` |
| Callbacks | onPrefix | `onPressed`, `onTap` |
| Booleans | is/has/can prefix | `isLoading`, `hasError` |
| Events | noun + Event | `LoginEvent`, `LogoutEvent` |
| States | noun + State | `AuthInitial`, `AuthLoading` |

### 3.3 Clean Architecture Layers

```
┌─────────────────────────────────────────────────────────────────┐
│                    FLUTTER CLEAN ARCHITECTURE                    │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────┐
│  Presentation   │  ← UI, BLoC/Cubit, Widgets
│     Layer       │
└────────┬────────┘
         │ depends on
         ▼
┌─────────────────┐
│    Domain       │  ← Entities, Use Cases, Repository Interfaces
│     Layer       │
└────────┬────────┘
         │ implemented by
         ▼
┌─────────────────┐
│     Data        │  ← Models, Data Sources, Repository Implementations
│     Layer       │
└─────────────────┘

RULES:
- Presentation depends only on Domain
- Domain has NO external dependencies
- Data implements Domain interfaces
- All dependencies point inward
```

### 3.4 BLoC Pattern

#### Event Definition

```dart
// features/auth/presentation/bloc/auth_event.dart
abstract class AuthEvent extends Equatable {
  const AuthEvent();

  @override
  List<Object?> get props => [];
}

class LoginRequested extends AuthEvent {
  final String email;
  final String password;

  const LoginRequested({
    required this.email,
    required this.password,
  });

  @override
  List<Object?> get props => [email, password];
}

class LogoutRequested extends AuthEvent {}

class AuthStatusChecked extends AuthEvent {}
```

#### State Definition

```dart
// features/auth/presentation/bloc/auth_state.dart
abstract class AuthState extends Equatable {
  const AuthState();

  @override
  List<Object?> get props => [];
}

class AuthInitial extends AuthState {}

class AuthLoading extends AuthState {}

class Authenticated extends AuthState {
  final User user;

  const Authenticated(this.user);

  @override
  List<Object?> get props => [user];
}

class Unauthenticated extends AuthState {}

class AuthError extends AuthState {
  final String message;

  const AuthError(this.message);

  @override
  List<Object?> get props => [message];
}
```

#### BLoC Implementation

```dart
// features/auth/presentation/bloc/auth_bloc.dart
class AuthBloc extends Bloc<AuthEvent, AuthState> {
  final Login login;
  final Logout logout;
  final GetCurrentUser getCurrentUser;

  AuthBloc({
    required this.login,
    required this.logout,
    required this.getCurrentUser,
  }) : super(AuthInitial()) {
    on<LoginRequested>(_onLoginRequested);
    on<LogoutRequested>(_onLogoutRequested);
    on<AuthStatusChecked>(_onAuthStatusChecked);
  }

  Future<void> _onLoginRequested(
    LoginRequested event,
    Emitter<AuthState> emit,
  ) async {
    emit(AuthLoading());

    final result = await login(
      LoginParams(
        email: event.email,
        password: event.password,
      ),
    );

    result.fold(
      (failure) => emit(AuthError(failure.message)),
      (user) => emit(Authenticated(user)),
    );
  }

  Future<void> _onLogoutRequested(
    LogoutRequested event,
    Emitter<AuthState> emit,
  ) async {
    await logout();
    emit(Unauthenticated());
  }

  Future<void> _onAuthStatusChecked(
    AuthStatusChecked event,
    Emitter<AuthState> emit,
  ) async {
    final result = await getCurrentUser(NoParams());
    result.fold(
      (failure) => emit(Unauthenticated()),
      (user) => emit(Authenticated(user)),
    );
  }
}
```

### 3.5 Use Case Pattern

```dart
// features/auth/domain/usecases/login.dart
class Login implements UseCase<User, LoginParams> {
  final AuthRepository repository;

  Login(this.repository);

  @override
  Future<Either<Failure, User>> call(LoginParams params) async {
    return await repository.login(
      email: params.email,
      password: params.password,
    );
  }
}

class LoginParams extends Equatable {
  final String email;
  final String password;

  const LoginParams({
    required this.email,
    required this.password,
  });

  @override
  List<Object?> get props => [email, password];
}
```

### 3.6 Repository Pattern

```dart
// features/auth/domain/repositories/auth_repository.dart
abstract class AuthRepository {
  Future<Either<Failure, User>> login({
    required String email,
    required String password,
  });

  Future<Either<Failure, User>> register({
    required String email,
    required String password,
    required String name,
  });

  Future<Either<Failure, void>> logout();

  Future<Either<Failure, User>> getCurrentUser();

  Future<Either<Failure, User>> updateProfile({
    String? name,
    String? avatarUrl,
  });
}
```

```dart
// features/auth/data/repositories/auth_repository_impl.dart
class AuthRepositoryImpl implements AuthRepository {
  final AuthRemoteDataSource remoteDataSource;
  final AuthLocalDataSource localDataSource;
  final NetworkInfo networkInfo;

  AuthRepositoryImpl({
    required this.remoteDataSource,
    required this.localDataSource,
    required this.networkInfo,
  });

  @override
  Future<Either<Failure, User>> login({
    required String email,
    required String password,
  }) async {
    if (!await networkInfo.isConnected) {
      return Left(NetworkFailure());
    }

    try {
      final response = await remoteDataSource.login(
        email: email,
        password: password,
      );
      await localDataSource.cacheTokens(
        accessToken: response.accessToken,
        refreshToken: response.refreshToken,
      );
      return Right(response.user);
    } on ServerException catch (e) {
      return Left(ServerFailure(e.message));
    }
  }
}
```

### 3.7 Error Handling

```dart
// core/errors/failures.dart
abstract class Failure extends Equatable {
  final String message;
  final int? code;

  const Failure({required this.message, this.code});

  @override
  List<Object?> get props => [message, code];
}

class ServerFailure extends Failure {
  const ServerFailure(String message, {int? code})
      : super(message: message, code: code);
}

class NetworkFailure extends Failure {
  const NetworkFailure() : super(message: 'No internet connection');
}

class CacheFailure extends Failure {
  const CacheFailure(String message) : super(message: message);
}

class ValidationFailure extends Failure {
  final List<ValidationError> errors;

  const ValidationFailure({
    required String message,
    required this.errors,
  }) : super(message: message);

  @override
  List<Object?> get props => [message, code, errors];
}
```

### 3.8 Dependency Injection

```dart
// injection_container.dart
final sl = GetIt.instance;

Future<void> init() async {
  // Features - Auth
  // Bloc
  sl.registerFactory(
    () => AuthBloc(
      login: sl(),
      logout: sl(),
      getCurrentUser: sl(),
    ),
  );

  // Use cases
  sl.registerLazySingleton(() => Login(sl()));
  sl.registerLazySingleton(() => Logout(sl()));
  sl.registerLazySingleton(() => GetCurrentUser(sl()));

  // Repository
  sl.registerLazySingleton<AuthRepository>(
    () => AuthRepositoryImpl(
      remoteDataSource: sl(),
      localDataSource: sl(),
      networkInfo: sl(),
    ),
  );

  // Data sources
  sl.registerLazySingleton<AuthRemoteDataSource>(
    () => AuthRemoteDataSourceImpl(client: sl()),
  );
  sl.registerLazySingleton<AuthLocalDataSource>(
    () => AuthLocalDataSourceImpl(storage: sl()),
  );

  // External
  final sharedPreferences = await SharedPreferences.getInstance();
  sl.registerLazySingleton(() => sharedPreferences);
  sl.registerLazySingleton(() => Dio());
  sl.registerLazySingleton<NetworkInfo>(() => NetworkInfoImpl(sl()));
}
```

### 3.9 Widget Guidelines

```dart
// Prefer stateless widgets when possible
class ScenarioCard extends StatelessWidget {
  final Scenario scenario;
  final VoidCallback? onTap;

  const ScenarioCard({
    super.key,
    required this.scenario,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      child: InkWell(
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                scenario.title,
                style: context.textTheme.titleMedium,
              ),
              const SizedBox(height: 8),
              Text(
                scenario.description,
                style: context.textTheme.bodyMedium,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
            ],
          ),
        ),
      ),
    );
  }
}

// Use const constructors
const SizedBox(height: 16);
const EdgeInsets.all(16);
```

### 3.10 Code Quality Tools

#### analysis_options.yaml

```yaml
include: package:flutter_lints/flutter.yaml

linter:
  rules:
    - avoid_print
    - avoid_relative_lib_imports
    - avoid_returning_null_for_void
    - avoid_slow_async_io
    - avoid_type_to_string
    - avoid_types_as_parameter_names
    - avoid_unnecessary_containers
    - avoid_web_libraries_in_flutter
    - cancel_subscriptions
    - close_sinks
    - comment_references
    - control_flow_in_finally
    - empty_statements
    - hash_and_equals
    - invariant_booleans
    - iterable_contains_unrelated_type
    - list_remove_unrelated_type
    - no_adjacent_strings_in_list
    - no_duplicate_case_values
    - no_logic_in_create_state
    - prefer_const_constructors
    - prefer_const_constructors_in_immutables
    - prefer_const_declarations
    - prefer_const_literals_to_create_immutables
    - prefer_final_fields
    - prefer_final_in_for_each
    - prefer_final_locals
    - prefer_if_null_operators
    - prefer_single_quotes
    - require_trailing_commas
    - sort_child_properties_last
    - test_types_in_equals
    - throw_in_finally
    - unnecessary_null_aware_assignments
    - unnecessary_null_in_if_null_operators
    - unnecessary_overrides
    - unnecessary_parenthesis
    - unnecessary_statements
    - unrelated_type_equality_checks
    - use_build_context_synchronously
    - use_key_in_widget_constructors
    - valid_regexps

analyzer:
  exclude:
    - "**/*.g.dart"
    - "**/*.freezed.dart"
  errors:
    invalid_annotation_target: ignore
```

---

## 4. Code Review Checklist

### 4.1 General

- [ ] Code follows naming conventions
- [ ] No commented-out code
- [ ] No hardcoded values (use constants)
- [ ] Proper error handling
- [ ] No security vulnerabilities

### 4.2 Python

- [ ] Type hints on all functions
- [ ] Docstrings on public methods
- [ ] Proper async/await usage
- [ ] No blocking I/O in async functions
- [ ] Proper exception handling

### 4.3 Flutter

- [ ] Proper BLoC pattern implementation
- [ ] No business logic in widgets
- [ ] Const constructors where possible
- [ ] Proper state management
- [ ] No memory leaks (dispose controllers)

---

## 5. Git Commit Convention

### 5.1 Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### 5.2 Types

| Type | Description |
|------|-------------|
| feat | New feature |
| fix | Bug fix |
| docs | Documentation |
| style | Formatting, no code change |
| refactor | Code refactoring |
| test | Adding tests |
| chore | Maintenance tasks |

### 5.3 Examples

```
feat(auth): add JWT refresh token support

- Implement refresh token endpoint
- Add token refresh interceptor
- Update auth service to handle token expiry

Closes #123
```

```
fix(practice): resolve audio playback issue on iOS

The audio was not playing correctly on iOS devices due to
incorrect audio session configuration.

Fixes #456
```
