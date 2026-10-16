def test_create_and_list_plans(client):
    client.post("/api/plans", json={"name": "Annual", "duration_months": 12, "price": 13000})
    client.post("/api/plans", json={"name": "Monthly", "duration_months": 1, "price": 1500})

    plans = client.get("/api/plans").json()

    assert [p["name"] for p in plans] == ["Monthly", "Annual"]  # ordered by duration


def test_plan_validation_rejects_bad_duration(client):
    response = client.post("/api/plans", json={"name": "Broken", "duration_months": 0, "price": 100})
    assert response.status_code == 422


def test_duplicate_plan_name_conflicts(client, plan):
    response = client.post("/api/plans", json={"name": "monthly", "duration_months": 1, "price": 999})
    assert response.status_code == 409


def test_update_plan_price(client, plan):
    response = client.put(f"/api/plans/{plan['id']}", json={"price": 1800})
    assert response.status_code == 200
    assert response.json()["price"] == 1800
    assert response.json()["name"] == "Monthly"


def test_cannot_delete_plan_in_use(client, member):
    response = client.delete(f"/api/plans/{member['plan_id']}")
    assert response.status_code == 409


def test_delete_unused_plan(client, plan):
    assert client.delete(f"/api/plans/{plan['id']}").status_code == 204
    assert client.get(f"/api/plans/{plan['id']}").status_code == 404
