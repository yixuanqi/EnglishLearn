"""Retry and circuit breaker utilities for AI services."""

import asyncio
import time
from functools import wraps
from typing import Any, Callable, Optional, TypeVar

from app.ai.exceptions import (
    AIServiceError,
    RateLimitError,
    ServiceUnavailableError,
)

T = TypeVar("T")


class RetryConfig:
    """Configuration for retry behavior."""

    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 30.0,
        exponential_base: float = 2.0,
        retryable_exceptions: tuple = (
            ServiceUnavailableError,
            RateLimitError,
            TimeoutError,
        ),
    ) -> None:
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.retryable_exceptions = retryable_exceptions


async def retry_with_backoff(
    func: Callable[..., T],
    config: Optional[RetryConfig] = None,
    *args: Any,
    **kwargs: Any,
) -> T:
    """Execute function with exponential backoff retry."""
    if config is None:
        config = RetryConfig()

    last_error: Optional[Exception] = None

    for attempt in range(config.max_attempts):
        try:
            return await func(*args, **kwargs)
        except config.retryable_exceptions as e:
            last_error = e
            if attempt == config.max_attempts - 1:
                break

            delay = min(
                config.base_delay * (config.exponential_base**attempt),
                config.max_delay,
            )

            if isinstance(e, RateLimitError) and e.retry_after:
                delay = max(delay, e.retry_after)

            await asyncio.sleep(delay)
        except AIServiceError:
            raise

    raise AIServiceError(
        service="Retry",
        message="Max retry attempts exceeded",
        details=str(last_error),
    )


def with_retry(config: Optional[RetryConfig] = None):
    """Decorator for retry with backoff."""

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            return await retry_with_backoff(func, config, *args, **kwargs)

        return wrapper

    return decorator


class CircuitBreaker:
    """Circuit breaker for service protection."""

    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: int = 60,
        success_threshold: int = 2,
    ) -> None:
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.success_threshold = success_threshold
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[float] = None
        self.state = "closed"

    def record_success(self) -> None:
        """Record a successful call."""
        self.failure_count = 0
        if self.state == "half_open":
            self.success_count += 1
            if self.success_count >= self.success_threshold:
                self.state = "closed"
                self.success_count = 0

    def record_failure(self) -> None:
        """Record a failed call."""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.state == "half_open":
            self.state = "open"
        elif self.failure_count >= self.failure_threshold:
            self.state = "open"

    def is_available(self) -> bool:
        """Check if the circuit allows requests."""
        if self.state == "closed":
            return True

        if self.state == "open":
            if self.last_failure_time is None:
                return True

            elapsed = time.time() - self.last_failure_time
            if elapsed >= self.timeout:
                self.state = "half_open"
                return True
            return False

        return True

    async def call(self, func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
        """Execute function with circuit breaker protection."""
        if not self.is_available():
            raise ServiceUnavailableError(
                service="CircuitBreaker",
                details="Circuit breaker is open",
            )

        try:
            result = await func(*args, **kwargs)
            self.record_success()
            return result
        except Exception as e:
            self.record_failure()
            raise
