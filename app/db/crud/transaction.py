import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.transaction import Transaction


async def create_transaction(db: AsyncSession, **kwargs) -> Transaction:
    txn = Transaction(**kwargs)
    db.add(txn)
    await db.flush()
    return txn


async def get_transaction_by_id(db: AsyncSession, txn_id: uuid.UUID):
    result = await db.execute(select(Transaction).where(Transaction.id == txn_id))
    return result.scalar_one_or_none()


async def get_transactions_by_user(db: AsyncSession, user_id: uuid.UUID, limit=50):
    result = await db.execute(
        select(Transaction).where(Transaction.user_id == user_id)
        .order_by(Transaction.processed_at.desc()).limit(limit)
    )
    return result.scalars().all()
