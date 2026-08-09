def _admin_headers(client, email="scoping_admin@test.com"):
    resp = client.post("/api/v1/auth/register", json={
        "full_name": "Admin", "email": email, "password": "AdminPass123", "role": "admin",
    })
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


def test_regional_manager_registration_requires_region(client):
    resp = client.post("/api/v1/auth/register", json={
        "full_name": "No Region Mgr", "email": "noregion@test.com", "password": "RegionPass123",
        "role": "regional_manager",
    })
    assert resp.status_code == 400


def test_regional_manager_registration_rejects_unknown_region(client):
    resp = client.post("/api/v1/auth/register", json={
        "full_name": "Bad Region Mgr", "email": "badregion@test.com", "password": "RegionPass123",
        "role": "regional_manager", "region": "Atlantis",
    })
    assert resp.status_code == 400


def test_regional_manager_only_sees_own_region_outlets(client):
    admin_headers = _admin_headers(client)
    south_outlet = client.post("/api/v1/outlets", json={
        "name": "South Outlet", "code": "SOUTH-001", "city": "Chennai", "state": "Tamil Nadu", "region": "South",
    }, headers=admin_headers).json()
    north_outlet = client.post("/api/v1/outlets", json={
        "name": "North Outlet", "code": "NORTH-001", "city": "Delhi", "state": "Delhi", "region": "North",
    }, headers=admin_headers).json()

    mgr_resp = client.post("/api/v1/auth/register", json={
        "full_name": "South Mgr", "email": "southmgr@test.com", "password": "SouthPass123",
        "role": "regional_manager", "region": "South",
    })
    mgr_headers = {"Authorization": f"Bearer {mgr_resp.json()['access_token']}"}

    resp = client.get("/api/v1/outlets", headers=mgr_headers)
    assert resp.status_code == 200
    visible_ids = [o["id"] for o in resp.json()]
    assert south_outlet["id"] in visible_ids
    assert north_outlet["id"] not in visible_ids


def test_regional_manager_cannot_create_outlet_outside_own_region(client):
    mgr_resp = client.post("/api/v1/auth/register", json={
        "full_name": "South Mgr 2", "email": "southmgr2@test.com", "password": "SouthPass123",
        "role": "regional_manager", "region": "South",
    })
    mgr_headers = {"Authorization": f"Bearer {mgr_resp.json()['access_token']}"}

    resp = client.post("/api/v1/outlets", json={
        "name": "Wrong Region Outlet", "code": "WRONG-001", "city": "Mumbai", "state": "Maharashtra", "region": "West",
    }, headers=mgr_headers)
    assert resp.status_code == 403


def test_regional_manager_can_create_outlet_in_own_region(client):
    mgr_resp = client.post("/api/v1/auth/register", json={
        "full_name": "East Mgr", "email": "eastmgr@test.com", "password": "EastPass123",
        "role": "regional_manager", "region": "East",
    })
    mgr_headers = {"Authorization": f"Bearer {mgr_resp.json()['access_token']}"}

    resp = client.post("/api/v1/outlets", json={
        "name": "Correct Region Outlet", "code": "RIGHT-001", "city": "Kolkata", "state": "West Bengal", "region": "East",
    }, headers=mgr_headers)
    assert resp.status_code == 201


def test_admin_still_sees_all_outlets_across_regions(client):
    admin_headers = _admin_headers(client, "cross_region_admin@test.com")
    client.post("/api/v1/outlets", json={
        "name": "Region A Outlet", "code": "RA-001", "city": "Chennai", "state": "Tamil Nadu", "region": "South",
    }, headers=admin_headers)
    client.post("/api/v1/outlets", json={
        "name": "Region B Outlet", "code": "RB-001", "city": "Delhi", "state": "Delhi", "region": "North",
    }, headers=admin_headers)

    resp = client.get("/api/v1/outlets", headers=admin_headers)
    regions_seen = {o["region"] for o in resp.json()}
    assert "South" in regions_seen and "North" in regions_seen


def test_regional_manager_cannot_complete_audit_outside_region(client):
    admin_headers = _admin_headers(client, "audit_scope_admin@test.com")
    outlet = client.post("/api/v1/outlets", json={
        "name": "West Audit Outlet", "code": "WAO-001", "city": "Mumbai", "state": "Maharashtra", "region": "West",
    }, headers=admin_headers).json()
    audit = client.post("/api/v1/audits", json={
        "outlet_id": outlet["id"], "scheduled_date": "2026-08-01",
    }, headers=admin_headers).json()

    mgr_resp = client.post("/api/v1/auth/register", json={
        "full_name": "South Auditor Mgr", "email": "southauditmgr@test.com", "password": "SouthPass123",
        "role": "regional_manager", "region": "South",
    })
    mgr_headers = {"Authorization": f"Bearer {mgr_resp.json()['access_token']}"}

    resp = client.put(f"/api/v1/audits/{audit['id']}/complete",
                       json={"completed_date": "2026-08-05", "compliance_score": 90}, headers=mgr_headers)
    assert resp.status_code == 403
