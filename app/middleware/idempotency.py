import json
import re
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from app.utils.redis_client import get_redis

IDEMPOTENCY_TTL = 86400  # 24 hours


class IdempotencyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method != 'POST' or '/transaction' not in request.url.path:
            return await call_next(request)
        key = request.headers.get('Idempotency-Key')
        if not key:
            return JSONResponse(status_code=422, content={'detail': 'Idempotency-Key header required'})
        if not re.match(r'^[a-zA-Z0-9_\-]{4,64}$', key):
            return JSONResponse(status_code=422, content={'detail': 'Invalid Idempotency-Key format'})
        redis = await get_redis()
        cached = await redis.get(f'idem:{key}')
        if cached:
            return JSONResponse(content=json.loads(cached), headers={'X-Idempotent-Replay': 'true'})
        response = await call_next(request)
        if response.status_code == 200:
            body = b''
            async for chunk in response.body_iterator:
                body += chunk
            await redis.setex(f'idem:{key}', IDEMPOTENCY_TTL, body.decode())
            return Response(
                content=body, status_code=200,
                headers=dict(response.headers),
                media_type=response.media_type,
            )
        return response
