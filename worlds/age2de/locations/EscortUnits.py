import enum


@enum.unique
class Age2EscortUnitData(enum.IntEnum):
    def __new__(cls, id: int, *args, **kwargs):
        value = id
        obj = int.__new__(cls, value)
        obj._value_ = value
        return obj

    def __init__(self, id: int, location_name: str, escort_name: str, game_id: int) -> None:
        self.id = id
        self.location_name = location_name
        self.escort_name = escort_name
        self.game_id = game_id

    # 600 - 799 = Escort objectives, picking up after the heroes.
    CART = 600, "Own Cart", "Cart", 1338


NAME_TO_ESCORT: dict[str, Age2EscortUnitData] = {escort.escort_name: escort
                                                 for escort in Age2EscortUnitData}
GAME_ID_TO_ESCORT: dict[int, Age2EscortUnitData] = {escort.game_id: escort
                                                    for escort in Age2EscortUnitData}
