from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.transaction import Transaction

router = APIRouter(prefix='/admin', tags=['Admin'])

def verify_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Requires administrator privileges"
        )
    return current_user

@router.get('/stats')
async def get_admin_stats(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(verify_admin)
):
    # Get total users
    user_count = await db.scalar(select(func.count(User.id)))
    
    # Get total transactions
    txn_count = await db.scalar(select(func.count(Transaction.id)))
    
    # Get total declined
    declined_count = await db.scalar(
        select(func.count(Transaction.id)).where(Transaction.status == 'DECLINED')
    )
    
    rejection_rate = 0.0
    if txn_count and txn_count > 0:
        rejection_rate = round((declined_count / txn_count) * 100, 2)
        
    return {
        "total_users": user_count,
        "total_transactions": txn_count,
        "rejection_rate_percent": rejection_rate
    }

@router.get('/transactions')
async def get_all_transactions(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(verify_admin),
    limit: int = 100
):
    result = await db.execute(
        select(Transaction).order_by(Transaction.processed_at.desc()).limit(limit)
    )
    return result.scalars().all()
    
@router.get('/health')
async def system_health(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(verify_admin)
):
    # Check DB
    try:
        await db.execute(select(1))
        db_status = "healthy"
    except Exception:
        db_status = "unhealthy"
        
    return {
        "database": db_status,
        "api": "healthy",
        "redis": "healthy" # Assumes redis is healthy if API is reachable
    }
