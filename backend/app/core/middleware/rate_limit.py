"""Rate limiting middleware."""

import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Callable, Optional

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings


@dataclass
class RateLimitRule:
    """Rate limit rule configuration."""

    requests: int
    window_seconds: int
    key_prefix: str = ""


@dataclass
class RateLimitEntry:
    """Rate limit tracking entry."""

    count: int = 0
    window_start: float = field(default_factory=time.time)


class InMemoryRateLimiter:
    """In-memory rate limiter for single instance deployment."""

    def __init__(self) -> None:
        self._store: dict[str, RateLimitEntry] = defaultdict(RateLimitEntry)

    def is_allowed(self, key: str, rule: RateLimitRule) -> tuple[bool, int, int]:
        """Check if request is allowed under rate limit."""
        now = time.time()
        entry = self._store[key]

        if now - entry.window_start >= rule.window_seconds:
            entry.count = 0
            entry.window_start = now

        entry.count += 1
        remaining = max(0, rule.requests - entry.count)
        reset_time = int(entry.window_start + rule.window_seconds)

        return entry.count <= rule.requests, remaining, reset_time

    def cleanup_expired(self, max_age: int = 3600) -> None:
        """Remove expired entries."""
        now = time.time()
        expired_keys = [
            key
            for key, entry in self._store.items()
            if now - entry.window_start > max_age
        ]
        for key in expired_keys:
            del self._store[key]


rate_limiter = InMemoryRateLimiter()

DEFAULT_RULES: dict[str, RateLimitRule] = {
    "auth": RateLimitRule(requests=10, window_seconds=60, key_prefix="auth:"),
    "api": RateLimitRule(requests=100, window_seconds=60, key_prefix="api:"),
    "practice": RateLimitRule(requests=30, window_seconds=60, key_prefix="practice:"),
}


def get_client_ip(request: Request) -> str:
    """Extract client IP address from request."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()

    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip

    if request.client:
        return request.client.host

    return "unknown"


def get_rate_limit_key(request: Request, rule: RateLimitRule, user_id: Optional[str] = None) -> str:
    """Generate rate limit key."""
    ip = get_client_ip(request)

    if user_id:
        return f"{rule.key_prefix}user:{user_id}"

    return f"{rule.key_prefix}ip:{ip}"


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware."""

    def __init__(
        self,
        app: FastAPI,
        rules: Optional[dict[str, RateLimitRule]] = None,
    ) -> None:
        super().__init__(app)
        self.rules = rules or DEFAULT_RULES

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request through rate limiter."""
        path = request.url.path

        rule = self._get_rule_for_path(path)
        if rule is None:
            return await call_next(request)

        user_id = getattr(request.state, "user_id", None)
        key = get_rate_limit_key(request, rule, user_id)

        is_allowed, remaining, reset_time = rate_limiter.is_allowed(key, rule)

        headers = {
            "X-RateLimit-Limit": str(rule.requests),
            "X-RateLimit-Remaining": str(remaining),
            "X-RateLimit-Reset": str(reset_time),
        }

        if not is_allowed:
            return JSONResponse(
                status_code=429,
                content={
                    "error": {
                        "code": "RATE_LIMIT_EXCEEDED",
                        "message": "Too many requests. Please try again later.",
                        "details": {
                            "retry_after": reset_time - int(time.time()),
                        },
                    }
                },
                headers=headers,
            )

        response = await call_next(request)

        for header_name, header_value in headers.items():
            response.headers[header_name] = header_value

        return response

    def _get_rule_for_path(self, path: str) -> Optional[RateLimitRule]:
        """Get applicable rate limit rule for path."""
        if "/auth/" in path:
            return self.rules.get("auth")
        if "/practice/" in path:
            return self.rules.get("practice")
        if path.startswith("/api/"):
            return self.rules.get("api")
        return None
