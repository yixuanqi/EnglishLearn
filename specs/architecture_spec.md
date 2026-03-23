# Architecture Specification

## 1. System Overview

### 1.1 Architecture Vision
Build a scalable, maintainable, and AI-integrated mobile application with clear separation of concerns, enabling independent development and deployment of each system layer.

### 1.2 High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           CLIENT LAYER                                   │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    Flutter Mobile App                             │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │   │
│  │  │    UI       │  │   State     │  │   Local     │              │   │
│  │  │  Components │  │ Management  │  │   Storage   │              │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘              │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ HTTPS/REST
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           API LAYER                                      │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    FastAPI Backend                                │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │   │
│  │  │    Auth     │  │  Business   │  │     AI      │              │   │
│  │  │  Service    │  │   Service   │  │  Orchestrator│              │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘              │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
                    ▼               ▼               ▼
┌─────────────────────┐ ┌─────────────────┐ ┌─────────────────────┐
│   AI SERVICES LAYER  │ │ DATABASE LAYER  │ │  EXTERNAL SERVICES  │
│  ┌───────────────┐  │ │ ┌─────────────┐ │ │  ┌───────────────┐  │
│  │  LLM Service  │  │ │ │ PostgreSQL  │ │ │  │   Payment     │  │
│  │  (OpenAI)     │  │ │ │  Database   │ │ │  │   Gateway     │  │
│  └───────────────┘  │ │ └─────────────┘ │ │  └───────────────┘  │
│  ┌───────────────┐  │ │ ┌─────────────┐ │ │  ┌───────────────┐  │
│  │  TTS Service  │  │ │ │    Redis    │ │ │  │   Analytics   │  │
│  │  (Azure/Google)│  │ │ │    Cache    │ │ │  │   Service     │  │
│  └───────────────┘  │ │ └─────────────┘ │ │  └───────────────┘  │
│  ┌───────────────┐  │ └─────────────────┘ └─────────────────────┘
│  │  STT Service  │  │
│  │  (Azure/Google)│  │
│  └───────────────┘  │
│  ┌───────────────┐  │
│  │ Pronunciation │  │
│  │  Evaluation   │  │
│  └───────────────┘  │
└─────────────────────┘
```

---

## 2. Layer Definitions

### 2.1 Mobile Layer (Flutter)

#### Responsibilities
| Responsibility | Description |
|----------------|-------------|
| UI Rendering | Display all user interface components |
| State Management | Manage application state using BLoC pattern |
| Local Storage | Cache user data, preferences, and offline content |
| Audio Recording | Capture user speech for evaluation |
| Audio Playback | Play TTS-generated audio |
| API Communication | Communicate with backend via REST API |

#### Module Structure
```
lib/
├── core/
│   ├── constants/
│   ├── theme/
│   ├── router/
│   └── utils/
├── features/
│   ├── auth/
│   │   ├── data/
│   │   ├── domain/
│   │   └── presentation/
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
│   └── services/
└── main.dart
```

#### Key Components
| Component | Technology | Purpose |
|-----------|------------|---------|
| State Management | BLoC/Cubit | Predictable state transitions |
| Dependency Injection | get_it | Service locator pattern |
| Networking | Dio | HTTP client with interceptors |
| Local Storage | Hive/SharedPreferences | Offline data persistence |
| Audio | just_audio + flutter_sound | Recording and playback |
| Navigation | go_router | Declarative routing |

---

### 2.2 API Layer (FastAPI)

#### Responsibilities
| Responsibility | Description |
|----------------|-------------|
| Authentication | JWT token generation and validation |
| Authorization | Role-based access control |
| Request Validation | Pydantic model validation |
| Business Logic | Core application logic |
| AI Orchestration | Coordinate AI service calls |
| Data Persistence | Database operations |
| Rate Limiting | Prevent API abuse |
| Logging | Structured request/response logging |

#### Module Structure
```
app/
├── core/
│   ├── config.py
│   ├── security.py
│   ├── exceptions.py
│   └── dependencies.py
├── api/
│   ├── v1/
│   │   ├── endpoints/
│   │   │   ├── auth.py
│   │   │   ├── scenarios.py
│   │   │   ├── dialogues.py
│   │   │   ├── practice.py
│   │   │   ├── evaluation.py
│   │   │   ├── reports.py
│   │   │   └── payments.py
│   │   └── router.py
│   └── deps.py
├── models/
│   ├── user.py
│   ├── scenario.py
│   ├── dialogue.py
│   ├── practice.py
│   └── payment.py
├── schemas/
│   ├── user.py
│   ├── scenario.py
│   ├── dialogue.py
│   ├── practice.py
│   └── payment.py
├── services/
│   ├── auth_service.py
│   ├── scenario_service.py
│   ├── dialogue_service.py
│   ├── practice_service.py
│   ├── evaluation_service.py
│   └── payment_service.py
├── ai/
│   ├── llm_client.py
│   ├── tts_client.py
│   ├── stt_client.py
│   └── pronunciation_evaluator.py
├── repositories/
│   ├── user_repo.py
│   ├── scenario_repo.py
│   └── practice_repo.py
├── utils/
│   ├── cache.py
│   └── logger.py
└── main.py
```

#### Key Components
| Component | Technology | Purpose |
|-----------|------------|---------|
| Web Framework | FastAPI | Async API development |
| ORM | SQLAlchemy 2.0 | Database operations |
| Validation | Pydantic v2 | Request/response validation |
| Authentication | python-jose | JWT handling |
| Cache | Redis + aioredis | Response caching |
| Task Queue | Celery | Background task processing |
| HTTP Client | httpx | External API calls |

---

### 2.3 AI Services Layer

#### Responsibilities
| Service | Responsibility |
|---------|----------------|
| LLM Service | Generate contextual dialogues, AI responses |
| TTS Service | Convert text to natural speech audio |
| STT Service | Transcribe user speech to text |
| Pronunciation Evaluation | Score pronunciation accuracy |

#### Service Interfaces

```python
class LLMServiceInterface:
    async def generate_dialogue(self, scenario: ScenarioContext) -> Dialogue
    async def generate_response(self, context: ConversationContext) -> str
    async def evaluate_response(self, expected: str, actual: str) -> EvaluationResult

