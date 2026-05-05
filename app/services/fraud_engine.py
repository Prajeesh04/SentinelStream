from dataclasses import dataclass
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.transaction import TransactionRequest
from app.services.rule_engine import RuleEngine
from app.services.location_service import haversine_distance
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
        home_lat = user_profile.get('home_lat')
        home_lng = user_profile.get('home_lng')
        
        distance_from_home = haversine_distance(
            home_lat, home_lng,
            txn.location_lat, txn.location_lng
        )
        
        location_status = 'UserHome' if distance_from_home <= 50.0 else 'Other'

        txn_data = {
            'amount': float(txn.amount),
            'merchant_category': txn.merchant_category or '',
            'location_lat': txn.location_lat,
            'location_lng': txn.location_lng,
            'distance_from_home': distance_from_home,
            'location': location_status,
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
        FIELD_MAPPING = {
            'amount': 'transaction amount',
            'location': 'location',
            'distance_from_home': 'distance from home location',
            'merchant_category': 'merchant category'
        }

        if rule_result and rule_result['action'] == 'DECLINE':
            field_name = FIELD_MAPPING.get(rule_result['field'], rule_result['field'])
            operator, threshold_value = rule_result['operator'], rule_result['threshold_value']
            
            # Construct human-readable reason
            if field_name == 'location' and operator == '!=' and str(threshold_value).lower() == 'userhome':
                reason_detail = "location is not same as home loc"
            elif operator == '>':
                reason_detail = f"{field_name} is above {threshold_value}"
            elif operator == '<':
                reason_detail = f"{field_name} is below {threshold_value}"
            elif operator == '!=':
                reason_detail = f"{field_name} is not {threshold_value}"
            else:
                reason_detail = f"{field_name} {operator} {threshold_value}"
                
            reason = f"Declined: {reason_detail}. (High Risk Transaction)"
            return FraudDecision('DECLINED', risk_score, reason, rule_result['name'])

        if risk_score >= settings.ML_RISK_THRESHOLD:
            return FraudDecision('DECLINED', risk_score, 'Declined: AI model detected unusual behavior. (High Risk Transaction)', None)

        if rule_result and rule_result['action'] == 'FLAG':
            return FraudDecision('FLAGGED', risk_score, f"Flagged by rule: {rule_result['name']}", rule_result['name'])

        return FraudDecision('APPROVED', risk_score, None, None)
