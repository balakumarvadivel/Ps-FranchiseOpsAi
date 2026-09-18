"""
Rate limiting
--------------
A minimal in-memory sliding-window limiter for the auth endpoints
(login, register, forgot-password) — the ones worth protecting against
brute force even in a small deployment. This is intentionally NOT
Redis-backed: for a single-instance deployment (which is what render.yaml
provisions), an in-process dict is sufficient and adds zero infra
dependencies. If this app is ever run with multiple instances behind a
load balancer, swap this for a shared store (Redis) — an in-memory limiter
per-instance would let an attacker get N attempts per instance instead of
N total.
"""
import time
from collections import defaultdict

from fastapi import HTTPException, Request, status

# ip -> list of unix timestamps of recent attempts
_attempts: dict[str, list[float]] = defaultdict(list)


def rate_limit(request: Request, max_attempts: int = 10, window_seconds: int = 60):
    """
    FastAPI dependency: raises 429 if this client IP has made more than
    `max_attempts` requests to this dependency in the last `window_seconds`.
    """
    client_ip = request.client.host if request.client else "unknown"

    from app.config import settings
    if settings.ENV == "test" and client_ip in ("testclient", "127.0.0.1", "localhost"):
        return
    now = time.time()

    _attempts[client_ip] = [t for t in _attempts[client_ip] if now - t < window_seconds]

    if len(_attempts[client_ip]) >= max_attempts:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Too many attempts. Try again in {window_seconds} seconds.",
        )

    _attempts[client_ip].append(now)


def login_rate_limit(request: Request):
    rate_limit(request, max_attempts=10, window_seconds=60)


def register_rate_limit(request: Request):
    rate_limit(request, max_attempts=5, window_seconds=300)


def forgot_password_rate_limit(request: Request):
    rate_limit(request, max_attempts=3, window_seconds=300)
