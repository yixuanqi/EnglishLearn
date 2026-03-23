# Database Schema Specification

## 1. Overview

### 1.1 Database Technology
- **Primary Database**: PostgreSQL 15+
- **Cache Layer**: Redis 7+
- **Connection Pool**: PgBouncer

### 1.2 Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| Tables | snake_case, plural | `users`, `practice_sessions` |
| Columns | snake_case | `created_at`, `user_id` |
| Primary Keys | `id` | `id UUID PRIMARY KEY` |
| Foreign Keys | `{table}_id` | `user_id`, `scenario_id` |
| Indexes | `idx_{table}_{columns}` | `idx_users_email` |
| Constraints | `fk_{table}_{column}` | `fk_sessions_user_id` |

### 1.3 Common Columns

All tables include these standard columns:

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key, auto-generated |
| `created_at` | TIMESTAMP WITH TIME ZONE | Record creation time |
| `updated_at` | TIMESTAMP WITH TIME ZONE | Last update time |

---

## 2. Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ENTITY RELATIONSHIP DIAGRAM                        │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│    users    │       │  scenarios  │       │  dialogues  │
├─────────────┤       ├─────────────┤       ├─────────────┤
│ id (PK)     │       │ id (PK)     │       │ id (PK)     │
│ email       │       │ title       │       │ scenario_id │──┐
│ name        │       │ category    │       │ content     │  │
│ ...         │       │ ...         │       │ ...         │  │
└──────┬──────┘       └──────┬──────┘       └─────────────┘  │
       │                     │                               │
       │                     │                               │
       │                     └───────────────────────────────┘
       │
       │
       ▼
┌─────────────────────┐       ┌─────────────────────┐
│  practice_sessions  │       │   speech_results    │
├─────────────────────┤       ├─────────────────────┤
│ id (PK)             │       │ id (PK)             │
│ user_id (FK)        │──────▶│ session_id (FK)     │
│ dialogue_id (FK)    │       │ transcription       │
│ status              │       │ pronunciation_score │
│ ...                 │       │ ...                 │
└─────────────────────┘       └─────────────────────┘

┌─────────────────────┐
│     payments        │
├─────────────────────┤
│ id (PK)             │
│ user_id (FK)        │
│ amount              │
│ status              │
│ ...                 │
└─────────────────────┘
```

---

## 3. Table Definitions

### 3.1 users

Stores user account information and profile data.

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(100) NOT NULL,
    avatar_url TEXT,
    english_level VARCHAR(20) DEFAULT 'intermediate',
    subscription_plan VARCHAR(30) DEFAULT 'free',
    subscription_expires_at TIMESTAMP WITH TIME ZONE,
    stripe_customer_id VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    is_email_verified BOOLEAN DEFAULT false,
    last_login_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT uq_users_email UNIQUE (email),
    CONSTRAINT chk_english_level CHECK (english_level IN ('beginner', 'intermediate', 'advanced')),
    CONSTRAINT chk_subscription_plan CHECK (subscription_plan IN ('free', 'premium_monthly', 'premium_annual'))
);
```

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | UUID | NO | gen_random_uuid() | Primary key |
| email | VARCHAR(255) | NO | - | User email (unique) |
| password_hash | VARCHAR(255) | NO | - | Bcrypt hashed password |
| name | VARCHAR(100) | NO | - | Display name |
| avatar_url | TEXT | YES | NULL | Profile image URL |
| english_level | VARCHAR(20) | NO | 'intermediate' | Self-assessed English level |
| subscription_plan | VARCHAR(30) | NO | 'free' | Current subscription plan |
| subscription_expires_at | TIMESTAMPTZ | YES | NULL | Subscription expiry date |
| stripe_customer_id | VARCHAR(255) | YES | NULL | Stripe customer ID |
| is_active | BOOLEAN | NO | true | Account active status |
| is_email_verified | BOOLEAN | NO | false | Email verification status |
| last_login_at | TIMESTAMPTZ | YES | NULL | Last login timestamp |
| created_at | TIMESTAMPTZ | NO | CURRENT_TIMESTAMP | Record creation time |
| updated_at | TIMESTAMPTZ | NO | CURRENT_TIMESTAMP | Last update time |

**Indexes:**

