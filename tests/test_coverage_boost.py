"""Tests for additional coverage: config, schemas, exceptions, dashboard."""
import pytest
import uuid
from app.schemas.transaction import TransactionRequest
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.user import UserResponse
from app.core.exceptions import FraudDetectionError, fraud_detection_exception_handler
from app.config import get_settings


def test_transaction_request_html_stripping():
    txn = TransactionRequest(
        user_id=uuid.uuid4(),
        amount=100.0,
        merchant_name='<script>alert("xss")</script>TestShop',
    )
    assert '<script>' not in txn.merchant_name
    assert 'TestShop' in txn.merchant_name


def test_transaction_request_valid():
    from decimal import Decimal
    txn = TransactionRequest(
        user_id=uuid.uuid4(),
        amount=Decimal('999.99'),
        merchant_name='Amazon',
        merchant_category='retail',
        currency='EUR',
    )
    assert txn.currency == 'EUR'
    assert txn.amount == Decimal('999.99')


def test_transaction_request_negative_amount():
    with pytest.raises(Exception):
        TransactionRequest(
            user_id=uuid.uuid4(),
            amount=-1,
            merchant_name='Test',
        )


def test_auth_request_schema():
    req = LoginRequest(email='test@test.com', password='secure123')
    assert req.email == 'test@test.com'
    assert req.password == 'secure123'


def test_token_response_schema():
    resp = TokenResponse(access_token='abc.def.ghi', token_type='bearer', expires_in=3600)
    assert resp.access_token == 'abc.def.ghi'
    assert resp.expires_in == 3600


def test_user_response_schema():
    uid = uuid.uuid4()
    resp = UserResponse(id=uid, email='a@b.com', role='user', is_active=True)
    assert resp.email == 'a@b.com'
    assert resp.is_active is True


def test_fraud_detection_error():
    err = FraudDetectionError('Test error')
    assert str(err) == 'Test error'


def test_config_singleton():
    s1 = get_settings()
    s2 = get_settings()
    assert s1 is s2


def test_config_allowed_origins():
    s = get_settings()
    origins = s.allowed_origins_list
    assert isinstance(origins, list)
    assert len(origins) > 0


async def test_dashboard_stats(client):
    r = await client.get('/api/v1/dashboard/stats', headers={'Authorization': 'Bearer invalid'})
    assert r.status_code == 401


async def test_rules_list(client):
    email = f'rules_{uuid.uuid4().hex[:8]}@test.com'
    reg = await client.post('/api/v1/auth/register', json={'email': email, 'password': 'pass'})
    token = reg.json()['access_token']
    r = await client.get('/api/v1/rules/', headers={'Authorization': f'Bearer {token}'})
    assert r.status_code == 200
    assert isinstance(r.json(), list)


async def test_dashboard_stats_authenticated(client):
    email = f'dash_{uuid.uuid4().hex[:8]}@test.com'
    reg = await client.post('/api/v1/auth/register', json={'email': email, 'password': 'pass'})
    token = reg.json()['access_token']
    r = await client.get('/api/v1/dashboard/stats', headers={'Authorization': f'Bearer {token}'})
    assert r.status_code == 200
    data = r.json()
    assert 'total_transactions' in data
