from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, Float, Enum as SQLEnum, ForeignKey, Date, DateTime, Index
from sqlalchemy.orm import relationship

from app.database import Base
from app.enums import RoomType, BookingStatus
from room_cost_calculator.calculator import Season, ExtraService


class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    room_number = Column(String, unique=True, nullable=False, index=True)
    room_type = Column(
        SQLEnum(RoomType, values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
        index=True,
    )
    price_per_night = Column(Float, nullable=False, index=True)
    floor = Column(Integer, nullable=False, index=True)
    capacity = Column(Integer, nullable=False, index=True)

    bookings = relationship("Booking", back_populates="room", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_room_type_price", "room_type", "price_per_night"),
    )


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False, index=True)
    guest_name = Column(String, nullable=False)
    guest_email = Column(String, nullable=False, index=True)
    guests_count = Column(Integer, nullable=False)
    check_in = Column(Date, nullable=False, index=True)
    check_out = Column(Date, nullable=False, index=True)
    season = Column(
        SQLEnum(Season, values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
    )
    extra_service = Column(
        SQLEnum(ExtraService, values_callable=lambda obj: [e.value for e in obj]),
        nullable=True,
    )
    total_price = Column(Float, nullable=False)
    status = Column(
        SQLEnum(BookingStatus, values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
        default=BookingStatus.PENDING,
        index=True,
    )
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), index=True)

    room = relationship("Room", back_populates="bookings")

    __table_args__ = (
        Index("ix_booking_dates", "check_in", "check_out"),
        Index("ix_booking_room_dates", "room_id", "check_in", "check_out"),
        Index("ix_booking_guest_created", "guest_email", "created_at"),
    )
