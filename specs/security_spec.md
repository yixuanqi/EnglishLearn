# Security Specification

## 1. Overview

### 1.1 Security Principles

- **Defense in Depth**: Multiple layers of security controls
- **Least Privilege**: Users and services have minimum necessary access
- **Zero Trust**: Verify every request, regardless of source
- **Secure by Default**: Security built into all components
- **Fail Secure**: Systems fail to a secure state

### 1.2 Security Layers

```
┌─────────────────────────────────────────────────────────────────┐
│                    SECURITY LAYERS                               │
└─────────────────────────────────────────────────────────────────┘

Layer 1: Network Security
├── HTTPS/TLS 1.3
├── DDoS Protection
├── Web Application Firewall (WAF)
└── IP Whitelisting (admin endpoints)

Layer 2: Application Security
├── Input Validation
├── Output Encoding
├── SQL Injection Prevention
├── XSS Protection
└── CSRF Protection

Layer 3: Authentication & Authorization
├── JWT Tokens
├── OAuth 2.0
├── Role-Based Access Control (RBAC)
└── Multi-Factor Authentication (MFA)

Layer 4: Data Security
├── Encryption at Rest
├── Encryption in Transit
├── Data Masking
└── Secure Key Management

Layer 5: Infrastructure Security
├── Container Security
├── Network Segmentation
├── Secrets Management
└── Audit Logging
```

---

## 2. Authentication

### 2.1 JWT Token Implementation

#### Token Structure

```python
# Access Token (15 minutes expiry)
{
    "sub": "user_id",
    "email": "user@example.com",
    "role": "user",
    "subscription": "premium_monthly",
    "iat": 1234567890,
    "exp": 1234568790,
    "jti": "unique_token_id"
}

# Refresh Token (7 days expiry)
{
    "sub": "user_id",
    "type": "refresh",
    "iat": 1234567890,
    "exp": 1235172690,
    "jti": "unique_refresh_id"
}
```

#### Token Configuration

```python
# app/core/security.py

from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

class SecurityConfig:
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    JWT_ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 15
    REFRESH_TOKEN_EXPIRE_DAYS = 7
    
    # Password hashing
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    @classmethod
    def create_access_token(cls, data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(
            minutes=cls.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        to_encode.update({
            "exp": expire,
            "jti": str(uuid4())
        })
        return jwt.encode(to_encode, cls.JWT_SECRET_KEY, algorithm=cls.JWT_ALGORITHM)
    
    @classmethod
    def create_refresh_token(cls, user_id: str) -> str:
        expire = datetime.utcnow() + timedelta(
            days=cls.REFRESH_TOKEN_EXPIRE_DAYS
        )
        payload = {
            "sub": user_id,
            "type": "refresh",
            "exp": expire,
            "jti": str(uuid4())
        }
        return jwt.encode(payload, cls.JWT_SECRET_KEY, algorithm=cls.JWT_ALGORITHM)
    
    @classmethod
    def verify_token(cls, token: str) -> dict:
        try:
            payload = jwt.decode(
                token,
                cls.JWT_SECRET_KEY,
                algorithms=[cls.JWT_ALGORITHM]
            )
            return payload
        except JWTError:
            raise AuthenticationError("Invalid token")
    
    @classmethod
    def hash_password(cls, password: str) -> str:
        return cls.pwd_context.hash(password)
    
    @classmethod
    def verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        return cls.pwd_context.verify(plain_password, hashed_password)
```

### 2.2 Token Refresh Flow

