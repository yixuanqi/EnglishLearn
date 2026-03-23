"""Request logging middleware."""

import json
import time
import uuid
from typing import Optional

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for request/response logging."""

    async def dispatch(self, request: Request, call_next) -> Response:
        """Log request and response details."""
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        start_time = time.time()

        request_info = {
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "query": str(request.query_params),
            "client_ip": self._get_client_ip(request),
            "user_agent": request.headers.get("User-Agent", ""),
        }

        if settings.environment != "test":
            print(f"[REQUEST] {json.dumps(request_info)}")

        response = await call_next(request)

        process_time = time.time() - start_time

        response_info = {
            "request_id": request_id,
            "status_code": response.status_code,
            "process_time_ms": round(process_time * 1000, 2),
        }

        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = f"{process_time:.4f}"

        if settings.environment != "test":
            print(f"[RESPONSE] {json.dumps(response_info)}")

        return response

    def _get_client_ip(self, request: Request) -> str:
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
