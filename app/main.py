from collections import defaultdict, deque
from datetime import date
from threading import Lock
from time import monotonic

from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.enums import BookingStatus
from app.models import Room, Booking
from app.schemas import (
    RoomCreate, RoomUpdate, RoomResponse,
    BookingCreate, BookingUpdate, BookingResponse,
)
from room_cost_calculator.calculator import calculate_total_cost


RATE_LIMIT_WINDOW_SECONDS = 60
RATE_LIMIT_MAX_REQUESTS = 500

request_log: dict[str, deque[float]] = defaultdict(deque)
request_log_lock = Lock()

app = FastAPI(title="Hotel Room API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


@app.middleware("http")
async def apply_security_controls(request: Request, call_next):
    client_host = request.client.host if request.client else "unknown"
    now = monotonic()

    with request_log_lock:
        timestamps = request_log[client_host]
        while timestamps and now - timestamps[0] > RATE_LIMIT_WINDOW_SECONDS:
            timestamps.popleft()
        if len(timestamps) >= RATE_LIMIT_MAX_REQUESTS:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "Too many requests"},
            )
        timestamps.append(now)

    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Cache-Control"] = "no-store"
    return response


def _check_room_availability(
    db: Session,
    room_id: int,
    check_in: date,
    check_out: date,
    exclude_booking_id: int | None = None,
) -> bool:

    query = db.query(Booking).filter(
        Booking.room_id == room_id,
        Booking.status != BookingStatus.CANCELLED,
        Booking.check_in < check_out,
        Booking.check_out > check_in,
    )
    if exclude_booking_id is not None:
        query = query.filter(Booking.id != exclude_booking_id)
    return query.first() is None


@app.get("/rooms", response_model=list[RoomResponse], status_code=status.HTTP_200_OK)
def list_rooms(db: Session = Depends(get_db)) -> list[Room]:
    return db.query(Room).all()


@app.post(
    "/rooms",
    response_model=RoomResponse,
    status_code=status.HTTP_201_CREATED,
    responses={status.HTTP_409_CONFLICT: {"description": "Room number already exists"}},
)
def create_room(data: RoomCreate, db: Session = Depends(get_db)) -> Room:
    existing = db.query(Room).filter(Room.room_number == data.room_number).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Room with this room_number already exists",
        )
    room = Room(**data.model_dump())
    db.add(room)
    db.commit()
    db.refresh(room)
    return room


@app.get(
    "/rooms/{room_id}",
    response_model=RoomResponse,
    status_code=status.HTTP_200_OK,
    responses={status.HTTP_404_NOT_FOUND: {"description": "Room not found"}},
)
def get_room(room_id: int, db: Session = Depends(get_db)) -> Room:
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found",
        )
    return room


@app.put(
    "/rooms/{room_id}",
    response_model=RoomResponse,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Room not found"},
        status.HTTP_409_CONFLICT: {"description": "Room number already exists"},
    },
)
def update_room(room_id: int, data: RoomUpdate, db: Session = Depends(get_db)) -> Room:
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found",
        )
    update_data = data.model_dump(exclude_unset=True)
    if "room_number" in update_data:
        existing = (
            db.query(Room)
            .filter(Room.room_number == update_data["room_number"])
            .filter(Room.id != room_id)
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Room with this room_number already exists",
            )
    for field, value in update_data.items():
        setattr(room, field, value)
    db.commit()
    db.refresh(room)
    return room


@app.delete(
    "/rooms/{room_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={status.HTTP_404_NOT_FOUND: {"description": "Room not found"}},
)
def delete_room(room_id: int, db: Session = Depends(get_db)) -> None:
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found",
        )
    db.delete(room)
    db.commit()


@app.get(
    "/bookings",
    response_model=list[BookingResponse],
    status_code=status.HTTP_200_OK,
)
def list_bookings(db: Session = Depends(get_db)) -> list[Booking]:
    return db.query(Booking).options(joinedload(Booking.room)).all()


@app.post(
    "/bookings",
    response_model=BookingResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Room not found"},
        status.HTTP_409_CONFLICT: {"description": "Room is not available for the selected dates"},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"description": "Invalid data"},
    },
)
def create_booking(data: BookingCreate, db: Session = Depends(get_db)) -> Booking:
    room = db.query(Room).filter(Room.id == data.room_id).first()
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found",
        )

    if data.guests_count > room.capacity:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Guests count ({data.guests_count}) exceeds room capacity ({room.capacity})",
        )

    nights = (data.check_out - data.check_in).days
    if nights <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="check_out must be after check_in",
        )

    today = date.today()
    if data.check_in < today:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="check_in must not be in the past",
        )

    total_price = calculate_total_cost(
        price_per_night=room.price_per_night,
        nights=nights,
        guests=data.guests_count,
        season=data.season,
        extra_service=data.extra_service,
    )

    if not _check_room_availability(db, data.room_id, data.check_in, data.check_out):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Room is not available for the selected dates",
        )

    booking = Booking(
        room_id=data.room_id,
        guest_name=data.guest_name,
        guest_email=data.guest_email,
        guests_count=data.guests_count,
        check_in=data.check_in,
        check_out=data.check_out,
        season=data.season,
        extra_service=data.extra_service,
        total_price=total_price,
        status=BookingStatus.PENDING,
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking


@app.get(
    "/bookings/{booking_id}",
    response_model=BookingResponse,
    status_code=status.HTTP_200_OK,
    responses={status.HTTP_404_NOT_FOUND: {"description": "Booking not found"}},
)
def get_booking(booking_id: int, db: Session = Depends(get_db)) -> Booking:
    booking = (
        db.query(Booking)
        .options(joinedload(Booking.room))
        .filter(Booking.id == booking_id)
        .first()
    )
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found",
        )
    return booking


@app.put(
    "/bookings/{booking_id}",
    response_model=BookingResponse,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Booking or room not found"},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"description": "Invalid data"},
    },
)
def update_booking(
    booking_id: int, data: BookingUpdate, db: Session = Depends(get_db)
) -> Booking:
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found",
        )

    update_data = data.model_dump(exclude_unset=True)

    if "room_id" in update_data:
        room = db.query(Room).filter(Room.id == update_data["room_id"]).first()
        if not room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Room not found",
            )

    for field, value in update_data.items():
        setattr(booking, field, value)

    if any(
        field in update_data
        for field in ("room_id", "check_in", "check_out", "guests_count", "season", "extra_service")
    ):
        room = db.query(Room).filter(Room.id == booking.room_id).first()
        nights = (booking.check_out - booking.check_in).days
        if nights <= 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="check_out must be after check_in",
            )

        today = date.today()
        if booking.check_in < today:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="check_in must not be in the past",
            )

        if booking.guests_count > room.capacity:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Guests count ({booking.guests_count}) exceeds room capacity ({room.capacity})",
            )

        if not _check_room_availability(
            db, booking.room_id, booking.check_in, booking.check_out, exclude_booking_id=booking.id
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Room is not available for the selected dates",
            )
        booking.total_price = calculate_total_cost(
            price_per_night=room.price_per_night,
            nights=nights,
            guests=booking.guests_count,
            season=booking.season,
            extra_service=update_data.get("extra_service") or getattr(booking, "extra_service", None),
        )

    db.commit()
    db.refresh(booking)
    return booking


@app.delete(
    "/bookings/{booking_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={status.HTTP_404_NOT_FOUND: {"description": "Booking not found"}},
)
def delete_booking(booking_id: int, db: Session = Depends(get_db)) -> None:
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found",
        )
    db.delete(booking)
    db.commit()
