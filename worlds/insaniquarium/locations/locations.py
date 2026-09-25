from __future__ import annotations

import enum

from BaseClasses import Location

from ..generation.identity import GAME_NAME


class InsaniquariumLocation(Location):
    game = GAME_NAME


class InsaniquariumLocationData(enum.IntEnum):
    """Every location. Ids must match the AP_*_LOCATION_ID constants in WinFish's APBridge.cpp."""

    def __new__(cls, id: int, location_name: str) -> InsaniquariumLocationData:
        obj = int.__new__(cls, id)
        obj._value_ = id
        return obj

    def __init__(self, id: int, location_name: str) -> None:
        self.id = id
        self.location_name = location_name

    MOCK_LOCATION = 1, "Mock Location"


# Event location holding the Victory item; has no id.
VICTORY_LOCATION_NAME = "Victory"

location_name_to_id: dict[str, int] = {location.location_name: location.id for location in InsaniquariumLocationData}
