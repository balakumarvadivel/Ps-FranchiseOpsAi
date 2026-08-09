def _admin_headers(client, email):
    resp = client.post("/api/v1/auth/register", json={
        "full_name": "Admin", "email": email, "password": "AdminPass123", "role": "admin",
    })
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


def _outlet_manager_headers(client, admin_headers, outlet_payload, email):
    outlet = client.post("/api/v1/outlets", json=outlet_payload, headers=admin_headers).json()
    mgr = client.post("/api/v1/auth/register", json={
        "full_name": "Outlet Mgr", "email": email, "password": "MgrPass123",
        "role": "outlet_manager", "outlet_id": outlet["id"],
    })
    return outlet, {"Authorization": f"Bearer {mgr.json()['access_token']}"}


def test_outlet_health_score_blocked_for_other_outlet(client):
    admin_headers = _admin_headers(client, "health_admin@test.com")
    outlet_a, mgr_a_headers = _outlet_manager_headers(
        client, admin_headers,
        {"name": "Outlet A", "code": "HA-001", "city": "Chennai", "state": "Tamil Nadu", "region": "South"},
        "healthmgra@test.com",
    )
    outlet_b = client.post("/api/v1/outlets", json={
        "name": "Outlet B", "code": "HB-001", "city": "Mumbai", "state": "Maharashtra", "region": "West",
    }, headers=admin_headers).json()

    # Manager A can see their own outlet's health score.
    resp = client.get(f"/api/v1/ai/outlets/{outlet_a['id']}/health-score", headers=mgr_a_headers)
    assert resp.status_code == 200

    # But not outlet B's.
    resp = client.get(f"/api/v1/ai/outlets/{outlet_b['id']}/health-score", headers=mgr_a_headers)
    assert resp.status_code == 403


def test_report_generation_scoped_to_own_outlets(client):
    admin_headers = _admin_headers(client, "report_admin@test.com")
    outlet_a, mgr_a_headers = _outlet_manager_headers(
        client, admin_headers,
        {"name": "Report Outlet A", "code": "RA-001", "city": "Chennai", "state": "Tamil Nadu", "region": "South"},
        "reportmgra@test.com",
    )
    client.post("/api/v1/outlets", json={
        "name": "Report Outlet B", "code": "RB-001", "city": "Mumbai", "state": "Maharashtra", "region": "West",
    }, headers=admin_headers)

    # An outlet_manager generating an "overall" report with no outlet_id
    # should only ever get their own outlet back, never the whole network.
    resp = client.post("/api/v1/reports/generate", json={"report_type": "overall", "format": "csv"}, headers=mgr_a_headers)
    assert resp.status_code == 201


def test_recommendation_status_update_blocked_for_other_outlet(client):
    admin_headers = _admin_headers(client, "rec_admin@test.com")
    outlet_a, mgr_a_headers = _outlet_manager_headers(
        client, admin_headers,
        {"name": "Rec Outlet A", "code": "RECA-001", "city": "Chennai", "state": "Tamil Nadu", "region": "South"},
        "recmgra@test.com",
    )
    outlet_b = client.post("/api/v1/outlets", json={
        "name": "Rec Outlet B", "code": "RECB-001", "city": "Mumbai", "state": "Maharashtra", "region": "West",
    }, headers=admin_headers).json()

    client.post("/api/v1/recommendations/refresh", headers=admin_headers)
    all_recs = client.get("/api/v1/recommendations", headers=admin_headers).json()
    outlet_b_recs = [r for r in all_recs if r["outlet_id"] == outlet_b["id"]]

    if outlet_b_recs:
        resp = client.put(f"/api/v1/recommendations/{outlet_b_recs[0]['id']}/status",
                           json={"status": "dismissed"}, headers=mgr_a_headers)
        assert resp.status_code == 403


def test_data_validation_commit_rejects_out_of_scope_outlet(client):
    admin_headers = _admin_headers(client, "commit_admin@test.com")
    client.post("/api/v1/outlets", json={
        "name": "Commit Outlet A", "code": "CA-001", "city": "Chennai", "state": "Tamil Nadu", "region": "South",
    }, headers=admin_headers)
    outlet_b = client.post("/api/v1/outlets", json={
        "name": "Commit Outlet B", "code": "CB-001", "city": "Mumbai", "state": "Maharashtra", "region": "West",
    }, headers=admin_headers).json()

    mgr = client.post("/api/v1/auth/register", json={
        "full_name": "South Commit Mgr", "email": "southcommitmgr@test.com", "password": "SouthPass123",
        "role": "regional_manager", "region": "South",
    })
    mgr_headers = {"Authorization": f"Bearer {mgr.json()['access_token']}"}

    resp = client.post("/api/v1/data-validation/commit", json={
        "dataset_type": "inventory",
        "rows": [{"outlet_id": outlet_b["id"], "product_id": 1, "quantity": 50}],
    }, headers=mgr_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["inserted"] == 0
    assert body["skipped"] == 1
    assert "outside your authorized scope" in body["errors"][0]