class TTSServiceInterface:
    async def synthesize(self, text: str, voice: VoiceConfig) -> AudioData
    async def get_available_voices(self) -> List[Voice]

class STTServiceInterface:
    async def transcribe(self, audio: AudioData) -> TranscriptionResult

class PronunciationEvaluatorInterface:
    async def evaluate(self, audio: AudioData, reference: str) -> PronunciationResult
```

#### AI Service Configuration

| Service | Provider | Model/API | Fallback |
|---------|----------|-----------|----------|
| LLM | OpenAI | GPT-4 / GPT-3.5-turbo | Azure OpenAI |
| TTS | Azure Cognitive Services | Neural voices | Google TTS |
| STT | Azure Cognitive Services | Speech-to-Text | Google STT |
| Pronunciation | Azure Speech | Pronunciation Assessment | Custom model |

---

### 2.4 Database Layer

#### Responsibilities
| Responsibility | Description |
|----------------|-------------|
| Data Persistence | Store all application data |
| Data Integrity | Enforce constraints and relations |
| Query Optimization | Indexes and query planning |
| Caching | Redis for frequently accessed data |

#### Database Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    PostgreSQL                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │   users     │  │  scenarios  │  │  dialogues  │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │  practice_  │  │   speech_   │  │  payments   │     │
│  │  sessions   │  │   results   │  │             │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                      Redis                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │   Session   │  │    API      │  │    AI       │     │
│  │    Cache    │  │   Response  │  │   Result    │     │
│  │             │  │    Cache    │  │   Cache     │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
└─────────────────────────────────────────────────────────┘
```

