from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

def get_auth_token():
    # Sign up
    client.post("/auth/signup", json={"username": "testuser", "password": "testpass"})
    # Login
    response = client.post("/auth/login", json={"username": "testuser", "password": "testpass"})
    return response.json()["access_token"]

def test_create_and_read_contact() -> None:
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.post("/contacts", headers=headers, json={
        "name": "Alex Example",
        "company": "OpenCLAW Labs",
        "email": "alex@example.com",
        "tags": "network,events",
        "priority": "high",
    })
    assert response.status_code == 200
    contact = response.json()
    assert contact["name"] == "Alex Example"
    assert contact["company"] == "OpenCLAW Labs"
    assert contact["priority"] == "high"

    read_response = client.get(f"/contacts/{contact['id']}", headers=headers)
    assert read_response.status_code == 200
    assert read_response.json()["id"] == contact["id"]


def test_add_interaction() -> None:
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    contact_resp = client.post("/contacts", headers=headers, json={"name": "Test User"})
    contact_id = contact_resp.json()["id"]

    interaction_resp = client.post(
        f"/contacts/{contact_id}/interactions",
        headers=headers,
        json={
            "date": "2026-05-07T10:30:00",
            "type": "meeting",
            "notes": "Discussed project ideas",
            "follow_up": True,
            "follow_up_notes": "Send the intro email next week",
        },
    )
    assert interaction_resp.status_code == 200
    interaction = interaction_resp.json()
    assert interaction["contact_id"] == contact_id
    assert interaction["type"] == "meeting"
    assert interaction["date"].startswith("2026-05-07T10:30:00")
    assert interaction["follow_up"] is True
    assert interaction["follow_up_notes"] == "Send the intro email next week"

    list_resp = client.get("/contacts", headers=headers)
    assert list_resp.status_code == 200
    listed_contact = next(contact for contact in list_resp.json() if contact["id"] == contact_id)
    assert listed_contact["follow_up_needed"] is True
