import pytest
from fastapi.testclient import TestClient
from app.modules.auth.models import User
from app.core.security import hash_password
from app.modules.sessions.models import Session
from app.modules.participants.models import Participant
from app.modules.chat.models import Message

def test_history_endpoints(client: TestClient, db):
    # Setup test agent
    agent = User(
        email="history_agent@atomquest.com",
        password_hash=hash_password("agent123"),
        role="agent"
    )
    db.add(agent)
    db.commit()

    # Create an ended session
    session = Session(
        title="Test Ended Session",
        status="completed",
        agent_id=agent.id,
        room_name="room-history-123"
    )
    db.add(session)
    db.commit()
    
    # Add participants
    part1 = Participant(
        session_id=session.id,
        user_id=agent.id,
        identity="agent_123",
        name="Agent History"
    )
    db.add(part1)
    db.commit()
    
    # Add messages
    msg1 = Message(
        session_id=session.id,
        sender_id=agent.id,
        content="Hello, history"
    )
    db.add(msg1)
    db.commit()

    # Login
    resp = client.post("/api/auth/login", json={"email": "history_agent@atomquest.com", "password": "agent123"})
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Test GET /api/sessions with status=completed filter
    resp = client.get("/api/sessions?status=completed", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1
    assert data[0]["status"] == "completed"

    # 2. Test GET /api/sessions/{session_id} for details (stats included)
    resp = client.get(f"/api/sessions/{session.id}", headers=headers)
    assert resp.status_code == 200
    detail_data = resp.json()
    assert detail_data["message_count"] == 1
    assert len(detail_data["participants"]) == 1
    assert detail_data["participants"][0]["name"] == "Agent History"
