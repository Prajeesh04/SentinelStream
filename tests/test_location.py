"""Tests for location_service (haversine distance)."""
from app.services.location_service import haversine_distance


def test_same_location():
    assert haversine_distance(37.7749, -122.4194, 37.7749, -122.4194) == 0.0


def test_known_distance():
    """SF to LA is approximately 559 km."""
    d = haversine_distance(37.7749, -122.4194, 34.0522, -118.2437)
    assert 550 < d < 570


def test_none_values():
    assert haversine_distance(None, -122.4194, 34.0522, -118.2437) == 0.0
    assert haversine_distance(37.7749, None, 34.0522, -118.2437) == 0.0
    assert haversine_distance(37.7749, -122.4194, None, -118.2437) == 0.0
    assert haversine_distance(37.7749, -122.4194, 34.0522, None) == 0.0


def test_zero_coordinates():
    d = haversine_distance(0, 0, 0, 1)
    assert d > 0  # Should be about 111km
