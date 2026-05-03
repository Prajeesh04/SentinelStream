from locust import FastHttpUser, task, constant
import base64
import json

import gevent


def _response_json(response):
    body = getattr(response, 'text', None)
    if body is None:
        raw = getattr(response, 'content', b'') or b''
        body = raw.decode('utf-8', errors='replace')
    body = (body or '').strip()
    if not body:
        return None
    try:
        return json.loads(body)
    except json.JSONDecodeError:
        return None


class TransactionUser(FastHttpUser):
    # Minimal think-time — target is sustained high RPS once tokens are issued.
    wait_time = constant(0)
    token = None
    user_id = None
    common_headers = {'X-Load-Test': '1'}

    def on_start(self):
        # Burst logins can see 503 during cold start; retry so users do not crash on r.json().
        for attempt in range(20):
            r = self.client.post(
                '/api/v1/auth/token',
                headers={
                    **self.common_headers,
                    'Content-Type': 'application/json',
                },
                json={'email': 'test@bank.com', 'password': 'password123'},
            )
            if r.status_code == 200:
                data = _response_json(r)
                if data:
                    self.token = data.get('access_token')
                    if self.token:
                        break
            elif r.status_code in (502, 503, 504):
                gevent.sleep(0.25 * (attempt + 1))
                continue
            else:
                gevent.sleep(0.05)
                continue
        if not self.token:
            return
        try:
            payload_b64 = self.token.split('.')[1]
            payload_b64 += '=' * (-len(payload_b64) % 4)
            payload = json.loads(
                base64.urlsafe_b64decode(payload_b64.encode('utf-8')).decode('utf-8')
            )
            self.user_id = payload.get('sub')
        except Exception:
            self.user_id = None

    @task
    def submit_transaction(self):
        if not self.token or not self.user_id:
            gevent.sleep(0.05)
            return
        import uuid

        self.client.post(
            '/api/v1/transactions/',
            headers={
                **self.common_headers,
                'Authorization': f'Bearer {self.token}',
                'Idempotency-Key': str(uuid.uuid4()),
            },
            json={'user_id': self.user_id, 'amount': 150.00, 'merchant_name': 'Test Shop'},
        )


# Prerequisites: Postgres + Redis up, DB migrated + seeded (`test@bank.com`).
# Docker: docker-compose up -d postgres redis fastapi … then migrate/seed per README.
# Run: locust -f locustfile.py --host=http://localhost:8000