---

## 3. Module Boundaries

### 3.1 Module Interaction Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        MODULE BOUNDARIES                         │
└─────────────────────────────────────────────────────────────────┘

                    ┌─────────────────┐
                    │   Mobile App    │
                    │    (Flutter)    │
                    └────────┬────────┘
                             │
                             │ REST API
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                       FastAPI Backend                            │
│                                                                  │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │    Auth     │    │  Business   │    │     AI      │         │
│  │   Module    │    │   Modules   │    │   Module    │         │
│  │             │    │             │    │             │         │
│  │ - JWT       │    │ - Scenarios │    │ - LLM       │         │
│  │ - OAuth     │    │ - Dialogues │    │ - TTS       │         │
│  │ - Users     │    │ - Practice  │    │ - STT       │         │
│  └─────────────┘    │ - Reports   │    │ - Eval      │         │
│         │           │ - Payments  │    │             │         │
│         │           └──────┬──────┘    └──────┬──────┘         │
│         │                  │                  │                 │
│         │           ┌──────┴──────┐    ┌──────┴──────┐         │
│         │           │ Repository  │    │   External  │         │
│         │           │    Layer    │    │    AI APIs  │         │
│         │           └──────┬──────┘    └─────────────┘         │
│         │                  │                                    │
│         └──────────────────┼────────────────────────────────────┘
│                            │
│                            ▼
│                    ┌─────────────┐
│                    │  Database   │
│                    │ (PostgreSQL)│
│                    └─────────────┘
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Module Dependency Rules

```
┌─────────────────────────────────────────────────────────────────┐
│                    DEPENDENCY DIRECTION                          │
│                                                                  │
│   Presentation Layer (API Endpoints)                            │
│         │                                                        │
│         ▼                                                        │
│   Service Layer (Business Logic)                                │
│         │                                                        │
│         ▼                                                        │
│   Repository Layer (Data Access)                                │
│         │                                                        │
│         ▼                                                        │
│   Model Layer (Database Models)                                 │
│                                                                  │
│   RULES:                                                         │
│   - Upper layers depend on lower layers                         │
│   - Lower layers NEVER depend on upper layers                   │
│   - Cross-cutting concerns (auth, logging) are horizontal       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 3.3 Module Communication Patterns

| From | To | Communication | Format |
|------|-----|---------------|--------|
| Mobile | API | REST | JSON |
| API | AI Services | HTTP/gRPC | JSON/Protobuf |
| API | Database | SQL | - |
| API | Cache | Redis Protocol | - |
| Services | Repository | Python Objects | - |
| Repository | Models | SQLAlchemy ORM | - |

---

## 4. Service Responsibilities

### 4.1 Auth Service

| Method | Description |
|--------|-------------|
| `register(email, password)` | Create new user account |
| `login(email, password)` | Authenticate and return JWT |
| `refresh_token(token)` | Refresh access token |
| `logout(token)` | Invalidate token |
| `get_current_user(token)` | Retrieve user from token |
| `update_profile(user_id, data)` | Update user profile |

### 4.2 Scenario Service

| Method | Description |
|--------|-------------|
| `list_scenarios(filters)` | Get paginated scenario list |
| `get_scenario(scenario_id)` | Get scenario details |
| `get_categories()` | Get scenario categories |
| `create_custom_scenario(user_id, data)` | Create custom scenario (premium) |

### 4.3 Dialogue Service

| Method | Description |
|--------|-------------|
| `generate_dialogue(scenario_id)` | Generate new dialogue |
| `get_dialogue(dialogue_id)` | Retrieve stored dialogue |
| `generate_next_response(context)` | Get AI response in practice |

### 4.4 Practice Service

| Method | Description |
|--------|-------------|
| `start_session(user_id, dialogue_id)` | Initialize practice session |
| `submit_speech(session_id, audio)` | Process user speech |
| `get_session_result(session_id)` | Get session summary |
| `list_user_sessions(user_id)` | Get practice history |

### 4.5 Evaluation Service

| Method | Description |
|--------|-------------|
| `evaluate_pronunciation(audio, reference)` | Basic evaluation |
| `evaluate_detailed(audio, reference)` | Advanced evaluation (premium) |
| `get_evaluation_history(user_id)` | Get past evaluations |

### 4.6 Report Service

| Method | Description |
|--------|-------------|
| `generate_weekly_report(user_id)` | Weekly progress report |
| `generate_monthly_report(user_id)` | Monthly progress report |
| `get_learning_stats(user_id)` | Aggregate statistics |

### 4.7 Payment Service

| Method | Description |
|--------|-------------|
| `create_subscription(user_id, plan)` | Create subscription |
| `cancel_subscription(user_id)` | Cancel subscription |
| `verify_payment(payment_id)` | Verify payment status |
| `get_subscription_status(user_id)` | Check premium status |

---

## 5. Data Flow Diagrams

### 5.1 Practice Session Data Flow

```
┌──────────────────────────────────────────────────────────────────┐
│                  PRACTICE SESSION DATA FLOW                       │
└──────────────────────────────────────────────────────────────────┘

