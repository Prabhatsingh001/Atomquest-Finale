from fastapi.testclient import TestClient
from app.modules.auth.models import User
from app.modules.sessions.models import Session
from app.core.security import hash_password

def test_create_session(client: TestClient, db):
    # Setup agent
    agent = User(
        email="agent_test_session@atomquest.com",
        password_hash=hash_password("agent123"),
        role="agent"
    )
    db.add(agent)
    db.commit()

    # Login
    resp = client.post("/api/auth/login", json={"email": "agent_test_session@atomquest.com", "password": "agent123"})
    token = resp.json()["access_token"]

    # Create Session
    resp = client.post("/api/sessions", json={"title": "Test Session"}, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "Test Session"
    assert "room_name" in data
    assert "join_token" in data

def test_customer_join(client: TestClient, db):
    # Setup session
    session = Session(
        title="Test Customer Join",
        room_name="room-1234",
        agent_id=1,
        join_token="secret-token-123"
    )
    db.add(session)
    db.commit()

    # Join
    resp = client.post(f"/api/participants/join/{session.join_token}", json={"name": "John Doe"})
    assert resp.status_code == 200
    data = resp.json()
    assert "livekit_token" in data
    assert data["room_name"] == "room-1234"
    assert data["identity"].startswith("customer-")
