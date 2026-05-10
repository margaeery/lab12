from pydantic import BaseModel, Field, ConfigDict

from app.enums import RoomType


class RoomBase(BaseModel):
    room_number: str = Field(..., min_length=1)
    room_type: RoomType
    price_per_night: float = Field(..., gt=0)
    floor: int
    capacity: int = Field(..., gt=0)


class RoomCreate(RoomBase):
    pass


class RoomUpdate(BaseModel):
    room_number: str | None = Field(None, min_length=1)
    room_type: RoomType | None = None
    price_per_night: float | None = Field(None, gt=0)
    floor: int | None = None
    capacity: int | None = Field(None, gt=0)


class RoomResponse(RoomBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
