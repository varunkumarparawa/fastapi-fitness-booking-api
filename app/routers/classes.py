from datetime import datetime
from zoneinfo import ZoneInfo
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user
from app.schemas import ClassCreate, ClassResponse
from app.models import Class, User

router = APIRouter(tags=["Classes"])
IST = ZoneInfo("Asia/Kolkata")

@router.post("/classes", response_model=ClassResponse, status_code=status.HTTP_201_CREATED)
def create_class(
    class_in: ClassCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new fitness class. Requires authentication."""
    # Convert input IST timezone-aware datetime to naive datetime for SQLite storage
    naive_ist_datetime = class_in.dateTime.replace(tzinfo=None)

    db_class = Class(
        name=class_in.name,
        date_time=naive_ist_datetime,
        instructor=class_in.instructor,
        available_slots=class_in.availableSlots
    )
    db.add(db_class)
    db.commit()
    db.refresh(db_class)
    return db_class

@router.get("/classes", response_model=list[ClassResponse])
def get_upcoming_classes(db: Session = Depends(get_db)):
    """Fetch all upcoming fitness classes (ordered by date/time)."""
    # Current time in IST, converted to naive for matching SQLite database contents
    now_ist_naive = datetime.now(IST).replace(tzinfo=None)

    upcoming_classes = (
        db.query(Class)
        .filter(Class.date_time > now_ist_naive)
        .order_by(Class.date_time.asc())
        .all()
    )
    return upcoming_classes
