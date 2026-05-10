from datetime import date, datetime

from pydantic import BaseModel, Field, ConfigDict

from app.enums import RoomType, BookingStatus
from room_cost_calculator.calculator import Season, ExtraService


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


class BookingBase(BaseModel):
    room_id: int = Field(..., gt=0)
    guest_name: str = Field(..., min_length=1)
    guest_email: str = Field(..., min_length=1)
    guests_count: int = Field(..., gt=0)
    check_in: date
    check_out: date
    season: Season
    extra_service: ExtraService | None = None


class BookingCreate(BookingBase):
    pass


class BookingUpdate(BaseModel):
    guest_name: str | None = Field(None, min_length=1)
    guest_email: str | None = Field(None, min_length=1)
    guests_count: int | None = Field(None, gt=0)
    check_in: date | None = None
    check_out: date | None = None
    season: Season | None = None
    status: BookingStatus | None = None
    extra_service: ExtraService | None = None


class BookingResponse(BaseModel):
    id: int
    room_id: int
    guest_name: str
    guest_email: str
    guests_count: int
    check_in: date
    check_out: date
    season: Season
    extra_service: ExtraService | None = None
    total_price: float
    status: BookingStatus
    created_at: datetime
    room: RoomResponse | None = None

    model_config = ConfigDict(from_attributes=True)
