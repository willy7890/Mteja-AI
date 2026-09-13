"""
backend/app/services/rate_limit.py

Simple rate limiter for campaign-launch endpoints.

Default: Redis-backed sliding window (works across multiple API workers/pods).
Falls back to an in-process limiter if no Redis client is configured — useful
for local dev/tests, but NOT safe for multi-worker production deployments
(each worker would track its own counter).

Adjust the Redis connection wiring (`get_redis`) to match how your project
already connects to Redis. If Mteja AI doesn't use Redis yet, either add it
(recommended for anything beyond a single dev instance) or tell me and I'll
swap this for a DB-backed limiter instead.
"""

from __future__ import annotations

import time
import asyncio
import logging
from collections import defaultdict, deque

from fastapi import HTTPException, status

logger = logging.getLogger(__name__)


class RateLimitExceeded(HTTPException):
    def __init__(self, retry_after_seconds: int):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many broadcast campaigns launched. Please slow down.",
            headers={"Retry-After": str(retry_after_seconds)},
        )


# --------------------------------------------------------------------------
# Redis-backed implementation (preferred)
# --------------------------------------------------------------------------

async def _redis_sliding_window(
    redis_client, key: str, max_calls: int, window_seconds: int
) -> tuple[bool, int]:
    """
    Sliding-window counter using a Redis sorted set.
    Returns (allowed, retry_after_seconds).
    """
    now = time.time()
    window_start = now - window_seconds
    redis_key = f"ratelimit:{key}"

    pipe = redis_client.pipeline()
    pipe.zremrangebyscore(redis_key, 0, window_start)
    pipe.zadd(redis_key, {str(now): now})
    pipe.zcard(redis_key)
    pipe.expire(redis_key, window_seconds)
    _, _, count, _ = await pipe.execute()

    if count > max_calls:
        # Remove the entry we just added since this call is rejected.
        await redis_client.zrem(redis_key, str(now))
        oldest = await redis_client.zrange(redis_key, 0, 0, withscores=True)
        retry_after = int(window_seconds - (now - oldest[0][1])) if oldest else window_seconds
        return False, max(retry_after, 1)

    return True, 0


# --------------------------------------------------------------------------
# In-memory fallback (single-process only — dev/test use)
# --------------------------------------------------------------------------

class _InMemoryLimiter:
    def __init__(self):
        self._hits: dict[str, deque] = defaultdict(deque)
        self._lock = asyncio.Lock()

    async def check(self, key: str, max_calls: int, window_seconds: int) -> tuple[bool, int]:
        async with self._lock:
            now = time.time()
            window_start = now - window_seconds
            q = self._hits[key]
            while q and q[0] < window_start:
                q.popleft()

            if len(q) >= max_calls:
                retry_after = int(window_seconds - (now - q[0]))
                return False, max(retry_after, 1)

            q.append(now)
            return True, 0


_in_memory_limiter = _InMemoryLimiter()


# --------------------------------------------------------------------------
# Public entrypoint
# --------------------------------------------------------------------------

async def enforce_rate_limit(*, key: str, max_calls: int, window_seconds: int) -> None:
    """
    Raises RateLimitExceeded (HTTP 429) if `key` has exceeded `max_calls`
    within the trailing `window_seconds`. Otherwise records this call and
    returns None.

    Usage:
        await enforce_rate_limit(key=f"broadcast_create:{org_id}", max_calls=10, window_seconds=3600)
    """
    redis_client = None
    try:
        # Lazy import so this module doesn't hard-require redis if unused.
        from app.core.redis import get_redis  # adjust to your actual redis accessor
        redis_client = get_redis()
    except Exception:
        redis_client = None

    if redis_client is not None:
        allowed, retry_after = await _redis_sliding_window(redis_client, key, max_calls, window_seconds)
    else:
        logger.warning(
            "Rate limiter falling back to in-memory store (no Redis configured) — "
            "not safe for multi-worker deployments."
        )
        allowed, retry_after = await _in_memory_limiter.check(key, max_calls, window_seconds)

    if not allowed:
        raise RateLimitExceeded(retry_after_seconds=retry_after)