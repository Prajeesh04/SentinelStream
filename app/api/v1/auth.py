import asyncio

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse
from app.core.security import verify_password, create_access_token, hash_password
from app.config import settings

router = APIRouter(prefix='/auth', tags=['Auth'])


@router.post('/token', response_model=TokenResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()
    ok = False
    if user:
        # bcrypt/passlib work is synchronous; run off the event loop so concurrent
        # Locust users do not stall the worker and wedge the DB pool.
        ok = await asyncio.to_thread(verify_password, payload.password, user.hashed_password)
    if not user or not ok:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid email or password')
    token = create_access_token({'sub': str(user.id), 'role': user.role})
    return TokenResponse(access_token=token, expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)


@router.post('/register', response_model=TokenResponse)
async def register(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(User).where(User.email == payload.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail='Email already registered')
    hashed = await asyncio.to_thread(hash_password, payload.password)
    user = User(email=payload.email, hashed_password=hashed)
    db.add(user)
    await db.flush()
    token = create_access_token({'sub': str(user.id), 'role': user.role})
    return TokenResponse(access_token=token, expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)
