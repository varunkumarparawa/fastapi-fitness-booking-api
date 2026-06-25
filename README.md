# AURA Fitness Studio - Booking API

A robust, self-contained Python & FastAPI backend Booking API for a fictional fitness studio. It handles user authentication, IST timezone calculations, overbooking protection, and reservation queries.

---

## 🛠️ Tech Stack

- **Framework:** FastAPI
- **Language:** Python 3.13
- **Database:** SQLite
- **ORM:** SQLAlchemy 2.0
- **Security:** PyJWT, Bcrypt
- **Testing:** Pytest, HTTPX TestClient

---

## 🔑 Environment Variables

To run this project, you will need to add the following environment variables to your `.env` file (see `.env.example` for reference):

`DATABASE_URL` = `sqlite:///./fitness_studio.db`  
`SECRET_KEY` = `supersecretkeyforfitnessstudiobookingapi123!`  
`ALGORITHM` = `HS256`  
`ACCESS_TOKEN_EXPIRE_MINUTES` = `60`

---

## 💻 Run Locally

### 1. Clone the project and navigate to the directory
```bash
cd backend_booking_api
```

### 2. Create a virtual environment
```bash
python -m venv .venv
```

### 3. Activate the virtual environment
- **Windows (PowerShell):**
  ```powershell
  .venv\Scripts\Activate.ps1
  ```
- **macOS/Linux:**
  ```bash
  source .venv/bin/activate
  ```

### 4. Install dependencies
```bash
pip install -r requirements.txt
```

### 5. Create the `.env` file
Copy the example template:
```bash
cp .env.example .env
```

### 6. Seed the Database
Initialize the database tables and seed test data:
```bash
python seed.py
```

### 7. Start the server
```bash
uvicorn app.main:app --reload
```

Server runs on: [http://127.0.0.1:8000](http://127.0.0.1:8000)  
Interactive API docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 🧪 Running Tests

To run the automated integration tests, run the following command in your terminal:

```bash
pytest
```

---

## 📖 API Reference

### 🔐 Authentication

#### Register a new user
```http
  POST /signup
```
| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `name`    | `string` | **Required**. Full name    |
| `email`   | `string` | **Required**. Valid email  |
| `password`| `string` | **Required**. Min 6 chars  |

**Response (201 Created):**
```json
{
  "id": 1,
  "name": "Jane Doe",
  "email": "jane@example.com"
}
```

#### Log in user
```http
  POST /login
```
| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `email`   | `string` | **Required**. Account email|
| `password`| `string` | **Required**. Password     |

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

### 🏋️ Classes

#### Create a class (Requires Auth Header)
```http
  POST /classes
```
| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `name`    | `string` | **Required**. Class title         |
| `dateTime`| `string` | **Required**. ISO-8601 UTC string |
| `instructor`| `string`| **Required**. Trainer name        |
| `availableSlots`| `int`| **Required**. Slot capacity      |

**Response (201 Created):**
```json
{
  "id": 1,
  "name": "Yoga Flow",
  "dateTime": "2027-06-15T15:30:00+05:30",
  "instructor": "John Doe",
  "availableSlots": 20
}
```

#### Fetch upcoming classes
```http
  GET /classes
```
*Retrieves all classes whose start time is in the future. Times are automatically localized and formatted in IST (+05:30).*

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "name": "HIIT Session",
    "dateTime": "2027-06-18T08:00:00+05:30",
    "instructor": "Jane Smith",
    "availableSlots": 10
  }
]
```

---

### 🎟️ Bookings

#### Book a slot in a class (Requires Auth Header)
```http
  POST /book
```
| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `class_id`| `int`    | **Required**. Target class id |
| `client_name`| `string`| **Required**. Client's name  |
| `client_email`| `string`| **Required**. Client's email|

**Response (201 Created):**
```json
{
  "booking_id": 1,
  "class_id": 1,
  "class_name": "Yoga Flow",
  "dateTime": "2027-06-15T15:30:00+05:30",
  "client_name": "Alice",
  "client_email": "alice@example.com",
  "booked_at": "2026-06-25T13:30:00+05:30"
}
```

#### Fetch user bookings (Requires Auth Header)
```http
  GET /bookings
```
*Retrieves all reservations booked by the authenticated user.*

**Response (200 OK):**
```json
[
  {
    "booking_id": 1,
    "class_id": 1,
    "class_name": "Yoga Flow",
    "dateTime": "2027-06-15T15:30:00+05:30",
    "client_name": "Alice",
    "client_email": "alice@example.com",
    "booked_at": "2026-06-25T13:30:00+05:30"
  }
]
```

---

## 🗄️ Database Schema

### Users Table
- `id` (INTEGER, PK)
- `name` (VARCHAR)
- `email` (VARCHAR, Unique, Indexed)
- `hashed_password` (VARCHAR)
- `created_at` (DATETIME)

### Classes Table
- `id` (INTEGER, PK)
- `name` (VARCHAR)
- `date_time` (DATETIME) - *Stored as naive local time in IST*
- `instructor` (VARCHAR)
- `available_slots` (INTEGER)

### Bookings Table
- `id` (INTEGER, PK)
- `class_id` (INTEGER, FK to classes)
- `user_id` (INTEGER, FK to users)
- `client_name` (VARCHAR)
- `client_email` (VARCHAR)
- `booked_at_utc` (DATETIME) - *Stored as naive UTC time*

---

## 💬 Feedback

If you have any feedback or questions, please reach out to the development team at support@aurastudio.com.
