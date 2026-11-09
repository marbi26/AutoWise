import pytest
import uuid

def test_user_registration(client):
    unique_email = f"user_{uuid.uuid4().hex[:8]}@autowise.test"
    username = f"testuser_{uuid.uuid4().hex[:6]}"
    payload = {
        "email": unique_email,
        "username": username,
        "full_name": "Test Driver",
        "password": "StrongPassword123!"
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code in [200, 201]
    data = response.json()
    assert "user" in data
    assert data["user"]["email"] == unique_email
    assert "id" in data["user"]
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_duplicate_user_registration(client):
    unique_email = f"dup_{uuid.uuid4().hex[:8]}@autowise.test"
    username = f"dup_{uuid.uuid4().hex[:6]}"
    payload = {
        "email": unique_email,
        "username": username,
        "full_name": "Duplicate User",
        "password": "StrongPassword123!"
    }
    r1 = client.post("/api/auth/register", json=payload)
    assert r1.status_code in [200, 201]

    r2 = client.post("/api/auth/register", json=payload)
    assert r2.status_code == 400
    assert "already registered" in r2.json()["detail"].lower()

def test_user_login_success_and_failure(client):
    unique_email = f"auth_{uuid.uuid4().hex[:8]}@autowise.test"
    username = f"auth_{uuid.uuid4().hex[:6]}"
    password = "CorrectPassword123!"

    # Register first
    client.post("/api/auth/register", json={
        "email": unique_email,
        "username": username,
        "full_name": "Auth Tester",
        "password": password
    })

    # Test login with correct credentials
    login_res = client.post("/api/auth/login", json={
        "username": username,
        "password": password
    })
    assert login_res.status_code == 200
    login_data = login_res.json()
    assert "access_token" in login_data
    assert login_data["user"]["username"] == username

    # Test login with wrong password
    bad_login = client.post("/api/auth/login", json={
        "username": username,
        "password": "WrongPassword123!"
    })
    assert bad_login.status_code == 401

def test_authenticated_profile(client):
    unique_email = f"profile_{uuid.uuid4().hex[:8]}@autowise.test"
    username = f"prof_{uuid.uuid4().hex[:6]}"
    password = "ProfilePassword123!"

    reg = client.post("/api/auth/register", json={
        "email": unique_email,
        "username": username,
        "full_name": "Profile Owner",
        "password": password
    })
    token = reg.json()["access_token"]

    # Access without token
    unauth = client.get("/api/auth/profile")
    assert unauth.status_code in [401, 403]

    # Access with valid token
    auth_res = client.get("/api/auth/profile", headers={"Authorization": f"Bearer {token}"})
    assert auth_res.status_code == 200
    profile = auth_res.json()
    assert profile["email"] == unique_email
    assert profile["username"] == username
