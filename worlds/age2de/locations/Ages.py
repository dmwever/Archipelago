import enum


class Age2AgeData(enum.IntEnum):
    """The ages, as both Archipelago locations and the ordinal XS compares on.

    The value is the location id; tier is what Techsanity.xs reads, so a
    technology's age can be written into TechData.xs unchanged.
    """

    def __new__(cls, id: int, *args, **kwargs):
        value = id
        obj = int.__new__(cls, value)
        obj._value_ = value
        return obj

    def __init__(self, id: int, location_name: str, tier: int) -> None:
        self.id = id
        self.location_name = location_name
        self.tier = tier

    @property
    def item(self):
        """The age-up item, which shares this location's id. Dark Age has none."""
        from ..items.Items import ID_TO_ITEM
        return ID_TO_ITEM.get(self.id)

    DARK =                  25, "Reach Dark Age", 0
    FEUDAL =                26, "Reach Feudal Age", 1
    CASTLE =                27, "Reach Castle Age", 2
    IMPERIAL =              28, "Reach Imperial Age", 3
