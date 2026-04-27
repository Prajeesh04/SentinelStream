import logging
import numpy as np
import joblib
from app.config import settings
from app.services.location_service import haversine_distance

logger = logging.getLogger(__name__)

# Category risk mapping
CATEGORY_RISK = {
    'cryptocurrency': 0.8,
    'gambling': 0.7,
    'wire_transfer': 0.6,
    'jewelry': 0.5,
    'electronics': 0.4,
    'travel': 0.3,
    'food': 0.1,
    'groceries': 0.1,
    'retail': 0.15,
    'entertainment': 0.2,
}


class MLScorer:
    _pipeline = None

    def __init__(self):
        if MLScorer._pipeline is None:
            try:
                MLScorer._pipeline = joblib.load(settings.ML_MODEL_PATH)
                logger.info(f'ML model loaded from {settings.ML_MODEL_PATH}')
            except Exception as e:
                logger.warning(f'ML model not found: {e}. Using fallback scoring.')
                MLScorer._pipeline = None

    def _extract_features(self, txn, user_profile: dict) -> np.ndarray:
        """Extract features for the ML model."""
        amount = float(txn.amount)

        # Log-transform amount
        log_amount = np.log1p(amount)

        # Category risk
        category = (txn.merchant_category or '').lower()
        cat_risk = CATEGORY_RISK.get(category, 0.2)

        # Distance from home
        home_lat = user_profile.get('home_lat')
        home_lng = user_profile.get('home_lng')
        distance = haversine_distance(
            home_lat, home_lng,
            txn.location_lat, txn.location_lng,
        ) if home_lat and home_lng and txn.location_lat and txn.location_lng else 0.0

        # Hour of day (use 12 as default since we don't have timestamp in request)
        hour = 12

        # Is high amount
        is_high_amount = 1.0 if amount > 5000 else 0.0

        # Is risky category
        is_risky_cat = 1.0 if cat_risk >= 0.5 else 0.0

        features = np.array([[log_amount, cat_risk, distance, hour, is_high_amount, is_risky_cat]])
        return features

    def score(self, txn, user_profile: dict) -> float:
        """Return a risk score between 0.0 and 1.0."""
        features = self._extract_features(txn, user_profile)

        if self._pipeline is not None:
            try:
                # Isolation Forest: decision_function returns negative for anomalies
                raw_score = self._pipeline.decision_function(features)[0]
                # Convert to 0-1 range: more negative = higher risk
                # Typical range is roughly -0.5 to 0.5
                risk_score = max(0.0, min(1.0, 0.5 - raw_score))
                return round(risk_score, 3)
            except Exception as e:
                logger.warning(f'ML scoring failed: {e}')

        # Fallback: heuristic scoring
        amount = float(txn.amount)
        category = (txn.merchant_category or '').lower()
        cat_risk = CATEGORY_RISK.get(category, 0.2)

        score = 0.0
        if amount > 5000:
            score += 0.4
        elif amount > 1000:
            score += 0.2
        elif amount > 500:
            score += 0.1

        score += cat_risk * 0.3

        return round(min(score, 1.0), 3)
