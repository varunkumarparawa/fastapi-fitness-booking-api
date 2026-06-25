import pytest
import datetime
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")

@pytest.fixture
def auth_header(client):
    # Signup and login to get access token
    client.post("/signup", json={
        "name": "Trainer Joe",
        "email": "joe@example.com",
        "password": "password123"
    })
    response = client.post("/login", json={
        "email": "joe@example.com",
        "password": "password123"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_create_class_unauthenticated(client):
    payload = {
        "name": "Power Yoga",
        "dateTime": "2025-06-15T10:00:00Z",
        "instructor": "John Doe",
        "availableSlots": 20
    }
    response = client.post("/classes", json=payload)
    assert response.status_code == 401

def test_create_class_success(client, auth_header):
    # Send dateTime in UTC (denoted by 'Z')
    payload = {
        "name": "Power Yoga",
        "dateTime": "2025-06-15T10:00:00Z",
        "instructor": "John Doe",
        "availableSlots": 20
    }
    response = client.post("/classes", json=payload, headers=auth_header)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Power Yoga"
    assert data["instructor"] == "John Doe"
    assert data["availableSlots"] == 20
    
    # 2025-06-15T10:00:00Z in IST is 2025-06-15T15:30:00+05:30
    assert data["dateTime"] == "2025-06-15T15:30:00+05:30"

def test_get_upcoming_classes_only(client, auth_header):
    current_time_ist = datetime.datetime.now(IST)
    
    # Define past and future class dateTimes
    past_dt = (current_time_ist - datetime.timedelta(hours=2)).isoformat()
    future_dt_1 = (current_time_ist + datetime.timedelta(days=1)).isoformat()
    future_dt_2 = (current_time_ist + datetime.timedelta(days=2)).isoformat()

    # Create past class
    client.post("/classes", json={
        "name": "Past Class",
        "dateTime": past_dt,
        "instructor": "Jane Smith",
        "availableSlots": 10
    }, headers=auth_header)

    # Create upcoming classes
    client.post("/classes", json={
        "name": "Upcoming Class 1",
        "dateTime": future_dt_1,
        "instructor": "John Doe",
        "availableSlots": 15
    }, headers=auth_header)

    client.post("/classes", json={
        "name": "Upcoming Class 2",
        "dateTime": future_dt_2,
        "instructor": "Carlos",
        "availableSlots": 5
    }, headers=auth_header)

    # Fetch classes
    response = client.get("/classes")
    assert response.status_code == 200
    upcoming = response.json()
    
    # Should only return upcoming classes (excluding the past class)
    assert len(upcoming) == 2
    class_names = [cls["name"] for cls in upcoming]
    assert "Upcoming Class 1" in class_names
    assert "Upcoming Class 2" in class_names
    assert "Past Class" not in class_names
