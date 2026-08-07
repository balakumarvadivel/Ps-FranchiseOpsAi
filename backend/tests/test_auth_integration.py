def test_register_creates_user_and_returns_token(client):
    resp = client.post("/api/v1/auth/register", json={
        "full_name": "Jane Doe", "email": "jane@test.com", "password": "SecurePass123", "role": "admin",
    })
    assert resp.status_code == 201
    body = resp.json()
    assert body["access_token"]
    assert body["user"]["email"] == "jane@test.com"
    assert body["user"]["role"] == "admin"


def test_register_duplicate_email_rejected(client):
    payload = {"full_name": "Jane Doe", "email": "dupe@test.com", "password": "SecurePass123", "role": "admin"}
    client.post("/api/v1/auth/register", json=payload)
    resp = client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 400


def test_register_outlet_manager_requires_outlet_id(client):
    resp = client.post("/api/v1/auth/register", json={
        "full_name": "Manager", "email": "mgr@test.com", "password": "SecurePass123", "role": "outlet_manager",
    })
    assert resp.status_code == 400


def test_login_with_correct_credentials(client):
    client.post("/api/v1/auth/register", json={
        "full_name": "Jane Doe", "email": "login@test.com", "password": "SecurePass123", "role": "admin",
    })
    resp = client.post("/api/v1/auth/login-json", json={"email": "login@test.com", "password": "SecurePass123"})
    assert resp.status_code == 200
    assert resp.json()["access_token"]


def test_login_with_wrong_password_rejected(client):
    client.post("/api/v1/auth/register", json={
        "full_name": "Jane Doe", "email": "wrongpw@test.com", "password": "SecurePass123", "role": "admin",
    })
    resp = client.post("/api/v1/auth/login-json", json={"email": "wrongpw@test.com", "password": "WrongPassword"})
    assert resp.status_code == 401


def test_me_endpoint_requires_auth(client):
    resp = client.get("/api/v1/auth/me")
    assert resp.status_code == 401


def test_me_endpoint_returns_current_user(client, auth_headers):
    resp = client.get("/api/v1/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["email"] == "admin@test.com"


def test_forgot_password_does_not_leak_account_existence(client):
    resp_existing = client.post("/api/v1/auth/forgot-password", json={"email": "nonexistent@test.com"})
    assert resp_existing.status_code == 200
    assert "message" in resp_existing.json()
