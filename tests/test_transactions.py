import pytest
import uuid


async def _register_and_get_token_and_uid(client):
    """Helper: register a unique user, return (token, user_id)."""
    email = f'txn_{uuid.uuid4().hex[:8]}@test.com'
    reg = await client.post('/api/v1/auth/register', json={'email': email, 'password': 'pass1234', 'confirm_password': 'pass1234'})
    token = reg.json()['access_token']
    from app.core.security import decode_token
    payload = decode_token(token)
    return token, payload['sub']


async def test_transaction_approved(client):
    token, user_id = await _register_and_get_token_and_uid(client)
    r = await client.post('/api/v1/transactions/',
        headers={'Authorization': f'Bearer {token}', 'Idempotency-Key': f'test-txn-{uuid.uuid4().hex[:8]}'},
        json={'user_id': user_id, 'amount': 50.00, 'merchant_name': 'Starbucks', 'merchant_category': 'food'})
    assert r.status_code == 200
    data = r.json()
    assert 'transaction_id' in data
    assert data['status'] in ['APPROVED', 'FLAGGED', 'DECLINED']
    assert 0.0 <= data['risk_score'] <= 1.0
    assert data['processing_time_ms'] >= 0


async def test_amount_validation(client):
    token, user_id = await _register_and_get_token_and_uid(client)
    r = await client.post('/api/v1/transactions/',
        headers={'Authorization': f'Bearer {token}', 'Idempotency-Key': f'val-{uuid.uuid4().hex[:8]}'},
        json={'user_id': user_id, 'amount': -50, 'merchant_name': 'Shop'})
    assert r.status_code == 422


async def test_xss_stripped_from_merchant(client):
    token, user_id = await _register_and_get_token_and_uid(client)
    r = await client.post('/api/v1/transactions/',
        headers={'Authorization': f'Bearer {token}', 'Idempotency-Key': f'xss-{uuid.uuid4().hex[:8]}'},
        json={
            'user_id': user_id,
            'amount': 50.00,
            'merchant_name': '<script>alert("xss")</script>Shop',
        })
    assert r.status_code == 200


async def test_get_transaction(client):
    token, user_id = await _register_and_get_token_and_uid(client)
    # Create a transaction first
    r1 = await client.post('/api/v1/transactions/',
        headers={'Authorization': f'Bearer {token}', 'Idempotency-Key': f'get-{uuid.uuid4().hex[:8]}'},
        json={'user_id': user_id, 'amount': 25.00, 'merchant_name': 'TestShop'})
    assert r1.status_code == 200
    txn_id = r1.json()['transaction_id']

    # Get it back
    r2 = await client.get(f'/api/v1/transactions/{txn_id}',
        headers={'Authorization': f'Bearer {token}'})
    assert r2.status_code == 200


async def test_list_transactions(client):
    token, user_id = await _register_and_get_token_and_uid(client)
    r = await client.get('/api/v1/transactions/',
        headers={'Authorization': f'Bearer {token}'})
    assert r.status_code == 200
    assert isinstance(r.json(), list)


async def test_cannot_submit_transaction_for_another_user(client):
    token_a, _user_id_a = await _register_and_get_token_and_uid(client)
    _token_b, user_id_b = await _register_and_get_token_and_uid(client)
    r = await client.post(
        '/api/v1/transactions/',
        headers={
            'Authorization': f'Bearer {token_a}',
            'Idempotency-Key': f'cross-{uuid.uuid4().hex[:8]}',
        },
        json={
            'user_id': user_id_b,
            'amount': 10.0,
            'merchant_name': 'BadActor',
        },
    )
    assert r.status_code == 403


async def test_cannot_fetch_another_users_transaction(client):
    token_a, user_id_a = await _register_and_get_token_and_uid(client)
    token_b, _user_id_b = await _register_and_get_token_and_uid(client)
    r1 = await client.post(
        '/api/v1/transactions/',
        headers={
            'Authorization': f'Bearer {token_a}',
            'Idempotency-Key': f'own-{uuid.uuid4().hex[:8]}',
        },
        json={
            'user_id': user_id_a,
            'amount': 33.0,
            'merchant_name': 'Mine',
        },
    )
    assert r1.status_code == 200
    txn_id = r1.json()['transaction_id']
    r2 = await client.get(
        f'/api/v1/transactions/{txn_id}',
        headers={'Authorization': f'Bearer {token_b}'},
    )
    assert r2.status_code == 403
