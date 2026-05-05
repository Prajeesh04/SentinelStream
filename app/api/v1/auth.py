import asyncio

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.core.security import verify_password, create_access_token, hash_password
from app.config import settings
from app.utils.redis_client import get_redis

router = APIRouter(prefix='/auth', tags=['Auth'])


@router.post('/token', response_model=TokenResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    redis = await get_redis()
    rl_key = f"login_attempts:{payload.email}"
    attempts = await redis.get(rl_key)
    
    if attempts and int(attempts) >= 5:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS, 
            detail="Too many failed login attempts. Please try again in 15 minutes."
        )

    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()
    ok = False
    if user:
        # bcrypt/passlib work is synchronous; run off the event loop so concurrent
        # Locust users do not stall the worker and wedge the DB pool.
        ok = await asyncio.to_thread(verify_password, payload.password, user.hashed_password)
        
    if not user or not ok:
        await redis.incr(rl_key)
        if not attempts:
            await redis.expire(rl_key, 900)  # 15 minutes window
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid email or password')
        
    # Login successful, clear attempts
    await redis.delete(rl_key)
    
    token = create_access_token({'sub': str(user.id), 'role': user.role})
    return TokenResponse(access_token=token, expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)


@router.post('/register', response_model=TokenResponse)
async def register(payload: RegisterRequest, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(User).where(User.email == payload.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail='Email already registered')
    hashed = await asyncio.to_thread(hash_password, payload.password)
    user = User(email=payload.email, hashed_password=hashed)
    db.add(user)
    await db.flush()
    token = create_access_token({'sub': str(user.id), 'role': user.role})
    return TokenResponse(access_token=token, expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)