User                Mobile App          API Backend         AI Services
  │                     │                    │                    │
  │  1. Select Scenario │                    │                    │
  ├────────────────────▶│                    │                    │
  │                     │  2. Request        │                    │
  │                     │    Dialogue        │                    │
  │                     ├───────────────────▶│                    │
  │                     │                    │  3. Generate       │
  │                     │                    │    Dialogue        │
  │                     │                    ├───────────────────▶│
  │                     │                    │◀───────────────────┤
  │                     │                    │  4. Dialogue Data  │
  │                     │◀───────────────────┤                    │
  │                     │  5. Dialogue       │                    │
  │                     │    + Session ID    │                    │
  │                     │                    │                    │
  │  6. AI Speaks       │                    │                    │
  │◀────────────────────┤  7. Request TTS    │                    │
  │                     ├───────────────────▶│                    │
  │                     │                    ├───────────────────▶│
  │                     │                    │◀───────────────────┤
  │                     │◀───────────────────┤                    │
  │                     │  8. Audio URL      │                    │
  │                     │                    │                    │
  │  9. User Speaks     │                    │                    │
  ├────────────────────▶│                    │                    │
  │                     │  10. Submit Audio  │                    │
  │                     ├───────────────────▶│                    │
  │                     │                    │  11. STT           │
  │                     │                    ├───────────────────▶│
  │                     │                    │◀───────────────────┤
  │                     │                    │  12. Transcription │
  │                     │                    │  13. Evaluate      │
  │                     │                    ├───────────────────▶│
  │                     │                    │◀───────────────────┤
  │                     │                    │  14. Score         │
  │                     │◀───────────────────┤                    │
  │                     │  15. Result        │                    │
  │◀────────────────────┤                    │                    │
  │  16. Show Score     │                    │                    │
  │                     │                    │                    │
  │        ... Loop for each dialogue turn ...                    │
  │                     │                    │                    │
  │  17. End Session    │                    │                    │
  ├────────────────────▶│  18. Save Session  │                    │
  │                     ├───────────────────▶│                    │
  │                     │◀───────────────────┤                    │
  │  19. Summary        │  19. Summary       │                    │
  │◀────────────────────┤                    │                    │
```

### 5.2 Authentication Flow

```
┌──────────────────────────────────────────────────────────────────┐
│                   AUTHENTICATION FLOW                             │
└──────────────────────────────────────────────────────────────────┘

