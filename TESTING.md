# Testing Guide

This guide explains how to run tests for the English Learning application.

## Backend Tests (Python/Pytest)

### Prerequisites

```bash
cd backend
pip install pytest pytest-asyncio pytest-cov httpx aiosqlite
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html --cov-report=term

# Run specific test file
pytest tests/integration/test_api/test_auth_endpoints.py

# Run specific test
pytest tests/integration/test_api/test_auth_endpoints.py::TestAuthEndpoints::test_register_success

# Run with verbose output
pytest -v

# Run only integration tests
pytest tests/integration/

# Run tests matching a pattern
pytest -k "login"

# Run tests with markers
pytest -m "not slow"
```

### Test Structure

```
tests/
├── conftest.py                 # Shared fixtures and configuration
├── integration/
│   └── test_api/
│       ├── test_auth_endpoints.py
│       ├── test_scenario_endpoints.py
│       ├── test_practice_endpoints.py
│       └── test_evaluation_endpoints.py
```

### Coverage Targets

- Unit Tests: 90%+
- Integration Tests: 80%+

## Flutter Tests

### Prerequisites

```bash
cd mobile_app
flutter pub get
flutter pub run build_runner build
```

### Running Tests

```bash
# Run all tests
flutter test

# Run with coverage
flutter test --coverage

# Run specific test file
flutter test test/presentation/pages/login/login_page_test.dart

# Run specific test
flutter test test/presentation/pages/login/login_page_test.dart --name "should display email and password fields"

# Run with verbose output
flutter test --verbose

# Run only widget tests
flutter test test/presentation/pages/

# Run only unit tests
flutter test test/unit/
```

### Test Structure

```
test/
└── presentation/
    └── pages/
        ├── login/
        │   └── login_page_test.dart
        ├── scenario/
        │   └── scenario_list_page_test.dart
        └── practice/
            └── practice_page_test.dart
```

### Coverage Targets

- Widget Tests: 70%+

## Test Fixtures

### Backend Fixtures (conftest.py)

- `db_session`: In-memory SQLite database session
- `client`: HTTP client for API testing
- `mock_user`: Mock user data
- `auth_headers`: Authentication headers with JWT token
- `mock_scenario`: Mock scenario data

### Flutter Mocks

Use `mockito` package for mocking:
```dart
@GenerateMocks([ApiService, AuthService])
import 'login_page_test.mocks.dart';
```

## Continuous Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install pytest pytest-asyncio pytest-cov
      - name: Run tests
        run: |
          cd backend
          pytest --cov=app --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v2

  flutter-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: subosito/flutter-action@v2
        with:
          flutter-version: '3.16.0'
      - name: Install dependencies
        run: |
          cd mobile_app
          flutter pub get
          flutter pub run build_runner build
      - name: Run tests
        run: |
          cd mobile_app
          flutter test --coverage
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## Best Practices

### Backend Testing

1. Use async/await for all async operations
2. Clean up database after each test
3. Mock external services (AI, payment providers)
4. Test both success and failure scenarios
5. Use descriptive test names

### Flutter Testing

1. Use `pumpAndSettle()` for async operations
2. Mock all network calls
3. Test user interactions (taps, inputs)
4. Verify UI state changes
5. Test error handling

## Troubleshooting

### Backend Tests

**Issue: Database connection error**
```bash
# Ensure aiosqlite is installed
pip install aiosqlite
```

**Issue: Import errors**
```bash
# Install all dependencies
pip install -r requirements.txt
```

### Flutter Tests

**Issue: Mock generation errors**
```bash
# Regenerate mocks
flutter pub run build_runner build --delete-conflicting-outputs
```

**Issue: Widget not found**
```bash
# Use pumpAndSettle() to wait for widgets to render
await tester.pumpAndSettle();
```

## Test Reports

### Backend Coverage Report

```bash
pytest --cov=app --cov-report=html
# Open htmlcov/index.html in browser
```

### Flutter Coverage Report

```bash
flutter test --coverage
# Open coverage/index.html in browser
```
