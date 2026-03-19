import enum

from ..items.Items import Age2ItemData

class Age2BuildingData(enum.IntEnum):
    
    def __new__(cls, id: int, *args, **kwargs):
        value = id
        obj = int.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(
        self, id: int, location_name: str, item: Age2ItemData
    ) -> None:
        self.id = id
        self.location_name = location_name
        self.item = item
        
    WONDER =                200, "Build Wonder", Age2ItemData.WONDER
    OUTPOST =               201, "Build Outpost", Age2ItemData.OUTPOST
    TOWN_CENTER =           202, "Build Town Center", Age2ItemData.TOWN_CENTER