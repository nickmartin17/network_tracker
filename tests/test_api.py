from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_create_and_read_contact() -> None:
    response = client.post("/contacts", json={
        "name": "Alex Example",
        "company": "OpenCLAW Labs",
        "email": "alex@example.com",
        "tags": "network,events",
    })
    assert response.status_code == 200
    contact = response.json()
    assert contact["name"] == "Alex Example"
    assert contact["company"] == "OpenCLAW Labs"

    read_response = client.get(f"/contacts/{contact['id']}")
    assert read_response.status_code == 200
    assert read_response.json()["id"] == contact["id"]


def test_add_interaction() -> None:
    contact_resp = client.post("/contacts", json={"name": "Test User"})
    contact_id = contact_resp.json()["id"]

    interaction_resp = client.post(
        f"/contacts/{contact_id}/interactions",
        json={"type": "meeting", "notes": "Discussed project ideas", "follow_up": True},
    )
    assert interaction_resp.status_code == 200
    interaction = interaction_resp.json()
    assert interaction["contact_id"] == contact_id
    assert interaction["type"] == "meeting"
