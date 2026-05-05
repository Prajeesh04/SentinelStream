import pytest
import uuid


async def test_register_success(client):
    email = f'new_{uuid.uuid4().hex[:8]}@test.com'
    r = await client.post('/api/v1/auth/register', json={'email': email, 'password': 'pass123'})
    assert r.status_code == 200
    assert 'access_token' in r.json()


async def test_login_wrong_password(client):
    email = f'user_{uuid.uuid4().hex[:8]}@test.com'
    await client.post('/api/v1/auth/register', json={'email': email, 'password': 'correct'})
    r = await client.post('/api/v1/auth/token', json={'email': email, 'password': 'wrong'})
    assert r.status_code == 401


async def test_transaction_without_auth(client):
    """Without Bearer token, should get 403 (HTTPBearer returns 403 by default)."""
    r = await client.post('/api/v1/transactions/',
        headers={'Idempotency-Key': f'noauth-{uuid.uuid4().hex[:8]}'},
        json={'user_id': '550e8400-e29b-41d4-a716-446655440000', 'amount': 100, 'merchant_name': 'Test'})
    assert r.status_code in [401, 403]


async def test_duplicate_email_registration(client):
    email = f'dup_{uuid.uuid4().hex[:8]}@test.com'
    await client.post('/api/v1/auth/register', json={'email': email, 'password': 'pass123'})
    r = await client.post('/api/v1/auth/register', json={'email': email, 'password': 'pass123'})
    assert r.status_code == 400


async def test_health_endpoint(client):
    r = await client.get('/health')
    assert r.status_code == 200
    assert r.json()['status'] == 'healthy'


async def test_login_success(client):
    email = f'login_{uuid.uuid4().hex[:8]}@test.com'
    await client.post('/api/v1/auth/register', json={'email': email, 'password': 'pass123'})
    r = await client.post('/api/v1/auth/token', json={'email': email, 'password': 'pass123'})
    assert r.status_code == 200
    data = r.json()
    assert 'access_token' in data
    assert data['token_type'] == 'bearer'
    assert data['expires_in'] > 0


async def test_invalid_token(client):
    r = await client.get('/api/v1/transactions/',
        headers={'Authorization': 'Bearer invalid.token.here'})
    assert r.status_code == 401