```sql
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_subscription_plan ON users(subscription_plan);
CREATE INDEX idx_users_stripe_customer_id ON users(stripe_customer_id);
```

---

### 3.2 scenarios

Stores practice scenario templates.

```sql
CREATE TABLE scenarios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    category VARCHAR(30) NOT NULL,
    difficulty VARCHAR(20) NOT NULL DEFAULT 'intermediate',
    context TEXT NOT NULL,
    user_role VARCHAR(200) NOT NULL,
    ai_role VARCHAR(200) NOT NULL,
    key_vocabulary JSONB DEFAULT '[]',
    tips JSONB DEFAULT '[]',
    estimated_duration INTEGER NOT NULL DEFAULT 10,
    is_premium BOOLEAN DEFAULT false,
    is_active BOOLEAN DEFAULT true,
    thumbnail_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT chk_category CHECK (category IN ('exhibition', 'technical', 'business', 'daily_life')),
    CONSTRAINT chk_difficulty CHECK (difficulty IN ('beginner', 'intermediate', 'advanced'))
);
```

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | UUID | NO | gen_random_uuid() | Primary key |
| title | VARCHAR(200) | NO | - | Scenario title |
| description | TEXT | NO | - | Brief description |
| category | VARCHAR(30) | NO | - | Scenario category |
| difficulty | VARCHAR(20) | NO | 'intermediate' | Difficulty level |
| context | TEXT | NO | - | Detailed scenario context |
| user_role | VARCHAR(200) | NO | - | User's role in scenario |
| ai_role | VARCHAR(200) | NO | - | AI's role in scenario |
| key_vocabulary | JSONB | NO | '[]' | Key vocabulary words |
| tips | JSONB | NO | '[]' | Practice tips |
| estimated_duration | INTEGER | NO | 10 | Estimated minutes |
| is_premium | BOOLEAN | NO | false | Premium-only flag |
| is_active | BOOLEAN | NO | true | Active status |
| thumbnail_url | TEXT | YES | NULL | Thumbnail image URL |
| created_at | TIMESTAMPTZ | NO | CURRENT_TIMESTAMP | Record creation time |
| updated_at | TIMESTAMPTZ | NO | CURRENT_TIMESTAMP | Last update time |

**Indexes:**

```sql
CREATE INDEX idx_scenarios_category ON scenarios(category);
CREATE INDEX idx_scenarios_difficulty ON scenarios(difficulty);
CREATE INDEX idx_scenarios_is_premium ON scenarios(is_premium);
CREATE INDEX idx_scenarios_is_active ON scenarios(is_active);
```

**JSONB Structure:**

```json
// key_vocabulary
[
    {
        "word": "exhibition",
        "definition": "A public display of works of art or items of interest",
        "example": "We have a booth at the optics exhibition."
    }
]

// tips
[
    "Speak clearly and at a moderate pace",
    "Use formal language for business contexts"
]
```

---

### 3.3 dialogues

Stores generated dialogue content for scenarios.

```sql
CREATE TABLE dialogues (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scenario_id UUID NOT NULL REFERENCES scenarios(id) ON DELETE CASCADE,
    variation INTEGER DEFAULT 1,
    content JSONB NOT NULL,
    generated_by VARCHAR(50) DEFAULT 'openai',
    generation_params JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT uq_dialogues_scenario_variation UNIQUE (scenario_id, variation),
    CONSTRAINT chk_variation CHECK (variation >= 1 AND variation <= 10)
);
```

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | UUID | NO | gen_random_uuid() | Primary key |
| scenario_id | UUID | NO | - | Foreign key to scenarios |
| variation | INTEGER | NO | 1 | Dialogue variation number |
| content | JSONB | NO | - | Dialogue lines |
| generated_by | VARCHAR(50) | NO | 'openai' | AI provider used |
| generation_params | JSONB | NO | '{}' | Generation parameters |
| created_at | TIMESTAMPTZ | NO | CURRENT_TIMESTAMP | Record creation time |
| updated_at | TIMESTAMPTZ | NO | CURRENT_TIMESTAMP | Last update time |

**Indexes:**

```sql
CREATE INDEX idx_dialogues_scenario_id ON dialogues(scenario_id);
```

**JSONB Structure (content):**

