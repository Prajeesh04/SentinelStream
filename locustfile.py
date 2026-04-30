from locust import HttpUser, task, between


class TransactionUser(HttpUser):
    wait_time = between(0.1, 0.5)
    token = None

    def on_start(self):
        r = self.client.post('/api/v1/auth/token', json={'email': 'test@bank.com', 'password': 'password123'})
        self.token = r.json().get('access_token')

    @task
    def submit_transaction(self):
        import uuid
        self.client.post('/api/v1/transactions/',
            headers={'Authorization': f'Bearer {self.token}', 'Idempotency-Key': str(uuid.uuid4())},
            json={'user_id': '550e8400-e29b-41d4-a716-446655440000', 'amount': 150.00, 'merchant_name': 'Test Shop'})

# Run: locust -f locustfile.py --host=http://localhost:8000
# Open http://localhost:8089 → set 50 users, spawn rate 5 → Start
# Target: 100+ requests/second with < 200ms avg response time
