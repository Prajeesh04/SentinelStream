from dataclasses import dataclass
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.transaction import TransactionRequest
from app.services.rule_engine import RuleEngine
from app.config import settings


@dataclass
class FraudDecision:
    status: str
    risk_score: float
    reason: Optional[str]
    rule_triggered: Optional[str]


class FraudEngine:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.rule_engine = RuleEngine()

    async def analyze(self, txn: TransactionRequest, user_profile: dict) -> FraudDecision:
        txn_data = {
            'amount': float(txn.amount),
            'merchant_category': txn.merchant_category or '',
            'location_lat': txn.location_lat,
            'location_lng': txn.location_lng,
        }
        # Step 1: Check rules
        rule_result = await self.rule_engine.evaluate(txn_data, self.db)

        # Step 2: ML scoring (import lazily to avoid startup failure if model missing)
        try:
            from app.services.ml_scorer import MLScorer
            scorer = MLScorer()
            risk_score = scorer.score(txn, user_profile)
        except Exception:
            risk_score = 0.1  # Fallback if model not ready

        # Step 3: Combine decisions
        if rule_result and rule_result['action'] == 'DECLINE':
            return FraudDecision('DECLINED', risk_score, f"Rule: {rule_result['name']}", rule_result['name'])
        if risk_score >= settings.ML_RISK_THRESHOLD:
            return FraudDecision('DECLINED', risk_score, 'ML_HIGH_RISK', None)
        if rule_result and rule_result['action'] == 'FLAG':
            return FraudDecision('FLAGGED', risk_score, f"Rule: {rule_result['name']}", rule_result['name'])
        return FraudDecision('APPROVED', risk_score, None, None)
