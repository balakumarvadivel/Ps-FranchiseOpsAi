def test_permissions_list_requires_auth(client):
    resp = client.get("/api/v1/permissions")
    assert resp.status_code == 401


def test_admin_sees_all_permissions_in_matrix(client, auth_headers):
    resp = client.get("/api/v1/permissions/matrix", headers=auth_headers)
    assert resp.status_code == 200
    admin_row = next(r for r in resp.json() if r["role"] == "admin")
    assert "outlets.write" in admin_row["permissions"]
    assert "users.manage" in admin_row["permissions"]


def test_outlet_manager_row_excludes_users_manage(client, auth_headers):
    resp = client.get("/api/v1/permissions/matrix", headers=auth_headers)
    outlet_mgr_row = next(r for r in resp.json() if r["role"] == "outlet_manager")
    assert "users.manage" not in outlet_mgr_row["permissions"]


def test_non_admin_cannot_update_permission_matrix(client):
    reg = client.post("/api/v1/auth/register", json={
        "full_name": "Regional Mgr", "email": "regional@test.com", "password": "RegionalPass123",
        "role": "regional_manager", "region": "South",
    })
    headers = {"Authorization": f"Bearer {reg.json()['access_token']}"}
    resp = client.put("/api/v1/permissions/matrix/outlet_manager",
                       json={"permission_codes": ["outlets.read"]}, headers=headers)
    assert resp.status_code == 403


def test_admin_can_update_permission_matrix(client, auth_headers):
    resp = client.put("/api/v1/permissions/matrix/outlet_manager",
                       json={"permission_codes": ["outlets.read"]}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["permissions"] == ["outlets.read"]


def test_update_matrix_rejects_unknown_permission_code(client, auth_headers):
    resp = client.put("/api/v1/permissions/matrix/outlet_manager",
                       json={"permission_codes": ["not.a.real.permission"]}, headers=auth_headers)
    assert resp.status_code == 400


def test_list_regions(client, auth_headers):
    resp = client.get("/api/v1/permissions/regions", headers=auth_headers)
    assert resp.status_code == 200
    names = [r["name"] for r in resp.json()]
    assert "South" in names and "North" in names
