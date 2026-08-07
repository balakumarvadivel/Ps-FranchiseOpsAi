def test_create_and_list_outlet(client, auth_headers):
    resp = client.post("/api/v1/outlets", json={
        "name": "Test Outlet", "code": "TST-001", "city": "Chennai", "state": "Tamil Nadu", "region": "South",
    }, headers=auth_headers)
    assert resp.status_code == 201
    outlet_id = resp.json()["id"]

    resp = client.get("/api/v1/outlets", headers=auth_headers)
    assert resp.status_code == 200
    assert any(o["id"] == outlet_id for o in resp.json())


def test_create_outlet_duplicate_code_rejected(client, auth_headers):
    payload = {"name": "Outlet A", "code": "DUP-001", "city": "Chennai", "state": "Tamil Nadu", "region": "South"}
    client.post("/api/v1/outlets", json=payload, headers=auth_headers)
    resp = client.post("/api/v1/outlets", json=payload, headers=auth_headers)
    assert resp.status_code == 400


def test_update_outlet(client, auth_headers):
    resp = client.post("/api/v1/outlets", json={
        "name": "Old Name", "code": "UPD-001", "city": "Mumbai", "state": "Maharashtra", "region": "West",
    }, headers=auth_headers)
    outlet_id = resp.json()["id"]

    resp = client.put(f"/api/v1/outlets/{outlet_id}", json={"name": "New Name"}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["name"] == "New Name"


def test_get_nonexistent_outlet_404(client, auth_headers):
    resp = client.get("/api/v1/outlets/9999", headers=auth_headers)
    assert resp.status_code == 404


def test_outlet_creation_requires_auth(client):
    resp = client.post("/api/v1/outlets", json={
        "name": "No Auth", "code": "NOA-001", "city": "Delhi", "state": "Delhi", "region": "North",
    })
    assert resp.status_code == 401


def test_outlet_manager_cannot_create_outlet(client):
    # Register an outlet first as admin to attach the outlet_manager to.
    admin_resp = client.post("/api/v1/auth/register", json={
        "full_name": "Admin", "email": "admin2@test.com", "password": "AdminPass123", "role": "admin",
    })
    admin_headers = {"Authorization": f"Bearer {admin_resp.json()['access_token']}"}
    outlet_resp = client.post("/api/v1/outlets", json={
        "name": "Scoped Outlet", "code": "SCP-001", "city": "Pune", "state": "Maharashtra", "region": "West",
    }, headers=admin_headers)
    outlet_id = outlet_resp.json()["id"]

    manager_resp = client.post("/api/v1/auth/register", json={
        "full_name": "Outlet Mgr", "email": "outletmgr@test.com", "password": "MgrPass123",
        "role": "outlet_manager", "outlet_id": outlet_id,
    })
    manager_headers = {"Authorization": f"Bearer {manager_resp.json()['access_token']}"}

    resp = client.post("/api/v1/outlets", json={
        "name": "Should Fail", "code": "FAIL-001", "city": "Pune", "state": "Maharashtra", "region": "West",
    }, headers=manager_headers)
    assert resp.status_code == 403


def test_outlet_manager_only_sees_own_outlet(client):
    admin_resp = client.post("/api/v1/auth/register", json={
        "full_name": "Admin", "email": "admin3@test.com", "password": "AdminPass123", "role": "admin",
    })
    admin_headers = {"Authorization": f"Bearer {admin_resp.json()['access_token']}"}

    outlet_a = client.post("/api/v1/outlets", json={
        "name": "Outlet A", "code": "A-001", "city": "Chennai", "state": "Tamil Nadu", "region": "South",
    }, headers=admin_headers).json()
    outlet_b = client.post("/api/v1/outlets", json={
        "name": "Outlet B", "code": "B-001", "city": "Chennai", "state": "Tamil Nadu", "region": "South",
    }, headers=admin_headers).json()

    manager_resp = client.post("/api/v1/auth/register", json={
        "full_name": "Mgr A", "email": "mgra@test.com", "password": "MgrPass123",
        "role": "outlet_manager", "outlet_id": outlet_a["id"],
    })
    manager_headers = {"Authorization": f"Bearer {manager_resp.json()['access_token']}"}

    resp = client.get("/api/v1/outlets", headers=manager_headers)
    assert resp.status_code == 200
    visible_ids = [o["id"] for o in resp.json()]
    assert outlet_a["id"] in visible_ids
    assert outlet_b["id"] not in visible_ids
