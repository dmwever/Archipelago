from __future__ import annotations

import enum


class Age2CivData(enum.IntEnum):
    def __new__(cls, id: int, *args, **kwargs):
        obj = int.__new__(cls, id)
        obj._value_ = id
        return obj

    def __init__(self, id: int, name: str, game_id: int) -> None:
        self.id = id
        self.campaign_name = name
        self.game_id = game_id
        self.excluded_buildings = []
        self.included_buildings = []
        self.excluded_techs = []
        self.included_techs = []
        self.excluded_units = []
        self.included_units = []
    HUNS = 0, "Huns", 17
    FRANKS = 1, "Franks", 2
    
    def builds(self, building) -> bool:
        from .Buildings import BuildingOption
        if BuildingOption.unique in building.building_options:
            return building in self.included_buildings
        return building not in self.excluded_buildings