User                Mobile App          API Backend         Database
  │                     │                    │                    │
  │  1. Login Request   │                    │                    │
  │    (email, pwd)     │                    │                    │
  ├────────────────────▶│                    │                    │
  │                     │  2. POST /auth/login                   │
  │                     ├───────────────────▶│                    │
  │                     │                    │  3. Query User     │
  │                     │                    ├───────────────────▶│
  │                     │                    │◀───────────────────┤
  │                     │                    │  4. User Data      │
  │                     │                    │  5. Verify Pwd     │
  │                     │                    │  6. Generate JWT   │
  │                     │◀───────────────────┤                    │
  │                     │  7. Access Token   │                    │
  │                     │    + Refresh Token │                    │
  │◀────────────────────┤                    │                    │
  │  8. Store Tokens    │                    │                    │
  │                     │                    │                    │
  │  9. API Request     │                    │                    │
  │    (with token)     │                    │                    │
  ├────────────────────▶│  10. API Call      │                    │
  │                     │    + Bearer Token  │                    │
  │                     ├───────────────────▶│                    │
  │                     │                    │  11. Validate JWT  │
  │                     │                    │  12. Process Req   │
  │                     │◀───────────────────┤                    │
  │                     │  13. Response      │                    │
  │◀────────────────────┤                    │                    │
```

---

## 6. Scalability Considerations

### 6.1 Horizontal Scaling Strategy

```
┌─────────────────────────────────────────────────────────────────┐
│                    HORIZONTAL SCALING                            │
└─────────────────────────────────────────────────────────────────┘

                    ┌─────────────────┐
                    │   Load Balancer │
                    │      (Nginx)    │
                    └────────┬────────┘
                             │
            ┌────────────────┼────────────────┐
            │                │                │
            ▼                ▼                ▼
    ┌───────────────┐ ┌───────────────┐ ┌───────────────┐
    │  API Server 1 │ │  API Server 2 │ │  API Server N │
    │   (FastAPI)   │ │   (FastAPI)   │ │   (FastAPI)   │
    └───────────────┘ └───────────────┘ └───────────────┘
            │                │                │
            └────────────────┼────────────────┘
                             │
                    ┌────────┴────────┐
                    │   PostgreSQL    │
                    │   (Primary +    │
                    │    Replicas)    │
                    └─────────────────┘
```

### 6.2 Caching Strategy

| Cache Type | Location | TTL | Use Case |
|------------|----------|-----|----------|
| Session Cache | Redis | 24h | User session data |
| API Response Cache | Redis | 5-60min | Scenario list, static content |
| AI Result Cache | Redis | 7 days | Generated dialogues, TTS audio |
| Local Cache | Mobile | 1-24h | User preferences, cached audio |

### 6.3 Database Scaling

| Strategy | Implementation |
|----------|----------------|
| Read Replicas | Route read queries to replicas |
| Connection Pooling | PgBouncer for connection management |
| Partitioning | Partition practice_sessions by user_id |
| Indexing | Optimized indexes for common queries |

---

## 7. Error Handling Architecture

### 7.1 Error Categories

| Category | HTTP Status | Example |
|----------|-------------|---------|
| Validation Error | 400 | Invalid request parameters |
| Authentication Error | 401 | Invalid/expired token |
| Authorization Error | 403 | Insufficient permissions |
| Not Found | 404 | Resource not found |
| Conflict | 409 | Duplicate resource |
| Rate Limit | 429 | Too many requests |
| AI Service Error | 502 | External AI service failure |
| Internal Error | 500 | Unexpected server error |

### 7.2 Error Response Format

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request parameters",
    "details": [
      {
        "field": "email",
        "message": "Invalid email format"
      }
    ],
    "request_id": "req_abc123"
  }
}
```

### 7.3 AI Service Fallback Strategy

