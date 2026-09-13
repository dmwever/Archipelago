import enum

class Age2AgeData(enum.IntEnum):
    def __new__(cls, id: int, *args, **kwargs):
        value = id
        obj = int.__new__(cls, value)
        obj._value_ = value
        return obj

    def __init__(self, id: int, location_name: str) -> None:
        self.id = id
        self.location_name = location_name

    @property
    def item(self):
        """The age-up item, which shares this location's id. Dark Age has none."""
        from ..items.Items import ID_TO_ITEM
        return ID_TO_ITEM.get(self.id)

    DARK =                  25, "Reach Dark Age"
    FEUDAL =                26, "Reach Feudal Age"
    CASTLE =                27, "Reach Castle Age"
    IMPERIAL =              28, "Reach Imperial Age"
