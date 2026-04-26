from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.fraud_rule import FraudRule
from app.schemas.fraud_rule import FraudRuleCreate, FraudRuleResponse
from typing import List

router = APIRouter(prefix='/rules', tags=['Rules'])


@router.get('/', response_model=List[FraudRuleResponse])
async def get_rules(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(FraudRule).order_by(FraudRule.priority.desc())
    )
    return result.scalars().all()


@router.post('/', response_model=FraudRuleResponse)
async def create_rule(
    payload: FraudRuleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail='Admin access required')
    rule = FraudRule(**payload.model_dump())
    db.add(rule)
    await db.flush()
    await db.refresh(rule)
    # Invalidate cached rules
    try:
        from app.utils.redis_client import get_redis
        redis = await get_redis()
        await redis.delete('fraud_rules')
    except Exception:
        pass
    return rule
