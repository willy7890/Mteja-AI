"""
Placeholder rate limiter - does nothing yet, just unblocks imports.
Replace with slowapi/fastapi-limiter before real traffic.
"""

from functools import wraps


def rate_limit(spec: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)
        return wrapper
    return decorator