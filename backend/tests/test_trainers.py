def test_trainer_crud(client):
    created = client.post("/api/trainers", json={"name": "Priya Nair", "specialization": "Yoga"}).json()
    assert created["member_count"] == 0

    updated = client.put(f"/api/trainers/{created['id']}", json={"experience_years": 7}).json()
    assert updated["experience_years"] == 7
    assert updated["specialization"] == "Yoga"

    assert client.delete(f"/api/trainers/{created['id']}").status_code == 204
    assert client.get(f"/api/trainers/{created['id']}").status_code == 404


def test_trainer_member_count(client, member):
    trainers = client.get("/api/trainers").json()
    assert trainers[0]["member_count"] == 1


def test_deleting_trainer_unassigns_members(client, member):
    client.delete(f"/api/trainers/{member['trainer_id']}")

    refreshed = client.get(f"/api/members/{member['id']}").json()
    assert refreshed["trainer_id"] is None
    assert refreshed["trainer_name"] is None