```python
# app/api/v1/endpoints/auth.py

@router.post("/refresh")
async def refresh_token(
    refresh_token: str,
    db: AsyncSession = Depends(get_db)
):
    try:
        payload = SecurityConfig.verify_token(refresh_token)
        
        if payload.get("type") != "refresh":
            raise AuthenticationError("Invalid token type")
        
        # Check if refresh token is revoked
        token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
        revoked = await db.execute(
            select(RefreshToken).where(
                RefreshToken.token_hash == token_hash,
                RefreshToken.revoked == True
            )
        )
        if revoked.scalar_one_or_none():
            raise AuthenticationError("Token revoked")
        
        # Get user
        user = await db.get(User, payload["sub"])
        if not user or not user.is_active:
            raise AuthenticationError("User not found")
        
        # Create new tokens
        access_token = SecurityConfig.create_access_token({
            "sub": str(user.id),
            "email": user.email,
            "role": "user",
            "subscription": user.subscription_plan
        })
        new_refresh_token = SecurityConfig.create_refresh_token(str(user.id))
        
        # Revoke old refresh token
        await db.execute(
            update(RefreshToken)
            .where(RefreshToken.token_hash == token_hash)
            .values(revoked=True, revoked_at=datetime.utcnow())
        )
        
        # Store new refresh token
        new_token_hash = hashlib.sha256(
            new_refresh_token.encode()
        ).hexdigest()
        db.add(RefreshToken(
            user_id=user.id,
            token_hash=new_token_hash,
            expires_at=datetime.utcnow() + timedelta(days=7)
        ))
        await db.commit()
        
        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }
        
    except JWTError:
        raise AuthenticationError("Invalid refresh token")
```

### 2.3 OAuth 2.0 Integration

```python
# app/api/v1/endpoints/auth.py

from authlib.integrations.starlette_client import OAuth

oauth = OAuth()

oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)

@router.get("/google")
async def google_login(request: Request):
    redirect_uri = request.url_for('auth_callback', provider='google')
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/callback/google")
async def google_callback(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    token = await oauth.google.authorize_access_token(request)
    user_info = await oauth.google.parse_id_token(request, token)
    
    # Check if user exists
    user = await db.execute(
        select(User).where(User.email == user_info["email"])
    )
    user = user.scalar_one_or_none()
    
    if not user:
        # Create new user
        user = User(
            email=user_info["email"],
            name=user_info["name"],
            is_email_verified=True,
            is_active=True
        )
        db.add(user)
        await db.commit()
    
    # Create tokens
    access_token = SecurityConfig.create_access_token({
        "sub": str(user.id),
        "email": user.email,
        "role": "user",
        "subscription": user.subscription_plan
    })
    
    return {"access_token": access_token, "token_type": "bearer"}
```

---

## 3. Authorization

### 3.1 Role-Based Access Control (RBAC)

#### Role Definitions

```python
# app/core/security.py

from enum import Enum

class UserRole(str, Enum):
    USER = "user"
    PREMIUM = "premium"
    ADMIN = "admin"

class Permission(str, Enum):
    # Basic permissions
    READ_SCENARIOS = "read:scenarios"
    PRACTICE = "practice:sessions"
    VIEW_REPORTS = "view:reports"
    
    # Premium permissions
    ADVANCED_EVALUATION = "evaluation:advanced"
    CUSTOM_SCENARIOS = "scenarios:custom"
    UNLIMITED_PRACTICE = "practice:unlimited"
    
    # Admin permissions
    MANAGE_USERS = "manage:users"
    MANAGE_SCENARIOS = "manage:scenarios"
    VIEW_ANALYTICS = "view:analytics"

ROLE_PERMISSIONS = {
    UserRole.USER: [
        Permission.READ_SCENARIOS,
        Permission.PRACTICE,
        Permission.VIEW_REPORTS
    ],
    UserRole.PREMIUM: [
        Permission.READ_SCENARIOS,
        Permission.PRACTICE,
        Permission.VIEW_REPORTS,
        Permission.ADVANCED_EVALUATION,
        Permission.CUSTOM_SCENARIOS,
        Permission.UNLIMITED_PRACTICE
    ],
    UserRole.ADMIN: [
        Permission.READ_SCENARIOS,
        Permission.PRACTICE,
        Permission.VIEW_REPORTS,
        Permission.ADVANCED_EVALUATION,
        Permission.CUSTOM_SCENARIOS,
        Permission.UNLIMITED_PRACTICE,
        Permission.MANAGE_USERS,
        Permission.MANAGE_SCENARIOS,
        Permission.VIEW_ANALYTICS
    ]
}
```

#### Permission Check

```python
# app/core/security.py

def has_permission(user: User, permission: Permission) -> bool:
    user_role = UserRole(user.subscription_plan)
    if user_role == UserRole.ADMIN:
        return True
    return permission in ROLE_PERMISSIONS.get(user_role, [])

def require_permission(permission: Permission):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user: User = Depends(get_current_user), **kwargs):
            if not has_permission(current_user, permission):
                raise AuthorizationError(
                    f"Permission required: {permission.value}"
                )
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator

# Usage example
@router.post("/evaluation/advanced")
@require_permission(Permission.ADVANCED_EVALUATION)
async def advanced_evaluation(
    request: AdvancedEvaluationRequest,
    current_user: User = Depends(get_current_user)
):
    ...
```

