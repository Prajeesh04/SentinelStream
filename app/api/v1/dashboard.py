from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.sql import functions as sqlfunc
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
    uid = current_user.id
    txn_for_user = Transaction.user_id == uid

    total = await db.execute(select(sqlfunc.count(Transaction.id)).where(txn_for_user))
    total_count = total.scalar_one()

    approved = await db.execute(
    select(sqlfunc.count(Transaction.id)).where(
        (txn_for_user) & (Transaction.status == 'APPROVED')
    )
)

    flagged = await db.execute(
    select(sqlfunc.count(Transaction.id)).where(
        (txn_for_user) & (Transaction.status == 'FLAGGED')
    )
)

    declined = await db.execute(
    select(sqlfunc.count(Transaction.id)).where(
        (txn_for_user) & (Transaction.status == 'DECLINED')
    )
)
    avg_risk = await db.execute(
    select(sqlfunc.avg(Transaction.risk_score)).where(txn_for_user)
)

    return {
    'total_transactions': total_count,
    'approved': approved.scalar(),
    'flagged': flagged.scalar(),
    'declined': declined.scalar(),
    'avg_risk_score': float(avg_risk.scalar() or 0),
	}
