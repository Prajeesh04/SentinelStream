import os

from celery import Celery

celery_app = Celery(
    'sentinelstream',
    broker=os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/1'),
    backend=os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/2'),
)
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    task_acks_late=True,
    broker_connection_retry_on_startup=True,
    broker_connection_retry=True,
    broker_connection_max_retries=10,
)