```json
{
    "lines": [
        {
            "id": 1,
            "speaker": "ai",
            "text": "Good morning! Welcome to our booth at the optics exhibition.",
            "translation": "早上好！欢迎来到我们在光学展览会的展位。"
        },
        {
            "id": 2,
            "speaker": "user",
            "text": "Thank you. I'm interested in your new laser products.",
            "translation": "谢谢。我对你们的新激光产品很感兴趣。"
        }
    ],
    "total_turns": 8,
    "estimated_duration_minutes": 5
}
```

---

### 3.4 practice_sessions

Records user practice sessions.

```sql
CREATE TABLE practice_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    dialogue_id UUID NOT NULL REFERENCES dialogues(id) ON DELETE CASCADE,
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    current_turn INTEGER DEFAULT 0,
    total_turns INTEGER NOT NULL,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP WITH TIME ZONE,
    duration_seconds INTEGER,
    overall_score DECIMAL(5,2),
    average_accuracy DECIMAL(5,2),
    average_fluency DECIMAL(5,2),
    average_completeness DECIMAL(5,2),
    feedback TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT chk_session_status CHECK (status IN ('active', 'completed', 'abandoned')),
    CONSTRAINT chk_current_turn CHECK (current_turn >= 0)
);
```

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | UUID | NO | gen_random_uuid() | Primary key |
| user_id | UUID | NO | - | Foreign key to users |
| dialogue_id | UUID | NO | - | Foreign key to dialogues |
| status | VARCHAR(20) | NO | 'active' | Session status |
| current_turn | INTEGER | NO | 0 | Current dialogue turn |
| total_turns | INTEGER | NO | - | Total turns in dialogue |
| started_at | TIMESTAMPTZ | NO | CURRENT_TIMESTAMP | Session start time |
| ended_at | TIMESTAMPTZ | YES | NULL | Session end time |
| duration_seconds | INTEGER | YES | NULL | Total duration |
| overall_score | DECIMAL(5,2) | YES | NULL | Overall pronunciation score |
| average_accuracy | DECIMAL(5,2) | YES | NULL | Average accuracy score |
| average_fluency | DECIMAL(5,2) | YES | NULL | Average fluency score |
| average_completeness | DECIMAL(5,2) | YES | NULL | Average completeness score |
| feedback | TEXT | YES | NULL | AI-generated feedback |
| created_at | TIMESTAMPTZ | NO | CURRENT_TIMESTAMP | Record creation time |
| updated_at | TIMESTAMPTZ | NO | CURRENT_TIMESTAMP | Last update time |

**Indexes:**

```sql
CREATE INDEX idx_practice_sessions_user_id ON practice_sessions(user_id);
CREATE INDEX idx_practice_sessions_status ON practice_sessions(status);
CREATE INDEX idx_practice_sessions_started_at ON practice_sessions(started_at);
CREATE INDEX idx_practice_sessions_user_started ON practice_sessions(user_id, started_at DESC);
```

---

### 3.5 speech_results

Stores individual speech evaluation results within practice sessions.

```sql
CREATE TABLE speech_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES practice_sessions(id) ON DELETE CASCADE,
    turn_index INTEGER NOT NULL,
    expected_text TEXT NOT NULL,
    transcription TEXT,
    pronunciation_score DECIMAL(5,2),
    accuracy_score DECIMAL(5,2),
    fluency_score DECIMAL(5,2),
    completeness_score DECIMAL(5,2),
    word_evaluations JSONB,
    audio_url TEXT,
    audio_duration_seconds DECIMAL(5,2),
    processing_time_ms INTEGER,
    ai_response_text TEXT,
    ai_response_audio_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_speech_results_session FOREIGN KEY (session_id) REFERENCES practice_sessions(id) ON DELETE CASCADE
);
```

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | UUID | NO | gen_random_uuid() | Primary key |
| session_id | UUID | NO | - | Foreign key to practice_sessions |
| turn_index | INTEGER | NO | - | Turn number in session |
| expected_text | TEXT | NO | - | Expected dialogue text |
| transcription | TEXT | YES | NULL | STT transcription |
| pronunciation_score | DECIMAL(5,2) | YES | NULL | Overall score (0-100) |
| accuracy_score | DECIMAL(5,2) | YES | NULL | Accuracy score (0-100) |
| fluency_score | DECIMAL(5,2) | YES | NULL | Fluency score (0-100) |
| completeness_score | DECIMAL(5,2) | YES | NULL | Completeness score (0-100) |
| word_evaluations | JSONB | YES | NULL | Word-level evaluation |
| audio_url | TEXT | YES | NULL | User audio storage URL |
| audio_duration_seconds | DECIMAL(5,2) | YES | NULL | Audio duration |
| processing_time_ms | INTEGER | YES | NULL | Processing time |
| ai_response_text | TEXT | YES | NULL | AI's response text |
| ai_response_audio_url | TEXT | YES | NULL | AI response audio URL |
| created_at | TIMESTAMPTZ | NO | CURRENT_TIMESTAMP | Record creation time |

