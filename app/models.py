import datetime
from zoneinfo import ZoneInfo
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

IST = ZoneInfo("Asia/Kolkata")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    bookings = relationship("Booking", back_populates="user", cascade="all, delete-orphan")


class Class(Base):
    __tablename__ = "classes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    # Stored as local time in IST (timezone-naive but offsets to IST)
    date_time = Column(DateTime, nullable=False)
    instructor = Column(String, nullable=False)
    available_slots = Column(Integer, nullable=False)

    bookings = relationship("Booking", back_populates="fitness_class", cascade="all, delete-orphan")

    @property
    def dateTime(self) -> datetime.datetime:
        """Returns class datetime localized to IST."""
        if self.date_time is None:
            return None
        return self.date_time.replace(tzinfo=IST)

    @property
    def availableSlots(self) -> int:
        """Alias for available_slots to support camelCase serialization."""
        return self.available_slots


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    client_name = Column(String, nullable=False)
    client_email = Column(String, nullable=False)
    booked_at_utc = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="bookings")
    fitness_class = relationship("Class", back_populates="bookings")

    @property
    def booking_id(self) -> int:
        """Alias for id to match response schema."""
        return self.id

    @property
    def class_name(self) -> str:
        """Convenience property for class name."""
        return self.fitness_class.name if self.fitness_class else ""

    @property
    def dateTime(self) -> datetime.datetime:
        """Convenience property for class dateTime localized to IST."""
        if self.fitness_class and self.fitness_class.date_time:
            return self.fitness_class.date_time.replace(tzinfo=IST)
        return None

    @property
    def booked_at(self) -> datetime.datetime:
        """Returns the booking time converted to IST."""
        if self.booked_at_utc is None:
            return None
        # Convert UTC naive datetime to IST timezone-aware datetime
        return self.booked_at_utc.replace(tzinfo=datetime.timezone.utc).astimezone(IST)
