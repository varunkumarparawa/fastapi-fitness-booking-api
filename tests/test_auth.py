import pytest

def test_signup_success(client):
    payload = {
        "name": "Jane Doe",
        "email": "jane@example.com",
        "password": "securepassword123"
    }
    response = client.post("/signup", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Jane Doe"
    assert data["email"] == "jane@example.com"
    assert "id" in data
    assert "password" not in data  # Ensure raw password is not leaked

def test_signup_duplicate_email(client):
    payload = {
        "name": "Jane Doe",
        "email": "jane@example.com",
        "password": "securepassword123"
    }
    client.post("/signup", json=payload)
    
    # Attempt second registration
    response = client.post("/signup", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"

def test_signup_invalid_email(client):
    payload = {
        "name": "Jane Doe",
        "email": "not-an-email",
        "password": "securepassword123"
    }
    response = client.post("/signup", json=payload)
    assert response.status_code == 422
    assert "errors" in response.json()

def test_signup_password_too_short(client):
    payload = {
        "name": "Jane Doe",
        "email": "jane@example.com",
        "password": "123"
    }
    response = client.post("/signup", json=payload)
    assert response.status_code == 422
    assert "errors" in response.json()

def test_login_success(client):
    # First signup
    signup_payload = {
        "name": "Jane Doe",
        "email": "jane@example.com",
        "password": "securepassword123"
    }
    client.post("/signup", json=signup_payload)

    # Then login
    login_payload = {
        "email": "jane@example.com",
        "password": "securepassword123"
    }
    response = client.post("/login", json=login_payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_credentials(client):
    login_payload = {
        "email": "doesnotexist@example.com",
        "password": "wrongpassword"
    }
    response = client.post("/login", json=login_payload)
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"
