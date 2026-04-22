# Import ALL models here so Alembic can detect them
from app.models.base import Base  # noqa
from app.models.user import User  # noqa
from app.models.transaction import Transaction  # noqa
from app.models.fraud_rule import FraudRule  # noqa
from app.models.audit_log import AuditLog  # noqa
