from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from starlette.requests import Request
from starlette.responses import JSONResponse
from app.config import settings
from app.api.v1.router import api_router
from app.api.v1.health import router as health_router
from app.middleware.idempotency import IdempotencyMiddleware
from app.middleware.rate_limit import RateLimitMiddleware
from app.core.exceptions import FraudDetectionError, fraud_detection_exception_handler


@asynccontextmanager
async def lifespan(_app: FastAPI):
    from app.db.session import engine

    startup_msg_db = (
        'PostgreSQL is not reachable via DATABASE_URL. '
        'On Windows: ensure Docker Desktop is running (not just installed), then from the project root run '
        '`docker compose up -d postgres redis`. '
        'If `docker` fails with dockerDesktopLinuxEngine / npipe, open Docker Desktop from the Start menu and wait until it says running. '
        'Alternatively install PostgreSQL locally and point DATABASE_URL at it.'
    )
    try:
        async with engine.connect() as conn:
            await conn.execute(text('SELECT 1'))
    except Exception as exc:
        raise RuntimeError(startup_msg_db) from exc

    startup_msg_redis = (
        'Redis is not reachable via REDIS_URL (required for idempotency and rate limiting when enabled). '
        'Start Redis with Docker: `docker compose up -d redis`, or install Redis for Windows and match REDIS_URL in .env.'
    )
    try:
        from app.utils.redis_client import get_redis

        r = await get_redis()
        await r.ping()
    except Exception as exc:
        raise RuntimeError(startup_msg_redis) from exc

    yield

    await engine.dispose()


async def operational_error_handler(_request: Request, exc: OperationalError):
    _ = exc
    return JSONResponse(
        status_code=503,
        content={
            'detail': 'Database unavailable.',
            'hint': 'Ensure PostgreSQL is running and DATABASE_URL matches (local: postgresql on port 5432).',
        },
    )


app = FastAPI(
    title='SentinelStream',
    description='Real-time fraud detection API',
    version='1.0.0',
    lifespan=lifespan,
)

# Middleware (order matters — outermost first)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(IdempotencyMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# Exception handlers
app.add_exception_handler(FraudDetectionError, fraud_detection_exception_handler)
app.add_exception_handler(OperationalError, operational_error_handler)

# Routers
app.include_router(health_router)
app.include_router(api_router)
