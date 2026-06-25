import datetime
from zoneinfo import ZoneInfo
from app.database import SessionLocal, engine, Base
from app.models import User, Class
from app.auth import hash_password

# Recreate tables to ensure a clean slate
print("Initializing database tables...")
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

db = SessionLocal()
IST = ZoneInfo("Asia/Kolkata")

try:
    print("Seeding database...")

    # 1. Create a demo user
    demo_user = User(
        name="John Studio Owner",
        email="john.owner@example.com",
        hashed_password=hash_password("password123")
    )
    db.add(demo_user)
    print("- Added user: john.owner@example.com / password123")

    # 2. Add classes (using current time context to establish past vs future classes)
    current_time_ist = datetime.datetime.now(IST)
    print(f"Current local time in IST used for reference: {current_time_ist.isoformat()}")

    # Setup class times relative to current local time
    upcoming_time_1 = current_time_ist + datetime.timedelta(days=1)   # Tomorrow
    upcoming_time_2 = current_time_ist + datetime.timedelta(days=2, hours=4) # In two days
    upcoming_time_3 = current_time_ist + datetime.timedelta(days=3, hours=-2) # In three days
    past_time_1 = current_time_ist - datetime.timedelta(days=2)       # Two days ago

    classes = [
        Class(
            name="Yoga Flow",
            date_time=upcoming_time_1.replace(tzinfo=None),
            instructor="Alice Smith",
            available_slots=15
        ),
        Class(
            name="Zumba Party",
            date_time=upcoming_time_2.replace(tzinfo=None),
            instructor="Carlos Santana",
            available_slots=25
        ),
        Class(
            name="HIIT Power Workout",
            date_time=upcoming_time_3.replace(tzinfo=None),
            instructor="Sarah Connor",
            available_slots=10
        ),
        Class(
            name="Morning Pilates (Past Class)",
            date_time=past_time_1.replace(tzinfo=None),
            instructor="Jane Doe",
            available_slots=5
        )
    ]

    db.add_all(classes)
    db.commit()
    print("Database seeding completed successfully!")

except Exception as e:
    db.rollback()
    print(f"An error occurred while seeding the database: {e}")
finally:
    db.close()
