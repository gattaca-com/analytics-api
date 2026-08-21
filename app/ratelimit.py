import math
import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.config import settings

EXEMPT_PATHS = {"/health", "/docs", "/redoc", "/openapi.json"}

# Paths that hit very large hypertables get a tighter budget.
HEAVY_PREFIXES = ("/bid-submissions",)


class _Bucket:
    __slots__ = ("tokens", "updated")

    def __init__(self, capacity: float):
        self.tokens = capacity
        self.updated = time.monotonic()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Per-client-IP token bucket. Returns 429 with Retry-After and
    X-RateLimit-* headers so well-behaved clients (and coding agents)
    can back off instead of hammering."""

    def __init__(self, app):
        super().__init__(app)
        self._buckets: dict[tuple[str, str], _Bucket] = {}

    @staticmethod
    def _limit_for(path: str) -> tuple[str, int]:
        if any(path.startswith(p) for p in HEAVY_PREFIXES):
            return "heavy", settings.rate_limit_heavy_per_minute
        return "default", settings.rate_limit_per_minute

    def _prune(self) -> None:
        if len(self._buckets) < 10_000:
            return
        now = time.monotonic()
        stale = [k for k, b in self._buckets.items() if now - b.updated > 120]
        for k in stale:
            del self._buckets[k]

    async def dispatch(self, request: Request, call_next) -> Response:
        path = request.url.path
        tier, limit = self._limit_for(path)
        if limit <= 0 or path in EXEMPT_PATHS:
            return await call_next(request)

        ip = request.client.host if request.client else "unknown"
        key = (ip, tier)
        bucket = self._buckets.get(key)
        if bucket is None:
            self._prune()
            bucket = self._buckets[key] = _Bucket(float(limit))

        now = time.monotonic()
        rate = limit / 60.0
        bucket.tokens = min(float(limit), bucket.tokens + (now - bucket.updated) * rate)
        bucket.updated = now

        if bucket.tokens < 1.0:
            retry_after = math.ceil((1.0 - bucket.tokens) / rate)
            return JSONResponse(
                status_code=429,
                content={
                    "detail": (
                        f"rate limit exceeded ({limit}/min for this endpoint); "
                        f"retry after {retry_after}s"
                    )
                },
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Remaining": "0",
                },
            )

        bucket.tokens -= 1.0
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(int(bucket.tokens))
        return response
