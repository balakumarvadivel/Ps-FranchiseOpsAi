"""
These test the rate limiter's core sliding-window algorithm directly
(bypassing the FastAPI Request/HTTPException wrapper) since a full FastAPI
integration test would need the app running.
"""
import time
from app.core.rate_limit import rate_limit, _attempts
from fastapi import HTTPException


class _FakeClient:
    def __init__(self, host):
        self.host = host


class _FakeRequest:
    def __init__(self, host):
        self.client = _FakeClient(host)


def setup_function():
    _attempts.clear()


def test_allows_requests_under_the_limit():
    req = _FakeRequest("1.1.1.1")
    for _ in range(5):
        rate_limit(req, max_attempts=5, window_seconds=60)  # should not raise


def test_blocks_requests_over_the_limit():
    req = _FakeRequest("2.2.2.2")
    for _ in range(5):
        rate_limit(req, max_attempts=5, window_seconds=60)
    try:
        rate_limit(req, max_attempts=5, window_seconds=60)
        assert False, "should have raised"
    except HTTPException as e:
        assert e.status_code == 429


def test_different_ips_have_independent_limits():
    req_a = _FakeRequest("3.3.3.3")
    req_b = _FakeRequest("4.4.4.4")
    for _ in range(5):
        rate_limit(req_a, max_attempts=5, window_seconds=60)
    rate_limit(req_b, max_attempts=5, window_seconds=60)  # different IP, should not raise


def test_window_expiry_resets_the_limit():
    req = _FakeRequest("5.5.5.5")
    _attempts["5.5.5.5"] = [time.time() - 100]  # old attempt, outside a 60s window
    rate_limit(req, max_attempts=1, window_seconds=60)  # should not raise — old attempt expired
