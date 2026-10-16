from datetime import date, timedelta

from app.services import add_months


def test_create_member_computes_end_date(client, member, plan):
    assert member["plan_name"] == "Monthly"
    assert member["trainer_name"] == "Rohit Sharma"
    assert member["status"] == "ACTIVE"
    assert member["end_date"] == add_months(date.today(), plan["duration_months"]).isoformat()


def test_member_requires_existing_plan(client):
    response = client.post(
        "/api/members", json={"full_name": "No Plan", "email": "noplan@example.com", "plan_id": 999}
    )
    assert response.status_code == 422


def test_member_email_must_be_valid(client, plan):
    response = client.post(
        "/api/members", json={"full_name": "Bad Email", "email": "not-an-email", "plan_id": plan["id"]}
    )
    assert response.status_code == 422


def test_duplicate_member_email_conflicts(client, member, plan):
    response = client.post(
        "/api/members",
        json={"full_name": "Copy Cat", "email": "HIMANSHU@example.com", "plan_id": plan["id"]},
    )
    assert response.status_code == 409


def test_member_with_past_start_is_expired(client, plan):
    old_start = (date.today() - timedelta(days=90)).isoformat()
    created = client.post(
        "/api/members",
        json={"full_name": "Old Member", "email": "old@example.com", "plan_id": plan["id"], "start_date": old_start},
    ).json()
    assert created["membership_state"] == "EXPIRED"
    assert created["days_left"] == 0

    expired = client.get("/api/members", params={"state": "EXPIRED"}).json()
    assert [m["email"] for m in expired] == ["old@example.com"]


def test_search_members(client, member):
    assert len(client.get("/api/members", params={"q": "himan"}).json()) == 1
    assert client.get("/api/members", params={"q": "nobody"}).json() == []


def test_update_member_status_to_frozen(client, member):
    response = client.put(f"/api/members/{member['id']}", json={"status": "FROZEN", "phone": "8888888888"})
    assert response.status_code == 200
    assert response.json()["membership_state"] == "FROZEN"
    assert response.json()["phone"] == "8888888888"


def test_renew_extends_membership(client, member):
    renewed = client.post(f"/api/members/{member['id']}/renew").json()
    expected = add_months(date.fromisoformat(member["end_date"]), 1)
    assert renewed["end_date"] == expected.isoformat()


def test_delete_member(client, member):
    assert client.delete(f"/api/members/{member['id']}").status_code == 204
    assert client.get(f"/api/members/{member['id']}").status_code == 404


def test_add_months_clamps_month_end():
    assert add_months(date(2026, 1, 31), 1) == date(2026, 2, 28)
    assert add_months(date(2026, 11, 15), 3) == date(2027, 2, 15)
