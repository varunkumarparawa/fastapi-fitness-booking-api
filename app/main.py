from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.database import engine, Base
from app.routers import auth, classes, bookings

# Automatically create the database tables on startup (if not already existing)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Fitness Studio Booking API",
    description="A robust backend Booking API for a fitness studio, handling user auth, classes in IST, and bookings.",
    version="1.0.0",
)

# Custom validation exception handler to return clean and structured errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        # Get the field name path, e.g. "body.email" or "body.dateTime"
        loc = " -> ".join(str(x) for x in err["loc"] if x != "body")
        errors.append({
            "field": loc or "request_body",
            "message": err["msg"],
            "type": err["type"]
        })
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Validation error occurred on the request parameters.",
            "errors": errors
        }
    )

# Include routers
app.include_router(auth.router)
app.include_router(classes.router)
app.include_router(bookings.router)

@app.get("/", tags=["System"])
def root():
    return {
        "status": "online",
        "message": "Welcome to the Fitness Studio Booking API!",
        "documentation": "/docs"
    }
