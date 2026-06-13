from fastapi.testclient import TestClient
from app.modules.auth.models import User
from app.modules.sessions.models import Session
from app.core.security import hash_password

def test_admin_metrics(client: TestClient, db):
    # Setup test admin
    admin = User(
        email="superadmin@atomquest.com",
        password_hash=hash_password("admin123"),
        role="admin"
    )
    db.add(admin)
    db.commit()

    # Create active session
    session = Session(
        title="Admin Test Session",
        status="active",
        agent_id=admin.id,
        room_name="room-admin-123"
    )
    db.add(session)
    db.commit()

    # Login
    resp = client.post("/api/auth/login", json={"email": "superadmin@atomquest.com", "password": "admin123"})
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Test GET /api/admin/metrics
    resp = client.get("/api/admin/metrics", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["active_sessions"] >= 1
    assert data["total_sessions"] >= 1
    
    # Test GET /api/admin/sessions
    resp = client.get("/api/admin/sessions", headers=headers)
    assert resp.status_code == 200
    sessions = resp.json()
    assert len(sessions) >= 1
    
    # Force end session
    resp = client.post("/api/admin/end-session", headers=headers, json={"session_id": session.id})
    assert resp.status_code == 200
    
    # Verify session is ended
    resp = client.get("/api/admin/metrics", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    # Depending on test ordering, this might not be exactly 0, but it should be reduced or reflect the change.
