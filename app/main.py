from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.v1.router import api_router
from app.api.v1.health import router as health_router
from app.middleware.idempotency import IdempotencyMiddleware
from app.middleware.rate_limit import RateLimitMiddleware
from app.core.exceptions import FraudDetectionError, fraud_detection_exception_handler

app = FastAPI(
    title='SentinelStream',
    description='Real-time fraud detection API',
    version='1.0.0',
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

# Routers
app.include_router(health_router)
app.include_router(api_router)
