import enum

from ..items.Items import Age2ItemData

class Age2AgeData(enum.IntEnum):
    
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

    DARK =                  25, "Reach Dark Age", None
    FEUDAL =                26, "Reach Feudal Age", Age2ItemData.FEUDAL_AGE
    CASTLE =                27, "Build Outpost", Age2ItemData.CASTLE_AGE
    IMPERIAL =              28, "Build Town Center", Age2ItemData.IMPERIAL_AGE
    