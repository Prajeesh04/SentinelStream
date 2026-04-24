from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.transaction import Transaction

router = APIRouter(prefix='/dashboard', tags=['Dashboard'])


@router.get('/stats')
async def get_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Total transactions
    total = await db.execute(select(func.count(Transaction.id)))
    total_count = total.scalar()

    # By status
    approved = await db.execute(
        select(func.count(Transaction.id)).where(Transaction.status == 'APPROVED')
    )
    flagged = await db.execute(
        select(func.count(Transaction.id)).where(Transaction.status == 'FLAGGED')
    )
    declined = await db.execute(
        select(func.count(Transaction.id)).where(Transaction.status == 'DECLINED')
    )

    # Average risk score
    avg_risk = await db.execute(select(func.avg(Transaction.risk_score)))

    return {
        'total_transactions': total_count,
        'approved': approved.scalar(),
        'flagged': flagged.scalar(),
        'declined': declined.scalar(),
        'avg_risk_score': float(avg_risk.scalar() or 0),
    }
