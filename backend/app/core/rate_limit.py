import asyncio
import logging
import time
from collections import defaultdict

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.core.config import settings
from app.core.redis import get_redis
from app.core.security import decode_token

logger = logging.getLogger(__name__)

_POLICIES = {
    "/api/v1/auth/send-otp": ("otp", "RATE_LIMIT_OTP_SEND"),
    "/api/v1/auth/verify-otp": ("otp-verify", "RATE_LIMIT_OTP_VERIFY"),
    "/api/v1/auth/login": ("login", "RATE_LIMIT_LOGIN"),
    "/api/v1/auth/register": ("register", "RATE_LIMIT_REGISTER"),
    "/api/v1/messages/send": ("messages", "RATE_LIMIT_MESSAGE_SEND"),
    "/api/v1/ai/generate-reply": ("ai", "RATE_LIMIT_AI_GENERATE"),
}
_memory_counters: dict[str, tuple[int, float]] = defaultdict(lambda: (0, 0.0))


def _identity(request: Request) -> tuple[str, str | None, str | None]:
    ip = request.client.host if request.client else "unknown"
    user_id = organization_id = None
    authorization = request.headers.get("authorization", "")
    if authorization.lower().startswith("bearer "):
        payload = decode_token(authorization[7:]) or {}
        user_id = str(payload.get("sub")) if payload.get("sub") else None
        organization_id = str(payload.get("org")) if payload.get("org") else None
    return ip, user_id, organization_id


async def _increment(key: str, window: int) -> tuple[int, int]:
    try:
        redis = await asyncio.wait_for(get_redis(), timeout=0.2)
        count = int(await asyncio.wait_for(redis.incr(key), timeout=0.2))
        if count == 1:
            await asyncio.wait_for(redis.expire(key, window), timeout=0.2)
        ttl = int(await asyncio.wait_for(redis.ttl(key), timeout=0.2))
        return count, max(ttl, 1)
    except Exception:
        now = time.monotonic()
        count, expires_at = _memory_counters[key]
        if expires_at <= now:
            count, expires_at = 0, now + window
        count += 1
        _memory_counters[key] = (count, expires_at)
        return count, max(int(expires_at - now), 1)


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if not settings.RATE_LIMIT_ENABLED or request.method == "OPTIONS":
            return await call_next(request)

        policy = _POLICIES.get(request.url.path)
        if policy is None:
            return await call_next(request)

        group, setting_name = policy
        limit = int(getattr(settings, setting_name))
        window = settings.RATE_LIMIT_WINDOW_SECONDS
        ip, user_id, organization_id = _identity(request)
        keys = [f"rl:{group}:ip:{ip}"]
        if user_id:
            keys.append(f"rl:{group}:user:{user_id}")
        if organization_id:
            keys.append(f"rl:{group}:org:{organization_id}")
        counts = [await _increment(key, window) for key in keys]
        org_limit = settings.RATE_LIMIT_ORG_CEILING if organization_id else limit
        effective_limit = org_limit if organization_id else limit
        exceeded = any(count > (org_limit if key.endswith(f":org:{organization_id}") else limit)
                       for key, (count, _) in zip(keys, counts))
        remaining = max(0, effective_limit - max(count for count, _ in counts))
        reset = max(ttl for _, ttl in counts)
        headers = {
            "X-RateLimit-Limit": str(effective_limit),
            "X-RateLimit-Remaining": str(remaining),
            "X-RateLimit-Reset": str(reset),
        }
        if exceeded:
            logger.warning("Rate limit exceeded path=%s ip=%s org=%s", request.url.path, ip, organization_id)
            headers["Retry-After"] = str(reset)
            return JSONResponse(
                {"detail": "Rate limit exceeded. Retry after the reset window."},
                status_code=429,
                headers=headers,
            )

        response = await call_next(request)
        for name, value in headers.items():
            response.headers[name] = value
        return response