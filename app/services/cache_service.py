import json
import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.utils.redis_client import get_redis
from app.models.user import User

USER_CACHE_TTL = 3600


async def get_user_profile(user_id: uuid.UUID, db: AsyncSession) -> Optional[dict]:
    redis = await get_redis()
    key = f'user:{user_id}'
    cached = await redis.get(key)
    if cached:
        return json.loads(cached)  # Cache HIT
    result = await db.execute(select(User).where(User.id == user_id, User.is_active == True))
    user = result.scalar_one_or_none()
    if not user:
        return None
    profile = {
        'id': str(user.id),
        'email': user.email,
        'role': user.role,
        'home_lat': user.home_lat,
        'home_lng': user.home_lng,
    }
    await redis.setex(key, USER_CACHE_TTL, json.dumps(profile))  # Store with TTL
    return profile