**Indexes:**

```sql
CREATE INDEX idx_speech_results_session_id ON speech_results(session_id);
CREATE INDEX idx_speech_results_session_turn ON speech_results(session_id, turn_index);
```

**JSONB Structure (word_evaluations - Premium only):**

```json
[
    {
        "word": "exhibition",
        "accuracy_score": 85.5,
        "error_type": "none",
        "phonemes": [
            {"phoneme": "IH0", "accuracy_score": 90.0},
            {"phoneme": "K", "accuracy_score": 85.0},
            {"phoneme": "S", "accuracy_score": 80.0}
        ]
    }
]
```

---

### 3.6 payments

Records payment transactions.

```sql
CREATE TABLE payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    stripe_payment_intent_id VARCHAR(255),
    stripe_subscription_id VARCHAR(255),
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    status VARCHAR(30) NOT NULL DEFAULT 'pending',
    plan_type VARCHAR(30) NOT NULL,
    billing_period VARCHAR(20),
    description TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT chk_payment_status CHECK (status IN ('pending', 'succeeded', 'failed', 'refunded', 'cancelled')),
    CONSTRAINT chk_plan_type CHECK (plan_type IN ('premium_monthly', 'premium_annual')),
    CONSTRAINT chk_billing_period CHECK (billing_period IN ('monthly', 'annual'))
);
```

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | UUID | NO | gen_random_uuid() | Primary key |
| user_id | UUID | NO | - | Foreign key to users |
| stripe_payment_intent_id | VARCHAR(255) | YES | NULL | Stripe payment intent ID |
| stripe_subscription_id | VARCHAR(255) | YES | NULL | Stripe subscription ID |
| amount | DECIMAL(10,2) | NO | - | Payment amount |
| currency | VARCHAR(3) | NO | 'USD' | Currency code |
| status | VARCHAR(30) | NO | 'pending' | Payment status |
| plan_type | VARCHAR(30) | NO | - | Subscription plan type |
| billing_period | VARCHAR(20) | YES | NULL | Billing period |
| description | TEXT | YES | NULL | Payment description |
| metadata | JSONB | NO | '{}' | Additional metadata |
| created_at | TIMESTAMPTZ | NO | CURRENT_TIMESTAMP | Record creation time |
| updated_at | TIMESTAMPTZ | NO | CURRENT_TIMESTAMP | Last update time |

**Indexes:**

```sql
CREATE INDEX idx_payments_user_id ON payments(user_id);
CREATE INDEX idx_payments_status ON payments(status);
CREATE INDEX idx_payments_stripe_payment_intent ON payments(stripe_payment_intent_id);
CREATE INDEX idx_payments_stripe_subscription ON payments(stripe_subscription_id);
CREATE INDEX idx_payments_created_at ON payments(created_at);
```

---

### 3.7 refresh_tokens

Stores JWT refresh tokens for authentication.

```sql
CREATE TABLE refresh_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    revoked BOOLEAN DEFAULT false,
    revoked_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT uq_refresh_tokens_token_hash UNIQUE (token_hash)
);
```

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | UUID | NO | gen_random_uuid() | Primary key |
| user_id | UUID | NO | - | Foreign key to users |
| token_hash | VARCHAR(255) | NO | - | Hashed refresh token |
| expires_at | TIMESTAMPTZ | NO | - | Token expiry time |
| revoked | BOOLEAN | NO | false | Revocation status |
| revoked_at | TIMESTAMPTZ | YES | NULL | Revocation timestamp |
| created_at | TIMESTAMPTZ | NO | CURRENT_TIMESTAMP | Record creation time |

