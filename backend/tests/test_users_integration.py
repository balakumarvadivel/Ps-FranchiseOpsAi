def test_list_users_requires_admin_or_regional_manager(client):
    outlet_mgr_resp = client.post("/api/v1/auth/register", json={
        "full_name": "Basic User", "email": "basic@test.com", "password": "BasicPass123",
        "role": "outlet_manager", "outlet_id": 1,
    })
    headers = {"Authorization": f"Bearer {outlet_mgr_resp.json()['access_token']}"}
    resp = client.get("/api/v1/users", headers=headers)
    assert resp.status_code == 403


def test_admin_can_list_users(client, auth_headers):
    resp = client.get("/api/v1/users", headers=auth_headers)
    assert resp.status_code == 200
    assert any(u["email"] == "admin@test.com" for u in resp.json())


def test_admin_can_update_user_role(client, auth_headers):
    reg_resp = client.post("/api/v1/auth/register", json={
        "full_name": "Promote Me", "email": "promote@test.com", "password": "PromotePass123", "role": "admin",
    })
    user_id = reg_resp.json()["user"]["id"]

    resp = client.put(f"/api/v1/users/{user_id}", json={"role": "regional_manager"}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["role"] == "regional_manager"


def test_admin_can_deactivate_user(client, auth_headers):
    reg_resp = client.post("/api/v1/auth/register", json={
        "full_name": "Deactivate Me", "email": "deactivate@test.com", "password": "DeactPass123", "role": "admin",
    })
    user_id = reg_resp.json()["user"]["id"]

    resp = client.delete(f"/api/v1/users/{user_id}", headers=auth_headers)
    assert resp.status_code == 204

    login_resp = client.post("/api/v1/auth/login-json", json={"email": "deactivate@test.com", "password": "DeactPass123"})
    assert login_resp.status_code == 403


def test_update_nonexistent_user_404(client, auth_headers):
    resp = client.put("/api/v1/users/99999", json={"full_name": "Nobody"}, headers=auth_headers)
    assert resp.status_code == 404
