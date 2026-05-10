import enum


class RoomType(str, enum.Enum):
    STANDARD = "standard"
    SUITE = "suite"
    FAMILY = "family"
