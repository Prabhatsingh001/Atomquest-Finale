from fastapi.testclient import TestClient
from app.modules.auth.models import User
from app.modules.sessions.models import Session
from app.core.security import hash_password
import io

def test_uploads_endpoints(client: TestClient, db):
    # Setup test agent
    agent = User(
        email="upload_agent@atomquest.com",
        password_hash=hash_password("agent123"),
        role="agent"
    )
    db.add(agent)
    db.commit()

    # Create active session
    session = Session(
        title="Test Upload Session",
        status="active",
        agent_id=agent.id,
        room_name="room-upload-123"
    )
    db.add(session)
    db.commit()

    # Login
    resp = client.post("/api/auth/login", json={"email": "upload_agent@atomquest.com", "password": "agent123"})
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create a dummy file
    file_content = b"fake image content"
    files = {'file': ('test_image.png', file_content, 'image/png')}
    data = {'session_id': session.id}

    # Test upload
    resp = client.post("/api/uploads", headers=headers, data=data, files=files)
    assert resp.status_code == 200
    upload_data = resp.json()
    assert upload_data["file_name"] == "test_image.png"
    assert "download" in upload_data["file_url"]

    # Test list files
    resp = client.get(f"/api/uploads/session/{session.id}", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 1

    # Test download
    download_url = upload_data["file_url"]
    resp = client.get(download_url)
    assert resp.status_code == 200
    assert resp.content == file_content
