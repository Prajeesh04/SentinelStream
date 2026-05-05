"""Test the fraud engine decision logic."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.fraud_engine import FraudEngine, FraudDecision
from app.schemas.transaction import TransactionRequest
import uuid


async def test_fraud_engine_decline_by_rule():
    """Rule with DECLINE action should result in DECLINED status."""
    db = AsyncMock()
    engine = FraudEngine(db)

    txn = MagicMock(spec=TransactionRequest)
    txn.amount = 7500.0
    txn.merchant_category = 'cryptocurrency'
    txn.location_lat = None
    txn.location_lng = None

    engine.rule_engine.evaluate = AsyncMock(return_value={'name': 'high_amount', 'action': 'DECLINE'})

    user_profile = {'home_lat': None, 'home_lng': None}
    decision = await engine.analyze(txn, user_profile)
    assert decision.status == 'DECLINED'
    assert decision.rule_triggered == 'high_amount'


async def test_fraud_engine_flag_by_rule():
    """Rule with FLAG action should result in FLAGGED status."""
    db = AsyncMock()
    engine = FraudEngine(db)

    txn = MagicMock(spec=TransactionRequest)
    txn.amount = 100.0
    txn.merchant_category = 'gambling'
    txn.location_lat = None
    txn.location_lng = None

    engine.rule_engine.evaluate = AsyncMock(return_value={'name': 'gambling', 'action': 'FLAG'})

    user_profile = {'home_lat': None, 'home_lng': None}
    decision = await engine.analyze(txn, user_profile)
    assert decision.status == 'FLAGGED'


async def test_fraud_engine_approve_no_rule():
    """No rule triggered + low ML score should result in APPROVED."""
    db = AsyncMock()
    engine = FraudEngine(db)

    txn = MagicMock(spec=TransactionRequest)
    txn.amount = 25.0
    txn.merchant_category = 'food'
    txn.location_lat = None
    txn.location_lng = None

    engine.rule_engine.evaluate = AsyncMock(return_value=None)

    user_profile = {'home_lat': None, 'home_lng': None}
    decision = await engine.analyze(txn, user_profile)
    assert decision.status == 'APPROVED'
    assert decision.risk_score >= 0.0
