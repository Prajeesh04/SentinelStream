import pytest
from unittest.mock import MagicMock
from app.services.ml_scorer import MLScorer


def test_fallback_scoring_low_amount():
    """Test fallback heuristic for low-risk transaction."""
    scorer = MLScorer()
    txn = MagicMock()
    txn.amount = 45.0
    txn.merchant_category = 'food'
    txn.location_lat = None
    txn.location_lng = None

    user_profile = {'home_lat': None, 'home_lng': None}

    score = scorer.score(txn, user_profile)
    assert 0.0 <= score <= 1.0
    assert score < 0.5  # Low risk expected


def test_fallback_scoring_high_amount():
    """Test fallback heuristic for high-risk transaction."""
    scorer = MLScorer()
    txn = MagicMock()
    txn.amount = 7500.0
    txn.merchant_category = 'cryptocurrency'
    txn.location_lat = None
    txn.location_lng = None

    user_profile = {'home_lat': None, 'home_lng': None}

    score = scorer.score(txn, user_profile)
    assert 0.0 <= score <= 1.0
    assert score > 0.3  # Higher risk expected


def test_score_returns_float():
    """Score must always return a float."""
    scorer = MLScorer()
    txn = MagicMock()
    txn.amount = 100.0
    txn.merchant_category = 'retail'
    txn.location_lat = None
    txn.location_lng = None

    user_profile = {'home_lat': None, 'home_lng': None}

    score = scorer.score(txn, user_profile)
    assert isinstance(score, float)


def test_category_risk_mapping():
    """Test that category risk mapping works correctly."""
    from app.services.ml_scorer import CATEGORY_RISK
    assert CATEGORY_RISK['cryptocurrency'] == 0.8
    assert CATEGORY_RISK['food'] == 0.1
    assert CATEGORY_RISK['gambling'] == 0.7
