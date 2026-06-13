from fastapi.testclient import TestClient
from app.modules.auth.models import User
from app.core.security import hash_password

def test_login_success(client: TestClient, db):
    # Setup test user
    user = User(
        email="test@atomquest.com",
        password_hash=hash_password("password123"),
        role="agent"
    )
    db.add(user)
    db.commit()

    response = client.post("/api/auth/login", json={
        "email": "test@atomquest.com",
        "password": "password123"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "test@atomquest.com"
    assert data["user"]["role"] == "agent"

def test_login_failure(client: TestClient):
    response = client.post("/api/auth/login", json={
        "email": "wrong@atomquest.com",
        "password": "password123"
    })
    
    assert response.status_code == 401

def test_get_me(client: TestClient, db):
    # Setup test user
    user = User(
        email="test2@atomquest.com",
        password_hash=hash_password("password123"),
        role="admin"
    )
    db.add(user)
    db.commit()

    # Login to get token
    login_response = client.post("/api/auth/login", json={
        "email": "test2@atomquest.com",
        "password": "password123"
    })
    token = login_response.json()["access_token"]

    # Get /me
    response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test2@atomquest.com"
    assert data["role"] == "admin"
