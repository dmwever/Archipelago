from __future__ import annotations

import enum


class Age2CivData(enum.IntEnum):
    def __new__(cls, id: int, *args, **kwargs):
        obj = int.__new__(cls, id)
        obj._value_ = id
        return obj

    def __init__(self, id: int, name: str) -> None:
        self.id = id
        self.campaign_name = name
        self.excluded_buildings = []
        self.included_buildings = []
    
    HUNS = 0, "Huns"
    FRANKS = 1, "Franks"