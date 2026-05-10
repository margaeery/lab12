import enum


class RoomType(str, enum.Enum):
    STANDARD = "standard"
    SUITE = "suite"
    FAMILY = "family"


class BookingStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
