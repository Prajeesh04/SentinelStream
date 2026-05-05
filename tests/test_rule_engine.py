import pytest
from unittest.mock import AsyncMock, MagicMock
from app.services.rule_engine import RuleEngine



async def test_high_amount_triggers_decline():
    """Test that amount > 5000 triggers the high_amount rule."""
    engine = RuleEngine()
    mock_db = AsyncMock()

    # Mock load_rules to return our test rules
    engine.load_rules = AsyncMock(return_value=[
        {'field': 'amount', 'operator': '>', 'threshold_value': '5000', 'action': 'DECLINE', 'name': 'high_amount'},
        {'field': 'merchant_category', 'operator': '=', 'threshold_value': 'cryptocurrency', 'action': 'FLAG', 'name': 'crypto_merchant'},
    ])

    result = await engine.evaluate({'amount': 7500, 'merchant_category': 'retail'}, mock_db)
    assert result is not None
    assert result['name'] == 'high_amount'
    assert result['action'] == 'DECLINE'



async def test_crypto_category_triggers_flag():
    """Test that cryptocurrency category triggers FLAG."""
    engine = RuleEngine()
    mock_db = AsyncMock()

    engine.load_rules = AsyncMock(return_value=[
        {'field': 'amount', 'operator': '>', 'threshold_value': '5000', 'action': 'DECLINE', 'name': 'high_amount'},
        {'field': 'merchant_category', 'operator': '=', 'threshold_value': 'cryptocurrency', 'action': 'FLAG', 'name': 'crypto_merchant'},
    ])

    result = await engine.evaluate({'amount': 100, 'merchant_category': 'cryptocurrency'}, mock_db)
    assert result is not None
    assert result['name'] == 'crypto_merchant'
    assert result['action'] == 'FLAG'



async def test_normal_transaction_no_rule():
    """Test that a normal transaction triggers no rules."""
    engine = RuleEngine()
    mock_db = AsyncMock()

    engine.load_rules = AsyncMock(return_value=[
        {'field': 'amount', 'operator': '>', 'threshold_value': '5000', 'action': 'DECLINE', 'name': 'high_amount'},
    ])

    result = await engine.evaluate({'amount': 45, 'merchant_category': 'food'}, mock_db)
    assert result is None



async def test_rule_priority_ordering():
    """Higher priority rules should be evaluated first."""
    engine = RuleEngine()
    mock_db = AsyncMock()

    # high_amount (priority 10) should fire before crypto (priority 8) 
    engine.load_rules = AsyncMock(return_value=[
        {'field': 'amount', 'operator': '>', 'threshold_value': '5000', 'action': 'DECLINE', 'name': 'high_amount'},
        {'field': 'merchant_category', 'operator': '=', 'threshold_value': 'cryptocurrency', 'action': 'FLAG', 'name': 'crypto_merchant'},
    ])

    result = await engine.evaluate({'amount': 7500, 'merchant_category': 'cryptocurrency'}, mock_db)
    assert result['name'] == 'high_amount'  # Higher priority fires first
