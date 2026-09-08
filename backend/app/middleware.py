"""Lightweight in-memory rate limiting.

A simple fixed-window limiter keyed on client IP. It needs no external store,
which suits the stateless, single-instance free-tier deployment. For multi-
instance scaling this would move to a shared store (e.g. Redis/Upstash).
"""

from __future__ import annotations

import time
from collections import defaultdict, deque

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app import config


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self._hits: dict[str, deque[float]] = defaultdict(deque)

    def _client_key(self, request: Request) -> str:
        if request.client and request.client.host:
            return request.client.host
        return "unknown"

    async def dispatch(self, request: Request, call_next):
        # Only throttle the expensive API endpoints, not health checks.
        if not request.url.path.startswith("/api/"):
            return await call_next(request)

        now = time.monotonic()
        window = config.RATE_LIMIT_WINDOW_SECONDS
        limit = config.RATE_LIMIT_REQUESTS
        key = self._client_key(request)

        hits = self._hits[key]
        while hits and now - hits[0] > window:
            hits.popleft()

        if len(hits) >= limit:
            retry_after = int(window - (now - hits[0])) + 1
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests. Please slow down and try again shortly."},
                headers={"Retry-After": str(retry_after)},
            )

        hits.append(now)
        return await call_next(request)
