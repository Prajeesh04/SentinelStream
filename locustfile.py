from locust import FastHttpUser, task, constant
import base64
import json


class TransactionUser(FastHttpUser):
    # Keep think-time near zero to measure max local throughput
    wait_time = constant(0)
    token = None
    user_id = None
    common_headers = {'X-Load-Test': '1'}

    def on_start(self):
        r = self.client.post(
            '/api/v1/auth/token',
            headers=self.common_headers,
            json={'email': 'test@bank.com', 'password': 'password123'},
        )
        self.token = r.json().get('access_token')
        if self.token:
            # Decode JWT payload without verification to grab the subject (user id)
            try:
                payload_b64 = self.token.split('.')[1]
                payload_b64 += '=' * (-len(payload_b64) % 4)  # pad for base64url
                payload = json.loads(base64.urlsafe_b64decode(payload_b64.encode('utf-8')).decode('utf-8'))
                self.user_id = payload.get('sub')
            except Exception:
                self.user_id = None

    @task
    def submit_transaction(self):
        import uuid
        self.client.post('/api/v1/transactions/',
            headers={
                **self.common_headers,
                'Authorization': f'Bearer {self.token}',
                'Idempotency-Key': str(uuid.uuid4()),
            },
            json={'user_id': self.user_id, 'amount': 150.00, 'merchant_name': 'Test Shop'})

# Run: locust -f locustfile.py --host=http://localhost:8000
# Open http://localhost:8089 → set 50 users, spawn rate 5 → Start
# Target: 100+ requests/second with < 200ms avg response time
