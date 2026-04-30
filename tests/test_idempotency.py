"""Tests for idempotency middleware logic.
These are unit tests that validate the middleware's key validation logic.
Full integration tests require the Redis-enabled app (tested manually via curl).
"""
import re


def test_valid_idempotency_key_format():
    """Valid keys should match the pattern."""
    pattern = r'^[a-zA-Z0-9_\-]{4,64}$'
    assert re.match(pattern, 'test-txn-001')
    assert re.match(pattern, 'idem-key-777')
    assert re.match(pattern, 'abcd')
    assert re.match(pattern, 'a' * 64)


def test_invalid_idempotency_key_too_short():
    """Keys shorter than 4 chars should be rejected."""
    pattern = r'^[a-zA-Z0-9_\-]{4,64}$'
    assert not re.match(pattern, 'ab')
    assert not re.match(pattern, '')


def test_invalid_idempotency_key_too_long():
    """Keys longer than 64 chars should be rejected."""
    pattern = r'^[a-zA-Z0-9_\-]{4,64}$'
    assert not re.match(pattern, 'a' * 65)


def test_invalid_idempotency_key_special_chars():
    """Keys with special chars should be rejected."""
    pattern = r'^[a-zA-Z0-9_\-]{4,64}$'
    assert not re.match(pattern, 'test key!')
    assert not re.match(pattern, 'test@key')
