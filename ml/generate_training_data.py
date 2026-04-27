"""Generate synthetic transaction data for training the fraud detection model."""
import pandas as pd
import numpy as np
import os

np.random.seed(42)

NUM_NORMAL = 9000
NUM_FRAUD = 1000

def generate_normal_transactions(n):
    """Generate normal transaction patterns."""
    return pd.DataFrame({
        'amount': np.random.lognormal(mean=4.0, sigma=1.0, size=n).clip(1, 5000),
        'category_risk': np.random.choice([0.1, 0.1, 0.15, 0.2, 0.3], size=n),
        'distance_from_home': np.random.exponential(scale=10, size=n).clip(0, 100),
        'hour': np.random.choice(range(8, 22), size=n),  # Business hours
        'is_high_amount': np.zeros(n),
        'is_risky_category': np.zeros(n),
        'is_fraud': np.zeros(n),
    })

def generate_fraud_transactions(n):
    """Generate fraudulent transaction patterns."""
    amounts = np.random.lognormal(mean=7.0, sigma=1.5, size=n).clip(500, 999999)
    return pd.DataFrame({
        'amount': amounts,
        'category_risk': np.random.choice([0.5, 0.6, 0.7, 0.8], size=n),
        'distance_from_home': np.random.exponential(scale=500, size=n).clip(100, 10000),
        'hour': np.random.choice([0, 1, 2, 3, 4, 5, 23], size=n),  # Late night
        'is_high_amount': (amounts > 5000).astype(float),
        'is_risky_category': np.ones(n),
        'is_fraud': np.ones(n),
    })


if __name__ == '__main__':
    normal = generate_normal_transactions(NUM_NORMAL)
    fraud = generate_fraud_transactions(NUM_FRAUD)
    data = pd.concat([normal, fraud], ignore_index=True).sample(frac=1, random_state=42)

    # Transform amount to log scale
    data['log_amount'] = np.log1p(data['amount'])

    output_path = os.path.join(os.path.dirname(__file__), 'training_data.csv')
    data.to_csv(output_path, index=False)
    print(f'Generated {len(data)} transactions ({NUM_NORMAL} normal, {NUM_FRAUD} fraud)')
    print(f'Saved to {output_path}')
    print(f'Fraud rate: {data["is_fraud"].mean():.1%}')
