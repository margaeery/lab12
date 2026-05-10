from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db, engine, Base
from app.models import Room
from app.schemas import RoomCreate, RoomUpdate, RoomResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Hotel Room API", lifespan=lifespan)


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
