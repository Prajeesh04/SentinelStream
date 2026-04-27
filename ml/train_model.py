"""Train an Isolation Forest model for fraud detection."""
import os
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.metrics import classification_report, precision_score, recall_score
from sklearn.model_selection import train_test_split
import joblib

FEATURES = ['log_amount', 'category_risk', 'distance_from_home', 'hour', 'is_high_amount', 'is_risky_category']
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'fraud_model.joblib')
DATA_PATH = os.path.join(os.path.dirname(__file__), 'training_data.csv')


def train():
    print('Loading training data...')
    data = pd.read_csv(DATA_PATH)
    print(f'Dataset: {len(data)} samples, {data["is_fraud"].sum():.0f} fraud')

    X = data[FEATURES].values
    y = data['is_fraud'].values

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    print('Training Isolation Forest...')
    model = IsolationForest(
        n_estimators=200,
        contamination=0.1,  # Expected fraud rate ~10%
        max_samples='auto',
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train)

    # Evaluate
    y_pred_raw = model.predict(X_test)
    # IsolationForest: -1 = anomaly (fraud), 1 = normal
    y_pred = (y_pred_raw == -1).astype(int)

    print('\n--- Classification Report ---')
    print(classification_report(y_test, y_pred, target_names=['Normal', 'Fraud']))

    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    print(f'Precision: {precision:.3f}')
    print(f'Recall: {recall:.3f}')

    # Test scoring
    sample_scores = model.decision_function(X_test[:5])
    risk_scores = np.clip(0.5 - sample_scores, 0, 1)
    print(f'\nSample risk scores: {risk_scores.round(3)}')

    # Save model
    joblib.dump(model, MODEL_PATH)
    print(f'\nModel saved to {MODEL_PATH}')
    return model


if __name__ == '__main__':
    train()