**Indexes:**

```sql
CREATE INDEX idx_refresh_tokens_user_id ON refresh_tokens(user_id);
CREATE INDEX idx_refresh_tokens_expires_at ON refresh_tokens(expires_at);
```

---

### 3.8 custom_scenarios

Stores user-created custom scenarios (Premium feature).

```sql
CREATE TABLE custom_scenarios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    category VARCHAR(30) NOT NULL,
    context TEXT NOT NULL,
    user_role VARCHAR(200) NOT NULL,
    ai_role VARCHAR(200) NOT NULL,
    difficulty VARCHAR(20) DEFAULT 'intermediate',
    is_active BOOLEAN DEFAULT true,
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT chk_custom_category CHECK (category IN ('exhibition', 'technical', 'business', 'daily_life')),
    CONSTRAINT chk_custom_difficulty CHECK (difficulty IN ('beginner', 'intermediate', 'advanced'))
);
```

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | UUID | NO | gen_random_uuid() | Primary key |
| user_id | UUID | NO | - | Foreign key to users |
| title | VARCHAR(200) | NO | - | Scenario title |
| description | TEXT | YES | NULL | Brief description |
| category | VARCHAR(30) | NO | - | Scenario category |
| context | TEXT | NO | - | Detailed context |
| user_role | VARCHAR(200) | NO | - | User's role |
| ai_role | VARCHAR(200) | NO | - | AI's role |
| difficulty | VARCHAR(20) | NO | 'intermediate' | Difficulty level |
| is_active | BOOLEAN | NO | true | Active status |
| usage_count | INTEGER | NO | 0 | Times used |
| created_at | TIMESTAMPTZ | NO | CURRENT_TIMESTAMP | Record creation time |
| updated_at | TIMESTAMPTZ | NO | CURRENT_TIMESTAMP | Last update time |

**Indexes:**

```sql
CREATE INDEX idx_custom_scenarios_user_id ON custom_scenarios(user_id);
CREATE INDEX idx_custom_scenarios_category ON custom_scenarios(category);
```

---

## 4. Relationships Summary

| Relationship | Type | Description |
|--------------|------|-------------|
| users → practice_sessions | One-to-Many | A user can have many practice sessions |
| scenarios → dialogues | One-to-Many | A scenario can have multiple dialogue variations |
| dialogues → practice_sessions | One-to-Many | A dialogue can be used in many sessions |
| practice_sessions → speech_results | One-to-Many | A session has multiple speech results |
| users → payments | One-to-Many | A user can have multiple payments |
| users → refresh_tokens | One-to-Many | A user can have multiple refresh tokens |
| users → custom_scenarios | One-to-Many | A user can create custom scenarios |

---

## 5. Migration Strategy

### 5.1 Migration Files Structure

```
migrations/
├── versions/
│   ├── 001_initial_schema.py
│   ├── 002_add_custom_scenarios.py
│   └── 003_add_indexes.py
├── env.py
└── alembic.ini
```

### 5.2 Initial Migration Example

```python
# migrations/versions/001_initial_schema.py

def upgrade():
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('avatar_url', sa.Text, nullable=True),
        sa.Column('english_level', sa.String(20), default='intermediate'),
        sa.Column('subscription_plan', sa.String(30), default='free'),
        sa.Column('subscription_expires_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('stripe_customer_id', sa.String(255), nullable=True),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('is_email_verified', sa.Boolean, default=False),
        sa.Column('last_login_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
    )
    
    # Create indexes
    op.create_index('idx_users_email', 'users', ['email'])
    op.create_index('idx_users_subscription_plan', 'users', ['subscription_plan'])

def downgrade():
    op.drop_index('idx_users_subscription_plan', 'users')
    op.drop_index('idx_users_email', 'users')
    op.drop_table('users')
```

---

## 6. Data Retention Policy

| Data Type | Retention Period | Action |
|-----------|------------------|--------|
| User Audio Files | 30 days | Auto-delete after processing |
| Speech Results | 1 year | Archive to cold storage |
| Practice Sessions | 2 years | Archive to cold storage |
| Payment Records | 7 years | Keep for compliance |
| Refresh Tokens | 7 days after expiry | Auto-delete |
| Inactive Users | 3 years | Anonymize data |

