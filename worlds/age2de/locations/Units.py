import enum

@enum.unique
class Age2UnitData(enum.IntEnum):
    """Units a mercenary can deliver. The member value is the engine object id, not an AP id, so
    it is what XS spawns against and what MercenaryData renders. Only the units the shipped
    scenarios actually hand over are listed; add a member when a mercenary needs one."""

    def __new__(cls, game_id: int, *args, **kwargs):
        value = game_id
        obj = int.__new__(cls, value)
        obj._value_ = value
        return obj

    def __init__(self, game_id: int, unit_name: str) -> None:
        self.game_id = game_id
        self.unit_name = unit_name

    HAND_CANNONEER =        5, "Hand Cannoneer"
    MANGUDAI =             11, "Mangudai"
    CROSSBOWMAN =          24, "Crossbowman"
    BOMBARD_CANNON =       36, "Bombard Cannon"
    KNIGHT =               38, "Knight"
    MILITIA =              74, "Militia"
    MAN_AT_ARMS =          75, "Man-at-Arms"
    VILLAGER_MALE =        83, "Villager (Male)"
    SCORPION =            279, "Scorpion"
    THROWING_AXEMAN =     281, "Throwing Axeman"
    VILLAGER_FEMALE =     293, "Villager (Female)"
    PIKEMAN =             358, "Pikeman"
    CAPPED_RAM =          422, "Capped Ram"
    HUSSAR =              441, "Hussar"
    SCOUT_CAVALRY =       448, "Scout Cavalry"
    HEAVY_SCORPION =      542, "Heavy Scorpion"
    ONAGER =              550, "Onager"
    JEAN_BUREAU =         650, "Jean Bureau"
    TARKAN =              755, "Tarkan"
