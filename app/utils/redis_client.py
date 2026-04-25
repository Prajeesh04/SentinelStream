import redis.asyncio as aioredis
from app.config import settings

_redis = None


async def get_redis():
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(
            settings.REDIS_URL,
            encoding='utf-8',
            decode_responses=True,
            socket_connect_timeout=2,
        )
    # Verify connection is alive
    try:
        await _redis.ping()
    except Exception:
        _redis = aioredis.from_url(
            settings.REDIS_URL,
            encoding='utf-8',
            decode_responses=True,
            socket_connect_timeout=2,
        )
    return _redis
