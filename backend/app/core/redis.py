# Redis client and helpers for MTEJA AI
# Caching, pub/sub for real-time events, job queues
import os
from redis.asyncio import Redis
from typing import Optional

# Retrieve Redis URL from environment variables, defaulting to local Redis instance
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Global Redis client instance
redis_client: Optional[Redis] = None


async def init_redis() -> Redis:
  """Initialize and return the async Redis connection client."""
  global redis_client
  if redis_client is None:
    redis_client = Redis.from_url(
        REDIS_URL, encoding="utf-8", decode_responses=True
    )
  return redis_client


async def close_redis():
  """Close the Redis connection gracefully on application shutdown."""
  global redis_client
  if redis_client:
    await redis_client.close()
    redis_client = None


async def get_redis() -> Redis:
  """FastAPI dependency for injecting Redis client into endpoints."""
  if redis_client is None:
    return await init_redis()
  return redis_client