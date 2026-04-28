import httpx
import logging
from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3)
def send_webhook_task(self, txn_id: str, merchant_url: str, status: str):
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.post(merchant_url, json={'transaction_id': txn_id, 'status': status})
            response.raise_for_status()
            logger.info(f'Webhook delivered for {txn_id}: {response.status_code}')
    except Exception as exc:
        logger.warning(f'Webhook failed for {txn_id}: {exc}')
        # Exponential backoff: retry after 10s, 30s, 90s
        raise self.retry(exc=exc, countdown=10 * (2 ** self.request.retries))


@celery_app.task
def send_alert_email_task(txn_id: str, risk_score: float):
    # In production: use SendGrid or AWS SES
    logger.warning(f'HIGH RISK ALERT: Transaction {txn_id} risk_score={risk_score}')
