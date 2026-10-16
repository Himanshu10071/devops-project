def test_active_member_can_check_in(client, member):
    response = client.post("/api/checkins", json={"member_id": member["id"]})
    assert response.status_code == 201
    assert response.json()["member_name"] == "Himanshu Chauhan"

    history = client.get("/api/checkins", params={"member_id": member["id"]}).json()
    assert len(history) == 1


def test_frozen_member_cannot_check_in(client, member):
    client.put(f"/api/members/{member['id']}", json={"status": "FROZEN"})
    response = client.post("/api/checkins", json={"member_id": member["id"]})
    assert response.status_code == 400
    assert "frozen" in response.json()["detail"]


def test_check_in_unknown_member(client):
    assert client.post("/api/checkins", json={"member_id": 12345}).status_code == 404


def test_dashboard_stats(client, member, plan):
    client.post("/api/checkins", json={"member_id": member["id"]})
    client.post("/api/checkins", json={"member_id": member["id"]})

    stats = client.get("/api/dashboard/stats").json()

    assert stats["total_members"] == 1
    assert stats["active_members"] == 1
    assert stats["checkins_today"] == 2
    assert stats["trainers"] == 1
    assert stats["monthly_revenue"] == plan["price"]
    assert stats["plan_breakdown"] == [{"plan": "Monthly", "members": 1}]
