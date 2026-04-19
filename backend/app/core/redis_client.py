import os

import redis.asyncio as aioredis

_client: aioredis.Redis | None = None


async def get_redis() -> aioredis.Redis:
    global _client
    if _client is None:
        _client = await aioredis.from_url(
            os.getenv("REDIS_URL", "redis://localhost:6379"),
            encoding="utf-8",
            decode_responses=True,
        )
    return _client