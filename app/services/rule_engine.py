import json
import logging
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.fraud_rule import FraudRule
from app.utils.redis_client import get_redis

logger = logging.getLogger(__name__)
RULE_CACHE_TTL = 60


class RuleEngine:
    async def load_rules(self, db: AsyncSession) -> list:
        redis = await get_redis()
        cached = await redis.get('fraud_rules')
        if cached:
            return json.loads(cached)
        result = await db.execute(
            select(FraudRule).where(FraudRule.is_active == True).order_by(FraudRule.priority.desc())
        )
        rules = result.scalars().all()
        rules_dict = [
            {
                'field': r.field_name,
                'op': r.operator,
                'val': r.threshold_value,
                'action': r.action,
                'name': r.name,
            }
            for r in rules
        ]
        await redis.setex('fraud_rules', RULE_CACHE_TTL, json.dumps(rules_dict))
        return rules_dict

    async def evaluate(self, txn_data: dict, db: AsyncSession) -> Optional[dict]:
        rules = await self.load_rules(db)
        for rule in rules:
            field_val = txn_data.get(rule['field'])
            if field_val is None:
                continue
            triggered = False
            try:
                fv, rv = float(field_val), float(rule['val'])
                if rule['op'] == '>':
                    triggered = fv > rv
                elif rule['op'] == '<':
                    triggered = fv < rv
                elif rule['op'] == '>=':
                    triggered = fv >= rv
                elif rule['op'] == '<=':
                    triggered = fv <= rv
                elif rule['op'] == '=':
                    triggered = fv == rv
                elif rule['op'] == '!=':
                    triggered = fv != rv
            except (ValueError, TypeError):
                triggered = str(field_val).lower() == str(rule['val']).lower()
            if triggered:
                logger.info(f"Rule '{rule['name']}' triggered")
                return {'name': rule['name'], 'action': rule['action']}
        return None