```
┌─────────────────────────────────────────────────────────────────┐
│                    AI SERVICE FALLBACK                           │
└─────────────────────────────────────────────────────────────────┘

Primary Service Failure
         │
         ▼
┌─────────────────┐
│ Retry (3x with  │
│ exponential     │
│ backoff)        │
└────────┬────────┘
         │
         ▼
    ┌────────┐
    │ Failed?│
    └────┬───┘
         │
    Yes  │
         ▼
┌─────────────────┐
│ Switch to       │
│ Fallback Service│
└────────┬────────┘
         │
         ▼
    ┌────────┐
    │ Failed?│
    └────┬───┘
         │
    Yes  │
         ▼
┌─────────────────┐
│ Return Cached   │
│ Response or     │
│ Graceful Error  │
└─────────────────┘
```

---

## 8. Security Architecture

### 8.1 Security Layers

```
┌─────────────────────────────────────────────────────────────────┐
│                    SECURITY LAYERS                               │
└─────────────────────────────────────────────────────────────────┘

Layer 1: Transport Security
├── HTTPS (TLS 1.3)
├── Certificate Pinning (Mobile)
└── Secure WebSocket

Layer 2: Authentication
├── JWT Access Tokens (15 min expiry)
├── Refresh Tokens (7 days expiry)
└── OAuth 2.0 (Google, Apple)

Layer 3: Authorization
├── Role-Based Access Control (RBAC)
├── Resource-Level Permissions
└── Premium Feature Gates

Layer 4: Input Validation
├── Request Schema Validation
├── SQL Injection Prevention
└── XSS Prevention

Layer 5: Rate Limiting
├── IP-Based Limits
├── User-Based Limits
└── Endpoint-Specific Limits
```

### 8.2 Data Protection

| Data Type | Protection |
|-----------|------------|
| Passwords | bcrypt hashing |
| PII | Encrypted at rest |
| Audio Files | Encrypted storage, auto-delete after processing |
| Tokens | Secure storage on device |
| API Keys | Environment variables, secrets manager |

---

## 9. Monitoring & Observability

### 9.1 Monitoring Stack

| Component | Tool | Purpose |
|-----------|------|---------|
| Metrics | Prometheus | System and application metrics |
| Logging | ELK Stack | Centralized log management |
| Tracing | Jaeger | Distributed tracing |
| Alerting | Alertmanager | Alert routing and notification |
| Dashboard | Grafana | Visualization |

### 9.2 Key Metrics

| Metric | Alert Threshold |
|--------|-----------------|
| API Response Time (p95) | > 1s |
| Error Rate | > 1% |
| Database Connections | > 80% pool |
| AI Service Latency | > 5s |
| Memory Usage | > 85% |
| CPU Usage | > 80% |

---

## 10. Technology Stack Summary

### 10.1 Mobile App

| Component | Technology |
|-----------|------------|
| Framework | Flutter 3.x |
| Language | Dart 3.x |
| State Management | BLoC/Cubit |
| HTTP Client | Dio |
| Local Storage | Hive, SharedPreferences |
| Audio | just_audio, flutter_sound |
| Navigation | go_router |

### 10.2 Backend

| Component | Technology |
|-----------|------------|
| Framework | FastAPI |
| Language | Python 3.11+ |
| ORM | SQLAlchemy 2.0 |
| Validation | Pydantic v2 |
| Authentication | python-jose |
| Cache | Redis |
| Task Queue | Celery |

### 10.3 Database

| Component | Technology |
|-----------|------------|
| Primary Database | PostgreSQL 15+ |
| Cache | Redis 7+ |
| Connection Pool | PgBouncer |

### 10.4 AI Services

| Service | Primary | Fallback |
|---------|---------|----------|
| LLM | OpenAI GPT-4 | Azure OpenAI |
| TTS | Azure Speech | Google Cloud TTS |
| STT | Azure Speech | Google Cloud STT |
| Pronunciation | Azure Speech | Custom Model |

### 10.5 Infrastructure

| Component | Technology |
|-----------|------------|
| Container | Docker |
| Orchestration | Docker Compose (dev) / Kubernetes (prod) |
| Reverse Proxy | Nginx |
| SSL | Let's Encrypt |
| CI/CD | GitHub Actions |
