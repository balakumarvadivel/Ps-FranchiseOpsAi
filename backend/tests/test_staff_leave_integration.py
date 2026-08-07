def _create_outlet_and_employee(client, headers):
    outlet = client.post("/api/v1/outlets", json={
        "name": "Leave Test Outlet", "code": "LV-001", "city": "Chennai", "state": "Tamil Nadu", "region": "South",
    }, headers=headers).json()
    employee = client.post("/api/v1/staff/employees", json={
        "outlet_id": outlet["id"], "full_name": "Test Employee", "designation": "Cashier",
    }, headers=headers).json()
    return outlet, employee


def test_request_leave(client, auth_headers):
    _, employee = _create_outlet_and_employee(client, auth_headers)
    resp = client.post("/api/v1/staff/leave", json={
        "employee_id": employee["id"], "leave_type": "casual",
        "start_date": "2026-08-10", "end_date": "2026-08-12", "reason": "Family event",
    }, headers=auth_headers)
    assert resp.status_code == 201
    assert resp.json()["status"] == "pending"


def test_leave_end_before_start_rejected(client, auth_headers):
    _, employee = _create_outlet_and_employee(client, auth_headers)
    resp = client.post("/api/v1/staff/leave", json={
        "employee_id": employee["id"], "start_date": "2026-08-12", "end_date": "2026-08-10",
    }, headers=auth_headers)
    assert resp.status_code == 400


def test_list_leave_requests(client, auth_headers):
    _, employee = _create_outlet_and_employee(client, auth_headers)
    client.post("/api/v1/staff/leave", json={
        "employee_id": employee["id"], "start_date": "2026-08-10", "end_date": "2026-08-11",
    }, headers=auth_headers)
    resp = client.get("/api/v1/staff/leave", headers=auth_headers)
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


def test_approve_leave_request(client, auth_headers):
    _, employee = _create_outlet_and_employee(client, auth_headers)
    leave = client.post("/api/v1/staff/leave", json={
        "employee_id": employee["id"], "start_date": "2026-08-10", "end_date": "2026-08-11",
    }, headers=auth_headers).json()

    resp = client.put(f"/api/v1/staff/leave/{leave['id']}/decision", json={"status": "approved"}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "approved"


def test_record_and_list_payroll(client, auth_headers):
    _, employee = _create_outlet_and_employee(client, auth_headers)
    resp = client.post("/api/v1/staff/payroll", json={
        "employee_id": employee["id"], "month": "2026-08-01", "base_salary": 25000, "overtime_pay": 1500, "deductions": 500,
    }, headers=auth_headers)
    assert resp.status_code == 201
    assert resp.json()["net_pay"] == 26000

    list_resp = client.get("/api/v1/staff/payroll", headers=auth_headers)
    assert list_resp.status_code == 200
    assert any(p["employee_id"] == employee["id"] for p in list_resp.json())


def test_schedule_and_list_shifts(client, auth_headers):
    _, employee = _create_outlet_and_employee(client, auth_headers)
    resp = client.post("/api/v1/staff/shifts", json={
        "employee_id": employee["id"], "shift_date": "2026-08-10", "start_time": "09:00:00", "end_time": "17:00:00",
    }, headers=auth_headers)
    assert resp.status_code == 201

    list_resp = client.get("/api/v1/staff/shifts", headers=auth_headers)
    assert list_resp.status_code == 200
    assert any(s["employee_id"] == employee["id"] for s in list_resp.json())
