from sqlalchemy import Column, Integer, String, Float, Enum as SQLEnum

from app.database import Base
from app.enums import RoomType


class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    room_number = Column(String, unique=True, nullable=False, index=True)
    room_type = Column(
        SQLEnum(RoomType, values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
    )
    price_per_night = Column(Float, nullable=False)
    floor = Column(Integer, nullable=False)
    capacity = Column(Integer, nullable=False)