### 3.2 Resource-Based Authorization

```python
# app/core/security.py

async def check_resource_ownership(
    user: User,
    resource_type: str,
    resource_id: str,
    db: AsyncSession
) -> bool:
    if user.subscription_plan == "admin":
        return True
    
    if resource_type == "practice_session":
        session = await db.get(PracticeSession, resource_id)
        return session and session.user_id == user.id
    
    if resource_type == "custom_scenario":
        scenario = await db.get(CustomScenario, resource_id)
        return scenario and scenario.user_id == user.id
    
    return False

# Usage
@router.get("/sessions/{session_id}")
async def get_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if not await check_resource_ownership(
        current_user, "practice_session", session_id, db
    ):
        raise AuthorizationError("Access denied")
    ...
```

---

## 4. Rate Limiting

### 4.1 Rate Limiting Strategy

```python
# app/core/rate_limit.py

from fastapi import Request, HTTPException
from redis import Redis

class RateLimiter:
    def __init__(self, redis: Redis):
        self.redis = redis
    
    async def is_allowed(
        self,
        key: str,
        limit: int,
        window: int
    ) -> bool:
        current = await self.redis.incr(key)
        
        if current == 1:
            await self.redis.expire(key, window)
        
        return current <= limit
    
    async def get_remaining(
        self,
        key: str
    ) -> int:
        return await self.redis.ttl(key)

# Rate limit configuration
RATE_LIMITS = {
    "auth": {"limit": 5, "window": 60},  # 5 requests per minute
    "api": {"limit": 100, "window": 60},  # 100 requests per minute
    "evaluation": {"limit": 10, "window": 60},  # 10 evaluations per minute
    "dialogue_generation": {"limit": 5, "window": 60}  # 5 dialogues per minute
}

# Middleware
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    endpoint = request.url.path
    
    # Determine rate limit
    if "/auth/" in endpoint:
        config = RATE_LIMITS["auth"]
    elif "/evaluation/" in endpoint:
        config = RATE_LIMITS["evaluation"]
    elif "/dialogues/" in endpoint:
        config = RATE_LIMITS["dialogue_generation"]
    else:
        config = RATE_LIMITS["api"]
    
    # Get client identifier
    client_id = request.client.host
    if "Authorization" in request.headers:
        token = request.headers["Authorization"].split(" ")[1]
        payload = SecurityConfig.verify_token(token)
        client_id = payload.get("sub", client_id)
    
    key = f"rate_limit:{client_id}:{endpoint}"
    
    limiter = RateLimiter(redis_client)
    if not await limiter.is_allowed(key, config["limit"], config["window"]):
        raise HTTPException(
            status_code=429,
            detail="Too many requests",
            headers={
                "Retry-After": str(await limiter.get_remaining(key))
            }
        )
    
    response = await call_next(request)
    response.headers["X-RateLimit-Limit"] = str(config["limit"])
    response.headers["X-RateLimit-Remaining"] = str(
        config["limit"] - await redis_client.incr(key)
    )
    
    return response
```

---

## 5. Input Validation

### 5.1 Pydantic Validation

```python
# app/schemas/user.py

from pydantic import BaseModel, EmailStr, Field, validator
import re

class UserRegistration(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    name: str = Field(..., min_length=1, max_length=100)
    
    @validator('password')
    def validate_password(cls, v):
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v
    
    @validator('name')
    def validate_name(cls, v):
        if not re.match(r'^[a-zA-Z\u4e00-\u9fff\s\-]+$', v):
            raise ValueError('Name contains invalid characters')
        return v
```

### 5.2 SQL Injection Prevention

```python
# Always use parameterized queries
from sqlalchemy import select, update, delete

# GOOD - Parameterized query
async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(
        select(User).where(User.email == email)
    )
    return result.scalar_one_or_none()

# BAD - String concatenation (VULNERABLE)
async def get_user_by_email_bad(db: AsyncSession, email: str):
    query = f"SELECT * FROM users WHERE email = '{email}'"
    result = await db.execute(text(query))
    return result.scalar_one_or_none()
```

