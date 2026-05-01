from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from app.utils.redis_client import get_redis
from app.config import settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Only rate-limit API endpoints
        if not request.url.path.startswith('/api/'):
            return await call_next(request)

        # Allow load testing in debug mode without tripping per-IP limits.
        # This is opt-in via header so normal clients still get rate-limited.
        if settings.DEBUG and request.headers.get('X-Load-Test') == '1':
            return await call_next(request)

        client_ip = request.client.host if request.client else 'unknown'
        redis = await get_redis()
        key = f'rate:{client_ip}'

        current = await redis.get(key)
        if current and int(current) >= settings.RATE_LIMIT_PER_MINUTE:
            return JSONResponse(
                status_code=429,
                content={'detail': 'Rate limit exceeded. Try again later.'},
            )

        pipe = redis.pipeline()
        pipe.incr(key)
        pipe.expire(key, 60)
        await pipe.execute()

        return await call_next(request)
