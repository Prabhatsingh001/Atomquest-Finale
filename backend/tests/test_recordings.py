from fastapi.testclient import TestClient
from app.modules.auth.models import User
from app.core.security import hash_password
from app.modules.sessions.models import Session
from app.modules.recordings.models import Recording, RecordingStatus

def test_recordings_endpoints(client: TestClient, db):
    # Setup test agent
    agent = User(
        email="record_agent@atomquest.com",
        password_hash=hash_password("agent123"),
        role="agent"
    )
    db.add(agent)
    db.commit()

    # Create active session
    session = Session(
        title="Test Recording Session",
        status="active",
        agent_id=agent.id,
        room_name="room-record-123"
    )
    db.add(session)
    db.commit()

    # Login
    resp = client.post("/api/auth/login", json={"email": "record_agent@atomquest.com", "password": "agent123"})
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # We cannot test /start easily because livekit_service requires a real LiveKit server running
    # but we can mock it or just insert a recording and test the GET endpoints.

    recording = Recording(
        session_id=session.id,
        status=RecordingStatus.recording,
        livekit_egress_id="eg_12345"
    )
    db.add(recording)
    db.commit()

    # Test GET /api/recordings/session/{session_id}
    resp = client.get(f"/api/recordings/session/{session.id}", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert "livekit_egress_id" not in data[0] # We don't expose egress id in response schema
    assert data[0]["status"] == "recording"

    # Test GET /api/recordings/{id}
    resp = client.get(f"/api/recordings/{recording.id}", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == recording.id
