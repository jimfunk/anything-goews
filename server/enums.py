"""
Variant definitions for GOEWS
"""
from enum import IntEnum


class Variant(IntEnum):
    ORIGINAL = 0
    THICKER_CLEATS = 1

    def to_int(self) -> int:
        return int(self)
