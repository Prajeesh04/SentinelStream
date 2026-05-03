import time
import uuid
from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.transaction import TransactionRequest, TransactionResponse
from app.db.crud.transaction import create_transaction, get_transaction_by_id, get_transactions_by_user
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.fraud_engine import FraudEngine
from app.services.cache_service import get_user_profile

router = APIRouter(prefix='/transactions', tags=['Transactions'])


@router.post('/', response_model=TransactionResponse)
async def submit_transaction(
    payload: TransactionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    idempotency_key: str = Header(..., alias='Idempotency-Key'),
):
    start = time.perf_counter()

    if str(payload.user_id) != str(current_user.id) and current_user.role != 'admin':
        raise HTTPException(
            status_code=403,
            detail='Cannot submit transactions for other users',
        )

    # Get user profile (from cache or DB)
    user_profile = await get_user_profile(payload.user_id, db)
    if not user_profile:
        raise HTTPException(404, 'User not found')

    # Run fraud analysis (rules + ML)
    engine = FraudEngine(db=db)
    result = await engine.analyze(payload, user_profile)

    ms = round((time.perf_counter() - start) * 1000)

    txn = await create_transaction(
        db, user_id=payload.user_id, idempotency_key=idempotency_key,
        amount=payload.amount, currency=payload.currency,
        merchant_name=payload.merchant_name, merchant_category=payload.merchant_category,
        location_lat=payload.location_lat, location_lng=payload.location_lng,
        card_last_four=payload.card_last_four,
        status=result.status, risk_score=result.risk_score,
        decline_reason=result.reason, rule_triggered=result.rule_triggered,
        processing_time_ms=ms,
    )

    # Queue async tasks (webhook + alert) — non-blocking
    try:
        from app.workers.tasks import send_webhook_task, send_alert_email_task
        send_webhook_task.delay(str(txn.id), 'https://httpbin.org/post', result.status)
        if result.risk_score and result.risk_score > 0.9:
            send_alert_email_task.delay(str(txn.id), result.risk_score)
    except Exception:
        pass  # Celery not available — don't block the response

    return TransactionResponse(
        transaction_id=txn.id, status=result.status,
        risk_score=float(result.risk_score), reason=result.reason,
        rule_triggered=result.rule_triggered, processing_time_ms=ms,
    )


@router.get('/{txn_id}')
async def get_transaction(
    txn_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    txn = await get_transaction_by_id(db, txn_id)
    if not txn:
        raise HTTPException(status_code=404, detail='Transaction not found')
    if str(txn.user_id) != str(current_user.id) and current_user.role != 'admin':
        raise HTTPException(status_code=403, detail='Access denied')
    return txn


@router.get('/')
async def list_transactions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = 50,
):
    txns = await get_transactions_by_user(db, current_user.id, limit=limit)
    return txns