---

## 7. Performance Considerations

### 7.1 Partitioning Strategy

For high-volume tables, implement partitioning:

```sql
-- Partition practice_sessions by created_at (monthly)
CREATE TABLE practice_sessions (
    id UUID,
    user_id UUID NOT NULL,
    -- ... other columns
    created_at TIMESTAMP WITH TIME ZONE NOT NULL
) PARTITION BY RANGE (created_at);

CREATE TABLE practice_sessions_2024_01 PARTITION OF practice_sessions
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE TABLE practice_sessions_2024_02 PARTITION OF practice_sessions
    FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');
```

### 7.2 Query Optimization

| Query Pattern | Optimization |
|---------------|--------------|
| User session history | Composite index on (user_id, started_at DESC) |
| Scenario filtering | Composite index on (category, difficulty, is_premium) |
| Payment lookup | Index on stripe_payment_intent_id |
| Active sessions | Partial index on status = 'active' |

### 7.3 Connection Pooling

```python
# PgBouncer configuration
[databases]
english_trainer = host=localhost port=5432 dbname=english_trainer

[pgbouncer]
pool_mode = transaction
max_client_conn = 1000
default_pool_size = 25
reserve_pool_size = 5
```

---

## 8. Backup Strategy

### 8.1 Backup Schedule

| Backup Type | Frequency | Retention |
|-------------|-----------|-----------|
| Full Backup | Daily | 30 days |
| Incremental | Hourly | 7 days |
| WAL Archiving | Continuous | 7 days |

### 8.2 Backup Commands

```bash
# Full backup
pg_dump -Fc english_trainer > backup_$(date +%Y%m%d).dump

# Point-in-time recovery setup
archive_mode = on
archive_command = 'cp %p /backup/wal/%f'
```

---

## 9. Redis Cache Schema

### 9.1 Cache Keys Structure

| Key Pattern | TTL | Description |
|-------------|-----|-------------|
| `user:{user_id}:profile` | 1 hour | User profile cache |
| `scenario:list:{category}` | 5 minutes | Scenario list cache |
| `dialogue:{dialogue_id}` | 24 hours | Generated dialogue cache |
| `tts:{text_hash}:{voice}` | 7 days | TTS audio cache |
| `session:{session_id}` | 2 hours | Active session data |
| `rate_limit:{ip}:{endpoint}` | 1 minute | Rate limiting counter |

### 9.2 Cache Invalidation Rules

| Event | Invalidation |
|-------|--------------|
| User profile update | `user:{user_id}:profile` |
| New scenario added | `scenario:list:*` |
| Session completed | `session:{session_id}` |
| Subscription change | `user:{user_id}:profile` |

---

## 10. SQL Query Templates

### 10.1 Common Queries

```sql
-- Get user's recent practice sessions with scores
SELECT 
    ps.id,
    s.title as scenario_title,
    ps.started_at,
    ps.duration_seconds,
    ps.overall_score,
    ps.status
FROM practice_sessions ps
JOIN dialogues d ON ps.dialogue_id = d.id
JOIN scenarios s ON d.scenario_id = s.id
WHERE ps.user_id = $1
ORDER BY ps.started_at DESC
LIMIT 10;

-- Get user's weekly statistics
SELECT 
    DATE_TRUNC('week', started_at) as week,
    COUNT(*) as sessions,
    AVG(overall_score) as avg_score,
    SUM(duration_seconds) as total_duration
FROM practice_sessions
WHERE user_id = $1
  AND started_at >= NOW() - INTERVAL '4 weeks'
  AND status = 'completed'
GROUP BY DATE_TRUNC('week', started_at)
ORDER BY week DESC;

-- Get popular scenarios
SELECT 
    s.id,
    s.title,
    s.category,
    COUNT(ps.id) as practice_count,
    AVG(ps.overall_score) as avg_score
FROM scenarios s
LEFT JOIN dialogues d ON s.id = d.scenario_id
LEFT JOIN practice_sessions ps ON d.id = ps.dialogue_id
WHERE s.is_active = true
GROUP BY s.id, s.title, s.category
ORDER BY practice_count DESC
LIMIT 20;
```
