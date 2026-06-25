import pytest
import datetime
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")

@pytest.fixture
def auth_user(client):
    # Register and login first user
    client.post("/signup", json={
        "name": "Alice Booking",
        "email": "alice@example.com",
        "password": "password123"
    })
    login_resp = client.post("/login", json={
        "email": "alice@example.com",
        "password": "password123"
    })
    token = login_resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def other_user(client):
    # Register and login second user
    client.post("/signup", json={
        "name": "Bob Booking",
        "email": "bob@example.com",
        "password": "password123"
    })
    login_resp = client.post("/login", json={
        "email": "bob@example.com",
        "password": "password123"
    })
    token = login_resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def setup_classes(client, auth_user):
    current_time_ist = datetime.datetime.now(IST)
    future_dt = (current_time_ist + datetime.timedelta(days=2)).isoformat()
    past_dt = (current_time_ist - datetime.timedelta(days=1)).isoformat()

    # Create an upcoming class with 2 slots
    class_future_resp = client.post("/classes", json={
        "name": "Spinning Masterclass",
        "dateTime": future_dt,
        "instructor": "John Taylor",
        "availableSlots": 2
    }, headers=auth_user)
    class_future_id = class_future_resp.json()["id"]

    # Create a past class
    class_past_resp = client.post("/classes", json={
        "name": "Yesterday Yoga",
        "dateTime": past_dt,
        "instructor": "Jane Smith",
        "availableSlots": 5
    }, headers=auth_user)
    class_past_id = class_past_resp.json()["id"]

    # Create a future class with 0 slots (full class)
    class_full_resp = client.post("/classes", json={
        "name": "Full Pilates",
        "dateTime": future_dt,
        "instructor": "Sarah Jenkins",
        "availableSlots": 0
    }, headers=auth_user)
    class_full_id = class_full_resp.json()["id"]

    return {
        "future_class_id": class_future_id,
        "past_class_id": class_past_id,
        "full_class_id": class_full_id
    }

def test_book_class_success(client, auth_user, setup_classes):
    class_id = setup_classes["future_class_id"]
    
    booking_payload = {
        "class_id": class_id,
        "client_name": "Alice",
        "client_email": "alice.booking@example.com"
    }

    # Book class
    response = client.post("/book", json=booking_payload, headers=auth_user)
    assert response.status_code == 201
    data = response.json()
    assert data["class_id"] == class_id
    assert data["client_name"] == "Alice"
    assert data["client_email"] == "alice.booking@example.com"
    assert "booking_id" in data
    assert "dateTime" in data
    assert "booked_at" in data

    # Verify that available slots in the class decremented from 2 to 1
    class_response = client.get("/classes")
    classes = class_response.json()
    target_class = next(c for c in classes if c["id"] == class_id)
    assert target_class["availableSlots"] == 1

def test_book_class_unauthenticated(client, setup_classes):
    class_id = setup_classes["future_class_id"]
    booking_payload = {
        "class_id": class_id,
        "client_name": "Alice",
        "client_email": "alice.booking@example.com"
    }
    response = client.post("/book", json=booking_payload)
    assert response.status_code == 401

def test_book_nonexistent_class(client, auth_user):
    booking_payload = {
        "class_id": 99999,
        "client_name": "Alice",
        "client_email": "alice.booking@example.com"
    }
    response = client.post("/book", json=booking_payload, headers=auth_user)
    assert response.status_code == 404
    assert response.json()["detail"] == "Class not found"

def test_book_past_class_error(client, auth_user, setup_classes):
    class_id = setup_classes["past_class_id"]
    booking_payload = {
        "class_id": class_id,
        "client_name": "Alice",
        "client_email": "alice.booking@example.com"
    }
    response = client.post("/book", json=booking_payload, headers=auth_user)
    assert response.status_code == 400
    assert "already started or passed" in response.json()["detail"]

def test_book_full_class_error(client, auth_user, setup_classes):
    class_id = setup_classes["full_class_id"]
    booking_payload = {
        "class_id": class_id,
        "client_name": "Alice",
        "client_email": "alice.booking@example.com"
    }
    response = client.post("/book", json=booking_payload, headers=auth_user)
    assert response.status_code == 400
    assert response.json()["detail"] == "No available slots in this class"

def test_book_duplicate_user_error(client, auth_user, setup_classes):
    class_id = setup_classes["future_class_id"]
    
    booking_payload = {
        "class_id": class_id,
        "client_name": "Alice One",
        "client_email": "alice.one@example.com"
    }
    
    # First booking succeeds
    client.post("/book", json=booking_payload, headers=auth_user)
    
    # Second booking by the same user fails
    duplicate_payload = {
        "class_id": class_id,
        "client_name": "Alice Two",
        "client_email": "alice.two@example.com"
    }
    response = client.post("/book", json=duplicate_payload, headers=auth_user)
    assert response.status_code == 400
    assert "already booked" in response.json()["detail"]

def test_book_duplicate_email_error(client, auth_user, other_user, setup_classes):
    class_id = setup_classes["future_class_id"]
    
    booking_payload = {
        "class_id": class_id,
        "client_name": "Alice One",
        "client_email": "shared@example.com"
    }
    
    # First user booking succeeds
    client.post("/book", json=booking_payload, headers=auth_user)
    
    # Second user booking with the same client email fails
    response = client.post("/book", json=booking_payload, headers=other_user)
    assert response.status_code == 400
    assert "email has already been used" in response.json()["detail"]

def test_get_user_bookings(client, auth_user, other_user, setup_classes):
    class_id = setup_classes["future_class_id"]

    # Book for first user
    client.post("/book", json={
        "class_id": class_id,
        "client_name": "Alice",
        "client_email": "alice@example.com"
    }, headers=auth_user)

    # Book for second user
    client.post("/book", json={
        "class_id": class_id,
        "client_name": "Bob",
        "client_email": "bob@example.com"
    }, headers=other_user)

    # Check bookings for first user
    auth_resp = client.get("/bookings", headers=auth_user)
    assert auth_resp.status_code == 200
    auth_bookings = auth_resp.json()
    assert len(auth_bookings) == 1
    assert auth_bookings[0]["client_name"] == "Alice"
    assert auth_bookings[0]["class_name"] == "Spinning Masterclass"

    # Check bookings for second user
    other_resp = client.get("/bookings", headers=other_user)
    assert other_resp.status_code == 200
    other_bookings = other_resp.json()
    assert len(other_bookings) == 1
    assert other_bookings[0]["client_name"] == "Bob"
