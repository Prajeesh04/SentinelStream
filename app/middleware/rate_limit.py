import base64
import json
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from app.utils.redis_client import get_redis
from app.config import settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if not request.url.path.startswith('/api/'):
            return await call_next(request)

        if settings.DEBUG and request.headers.get('X-Load-Test') == '1':
            return await call_next(request)

        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            try:
                token = auth_header.split(' ', 1)[1]
                payload_b64 = token.split('.')[1]
                payload_b64 += '=' * (4 - len(payload_b64) % 4)
                payload = json.loads(base64.urlsafe_b64decode(payload_b64.encode('ascii')))
                rate_key = f"rate:{payload.get('sub', 'anon')}"
            except Exception:
                rate_key = f"rate:{request.client.host if request.client else 'unknown'}"
        else:
            rate_key = f"rate:{request.client.host if request.client else 'unknown'}"

        try:
            redis = await get_redis()
            current = await redis.get(rate_key)
            if current and int(current) >= settings.RATE_LIMIT_PER_MINUTE:
                return JSONResponse(
                    status_code=429,
                    content={'detail': 'Rate limit exceeded. Try again later.'},
                    headers={'Retry-After': '60'},
                )
            pipe = redis.pipeline()
            pipe.incr(rate_key)
            pipe.expire(rate_key, 60)
            await pipe.execute()
        except Exception:
            pass

        return await call_next(request)
