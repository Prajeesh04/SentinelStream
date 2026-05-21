from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.transaction import Transaction
from sqlalchemy import select, func, case

router = APIRouter(prefix='/dashboard', tags=['Dashboard'])



@router.get('/stats')
async def get_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    uid = current_user.id
    #txn_for_user = Transaction.user_id == uid

    result = await db.execute(
        select(
            func.count(Transaction.id),
            func.sum(case((Transaction.status == 'APPROVED', 1), else_=0)),
            func.sum(case((Transaction.status == 'FLAGGED', 1), else_=0)),
            func.sum(case((Transaction.status == 'DECLINED', 1), else_=0)),
            func.avg(Transaction.risk_score)
        ).where(Transaction.user_id == uid)
    )

    total, approved, flagged, declined, avg_risk = result.one()

    return {
        'total_transactions': total or 0,
        'approved': approved or 0,
        'flagged': flagged or 0,
        'declined': declined or 0,
        'avg_risk_score': float(avg_risk or 0),
    }