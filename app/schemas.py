import re
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from pydantic import BaseModel, Field, field_validator, ConfigDict

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
IST = ZoneInfo("Asia/Kolkata")

def convert_to_ist(dt: datetime) -> datetime:
    """Helper to convert any datetime (naive or aware) to IST."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(IST)


# --- Authentication Schemas ---

class UserSignup(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Full name of the user")
    email: str = Field(..., max_length=255, description="Unique email address")
    password: str = Field(..., min_length=6, max_length=128, description="Password (min 6 characters)")

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        v = v.strip().lower()
        if not EMAIL_REGEX.match(v):
            raise ValueError("Invalid email format")
        return v


class UserLogin(BaseModel):
    email: str = Field(..., description="Registered email address")
    password: str = Field(..., description="Account password")

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        return v.strip().lower()


class UserResponse(BaseModel):
    id: int
    name: str
    email: str

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str


# --- Class Schemas ---

class ClassCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    dateTime: datetime = Field(..., description="Class date and time (ISO format)")
    instructor: str = Field(..., min_length=1, max_length=100)
    availableSlots: int = Field(..., ge=0, description="Number of slots available initially")

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("dateTime", mode="before")
    @classmethod
    def parse_and_convert_datetime(cls, v):
        if isinstance(v, str):
            # Parse ISO 8601 string, translating 'Z' to '+00:00' if needed
            if v.endswith("Z"):
                v = v[:-1] + "+00:00"
            try:
                dt = datetime.fromisoformat(v)
            except ValueError:
                raise ValueError("Invalid ISO-8601 datetime format")
        elif isinstance(v, datetime):
            dt = v
        else:
            raise ValueError("dateTime must be a string or datetime object")
        
        return convert_to_ist(dt)


class ClassResponse(BaseModel):
    id: int
    name: str
    dateTime: datetime = Field(..., serialization_alias="dateTime")
    instructor: str
    availableSlots: int = Field(..., serialization_alias="availableSlots")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        json_encoders={
            datetime: lambda dt: dt.isoformat()
        }
    )


# --- Booking Schemas ---

class BookingCreate(BaseModel):
    class_id: int = Field(..., description="ID of the class to book")
    client_name: str = Field(..., min_length=1, max_length=100, description="Name of the booking client")
    client_email: str = Field(..., description="Email of the booking client")

    @field_validator("client_email")
    @classmethod
    def validate_client_email(cls, v: str) -> str:
        v = v.strip().lower()
        if not EMAIL_REGEX.match(v):
            raise ValueError("Invalid email format")
        return v


class BookingResponse(BaseModel):
    booking_id: int = Field(..., serialization_alias="booking_id")
    class_id: int = Field(..., serialization_alias="class_id")
    class_name: str = Field(..., serialization_alias="class_name")
    dateTime: datetime = Field(..., serialization_alias="dateTime")
    client_name: str = Field(..., serialization_alias="client_name")
    client_email: str = Field(..., serialization_alias="client_email")
    booked_at: datetime = Field(..., serialization_alias="booked_at")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        json_encoders={
            datetime: lambda dt: dt.isoformat()
        }
    )