### 5.3 XSS Prevention

```python
# Output encoding
from markupsafe import escape

def sanitize_html(text: str) -> str:
    return escape(text)

# Content Security Policy headers
@app.middleware("http")
async def csp_middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "font-src 'self'; "
        "connect-src 'self'; "
        "media-src 'self'; "
        "object-src 'none'; "
        "frame-ancestors 'none';"
    )
    return response
```

---

## 6. Data Protection

### 6.1 Encryption at Rest

```python
# app/core/encryption.py

from cryptography.fernet import Fernet
import base64

class DataEncryption:
    def __init__(self, key: str):
        self.cipher = Fernet(key.encode())
    
    def encrypt(self, data: str) -> str:
        encrypted = self.cipher.encrypt(data.encode())
        return base64.b64encode(encrypted).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        decoded = base64.b64decode(encrypted_data.encode())
        decrypted = self.cipher.decrypt(decoded)
        return decrypted.decode()

# Usage
encryption = DataEncryption(os.getenv("ENCRYPTION_KEY"))

# Encrypt sensitive data before storing
user.encrypted_field = encryption.encrypt("sensitive_data")
```

### 6.2 Encryption in Transit

```python
# Force HTTPS
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

app.add_middleware(HTTPSRedirectMiddleware)

# TLS Configuration
# nginx.conf
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256';
ssl_prefer_server_ciphers off;
```

### 6.3 Secrets Management

```python
# Use environment variables or secrets manager
import os
from dotenv import load_dotenv

load_dotenv()

class Secrets:
    @staticmethod
    def get(key: str, default: str = None) -> str:
        value = os.getenv(key, default)
        if not value:
            raise ValueError(f"Secret {key} not found")
        return value
    
    @staticmethod
    def get_optional(key: str) -> Optional[str]:
        return os.getenv(key)

# Usage
DATABASE_URL = Secrets.get("DATABASE_URL")
JWT_SECRET = Secrets.get("JWT_SECRET_KEY")
```

---

## 7. API Security

### 7.1 CORS Configuration

```python
# app/main.py

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://englishspeakingtrainer.com",
        "https://www.englishspeakingtrainer.com",
        "https://app.englishspeakingtrainer.com"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-RateLimit-Limit", "X-RateLimit-Remaining"]
)
```

### 7.2 Security Headers

```python
# app/main.py

@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    
    # Security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    
    return response
```

### 7.3 API Key Validation

```python
# app/core/security.py

async def validate_api_key(api_key: str) -> bool:
    if not api_key.startswith("est_"):
        return False
    
    # Check against database or cache
    cached = await redis_client.get(f"api_key:{api_key}")
    if cached:
        return True
    
    # Database lookup
    key_record = await db.execute(
        select(APIKey).where(APIKey.key == api_key, APIKey.is_active == True)
    )
    key_record = key_record.scalar_one_or_none()
    
    if key_record:
        await redis_client.setex(
            f"api_key:{api_key}",
            3600,
            "1"
        )
        return True
    
    return False
```

---

## 8. Mobile App Security

### 8.1 Certificate Pinning

```dart
// lib/core/security/certificate_pinning.dart

import 'dart:io';
import 'package:http/http.dart' as http;

class SecureHttpClient extends http.BaseClient {
  final http.Client _inner;
  final List<String> pinnedCertificates;

  SecureHttpClient(this._inner, this.pinnedCertificates);

  @override
  Future<http.StreamedResponse> send(http.BaseRequest request) async {
    final response = await _inner.send(request);
    
    // Verify certificate
    if (response.headers.containsKey('certificate')) {
      final certificate = response.headers['certificate'];
      if (!pinnedCertificates.contains(certificate)) {
        throw SecurityException('Certificate pinning failed');
      }
    }
    
    return response;
  }
}

// Usage
final client = SecureHttpClient(
  http.Client(),
  [
    'sha256/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=',
    'sha256/BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB='
  ]
);
```

### 8.2 Secure Storage

