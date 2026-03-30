from enum import Enum, auto


class SENDER(Enum):
    ADD_TRANSACTION = auto()
    VIEW = auto()
    OTHER = auto()