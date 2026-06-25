from datetime import datetime
from zoneinfo import ZoneInfo
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user
from app.schemas import BookingCreate, BookingResponse
from app.models import Class, Booking, User

router = APIRouter(tags=["Bookings"])
IST = ZoneInfo("Asia/Kolkata")

@router.post("/book", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
def book_class(
    booking_in: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Book a slot in a fitness class. Requires authentication."""
    # Find the class
    db_class = db.query(Class).filter(Class.id == booking_in.class_id).first()
    if not db_class:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Class not found"
        )

    # Validate class date/time is in the future
    now_ist_naive = datetime.now(IST).replace(tzinfo=None)
    if db_class.date_time <= now_ist_naive:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot book a class that has already started or passed"
        )

    # Check slot availability
    if db_class.available_slots <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No available slots in this class"
        )

    # Prevent duplicate booking by the same user for this class
    existing_user_booking = db.query(Booking).filter(
        Booking.class_id == booking_in.class_id,
        Booking.user_id == current_user.id
    ).first()
    if existing_user_booking:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already booked a slot in this class"
        )

    # Prevent duplicate booking by the same client email for this class
    existing_email_booking = db.query(Booking).filter(
        Booking.class_id == booking_in.class_id,
        Booking.client_email == booking_in.client_email
    ).first()
    if existing_email_booking:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This client email has already been used to book a slot in this class"
        )

    # Deduct available slots
    db_class.available_slots -= 1

    # Record the booking
    db_booking = Booking(
        class_id=booking_in.class_id,
        user_id=current_user.id,
        client_name=booking_in.client_name,
        client_email=booking_in.client_email
    )
    db.add(db_booking)
    
    try:
        db.commit()
        db.refresh(db_booking)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not complete booking transaction"
        )

    return db_booking

@router.get("/bookings", response_model=list[BookingResponse])
def get_user_bookings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """View all bookings by the authenticated user."""
    # Fetch all bookings linked to the current user
    bookings = (
        db.query(Booking)
        .filter(Booking.user_id == current_user.id)
        .order_by(Booking.id.desc())
        .all()
    )
    return bookings