```dart
// lib/core/security/secure_storage.dart

import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class SecureStorage {
  static const _storage = FlutterSecureStorage(
    aOptions: AndroidOptions(
      encryptedSharedPreferences: true,
    ),
    iOptions: IOSOptions(
      accessibility: KeychainAccessibility.first_unlock,
    ),
  );

  static Future<void> saveToken(String key, String value) async {
    await _storage.write(key: key, value: value);
  }

  static Future<String?> getToken(String key) async {
    return await _storage.read(key: key);
  }

  static Future<void> deleteToken(String key) async {
    await _storage.delete(key: key);
  }

  static Future<void> clearAll() async {
    await _storage.deleteAll();
  }
}
```

### 8.3 Biometric Authentication

```dart
// lib/features/auth/presentation/bloc/auth_bloc.dart

import 'package:local_auth/local_auth.dart';

class AuthBloc extends Bloc<AuthEvent, AuthState> {
  final LocalAuthentication _localAuth = LocalAuthentication();

  Future<bool> _authenticateWithBiometrics() async {
    try {
      return await _localAuth.authenticate(
        localizedReason: 'Please authenticate to access your account',
        options: const AuthenticationOptions(
          biometricOnly: true,
          stickyAuth: true,
        ),
      );
    } catch (e) {
      return false;
    }
  }
}
```

---

## 9. Audit Logging

### 9.1 Audit Log Structure

```python
# app/models/audit_log.py

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False)
    resource_type = Column(String(50), nullable=False)
    resource_id = Column(String(255), nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    status = Column(String(20), nullable=False)
    details = Column(JSONB, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
```

### 9.2 Audit Middleware

```python
# app/core/audit.py

async def log_audit(
    action: str,
    resource_type: str,
    resource_id: str = None,
    user: User = None,
    status: str = "success",
    details: dict = None
):
    log = AuditLog(
        user_id=user.id if user else None,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        ip_address=request.client.host if request else None,
        user_agent=request.headers.get("user-agent") if request else None,
        status=status,
        details=details
    )
    db.add(log)
    await db.commit()
```

---

## 10. Security Testing

### 10.1 Automated Security Scanning

```yaml
# .github/workflows/security.yml

name: Security Scan

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  dependency-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          format: 'sarif'
          output: 'trivy-results.sarif'
      
      - name: Upload Trivy results
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'

  sast-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Run Bandit
        run: |
          pip install bandit
          bandit -r app/ -f json -o bandit-report.json
      
      - name: Upload Bandit results
        uses: actions/upload-artifact@v3
        with:
          name: bandit-report
          path: bandit-report.json
```

### 10.2 Penetration Testing Checklist

- [ ] SQL Injection testing
- [ ] XSS vulnerability testing
- [ ] CSRF protection verification
- [ ] Authentication bypass testing
- [ ] Authorization bypass testing
- [ ] Rate limiting verification
- [ ] Input validation testing
- [ ] API security testing
- [ ] Mobile app security testing
- [ ] Session management testing

---

## 11. Incident Response

### 11.1 Incident Response Plan

| Phase | Actions | Timeline |
|--------|----------|-----------|
| Detection | Monitor alerts, identify breach | Immediate |
| Containment | Isolate affected systems | < 1 hour |
| Eradication | Remove threat, patch vulnerabilities | < 4 hours |
| Recovery | Restore systems, verify integrity | < 24 hours |
| Lessons Learned | Document, update procedures | Within 1 week |

### 11.2 Security Incident Escalation

```
Level 1: Low Severity
- Security team notification
- Investigation within 24 hours
- No public disclosure

Level 2: Medium Severity
- Security team + Engineering notification
- Investigation within 4 hours
- Internal communication

Level 3: High Severity
- All-hands on deck
- Investigation within 1 hour
- External communication if needed
- Public disclosure if user data affected

Level 4: Critical Severity
- Emergency response team activated
- Immediate investigation
- Public disclosure within 72 hours
- Regulatory notification
```

---

## 12. Compliance

### 12.1 GDPR Compliance

- [ ] Data minimization
- [ ] Right to be forgotten
- [ ] Data portability
- [ ] Explicit consent
- [ ] Data breach notification
- [ ] Privacy by design

### 12.2 Data Retention

| Data Type | Retention Period | Action |
|-----------|------------------|--------|
| User Audio | 30 days | Auto-delete |
| Speech Results | 1 year | Archive |
| Practice Sessions | 2 years | Archive |
| Payment Records | 7 years | Keep |
| Audit Logs | 1 year | Archive |
| Refresh Tokens | 7 days | Auto-delete |
