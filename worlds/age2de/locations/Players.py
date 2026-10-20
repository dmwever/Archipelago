import enum

from .Buildings import Age2BuildingData

class Side(enum.Enum):
    """Which side of P1 a player stands on, fixed for the whole scenario."""
    ALLY = "ally"
    ENEMY = "enemy"

class TradeAccess(enum.Enum):
    """Whether P1's carts or cogs can usefully run to a player's market or dock."""
    CLOSED = "closed"
    """None stands, or none worth trading with."""
    OPEN = "open"
    """An ally's, or an enemy's that nothing guards."""
    ONCE_DEFEATED = "once defeated"
    """An enemy's, usable once P1 can defeat its owner."""

@enum.unique
class Age2PlayerData(enum.IntEnum):
    """A player other than P1, as one scenario has it: one member per ally and enemy. A neutral or
    ignored slot has no member. Routed to its scenario by connections/ScenarioPlayers.

    The id is the scenario's id, then the slot. Trade access is hand-written from PR 19's judged
    flags and the design rulings: where a flag is true, a player on that side is open if it owns
    that building at the start or its AI builds one, unless it is a main opponent; where a flag is
    false, no one is. The flags mean usability, never existence: do not correct them from a scan.
    """

    def __new__(cls, id: int, *args, **kwargs):
        value = id
        obj = int.__new__(cls, value)
        obj._value_ = value
        return obj

    def __init__(
        self, id: int, player_name: str, slot: int, side: Side, is_main_opponent: bool,
        market: TradeAccess, dock: TradeAccess
    ) -> None:
        self.id = id
        self.player_name = player_name
        """How it reads mid-sentence: "can defeat the Jin"."""
        self.slot = slot
        """Its slot in the scenario, P2 to P8."""
        self.side = side
        self.is_main_opponent = is_main_opponent
        """Significantly stronger than the rest: its market and dock stay closed unless nothing
        guards them."""
        self.market = market
        self.dock = dock

    def trade_access(self, building: Age2BuildingData) -> TradeAccess:
        """The access for its market or its dock."""
        if building is Age2BuildingData.MARKET:
            return self.market
        if building is Age2BuildingData.DOCK:
            return self.dock
        raise ValueError(f"{building.name} is not a trade building")

    # Attila 1. Bleda (P2) is ignored. Ruled: the Scythians are an ally.
    ATT1_SCYTHIANS =            1013, "the Scythians",              3, Side.ALLY,  False, TradeAccess.OPEN,          TradeAccess.CLOSED
    ATT1_PERSIANS =             1014, "the Persians",               4, Side.ENEMY, True,  TradeAccess.CLOSED,        TradeAccess.CLOSED
    ATT1_EASTERN_ROMAN_EMPIRE = 1015, "the Eastern Roman Empire",   5, Side.ENEMY, False, TradeAccess.ONCE_DEFEATED, TradeAccess.ONCE_DEFEATED

    # Attila 2. The Scythians (P8) stay neutral. Ruled: Thessalonica's dock is usable.
    ATT2_SOFIA =                1022, "Sofia",                      2, Side.ENEMY, False, TradeAccess.CLOSED,        TradeAccess.CLOSED
    ATT2_NAISSUS =              1023, "Naissus",                    3, Side.ENEMY, False, TradeAccess.CLOSED,        TradeAccess.CLOSED
    ATT2_ADRIANOPLE =           1024, "Adrianople",                 4, Side.ENEMY, False, TradeAccess.CLOSED,        TradeAccess.CLOSED
    ATT2_DYRRHACHIUM =          1025, "Dyrrhachium",                5, Side.ENEMY, False, TradeAccess.ONCE_DEFEATED, TradeAccess.CLOSED
    ATT2_THESSALONICA =         1026, "Thessalonica",               6, Side.ENEMY, False, TradeAccess.ONCE_DEFEATED, TradeAccess.ONCE_DEFEATED
    ATT2_EASTERN_ROMAN_EMPIRE = 1027, "the Eastern Roman Empire",   7, Side.ENEMY, True,  TradeAccess.CLOSED,        TradeAccess.CLOSED

    # Attila 3.
    ATT3_CONSTANTINOPLE =       1032, "Constantinople",             2, Side.ENEMY, True,  TradeAccess.CLOSED,        TradeAccess.CLOSED
    ATT3_MARCIANOPOLIS =        1033, "Marcianopolis",              3, Side.ENEMY, False, TradeAccess.CLOSED,        TradeAccess.ONCE_DEFEATED
    ATT3_PHILIPPOPOLIS =        1034, "Philippopolis",              4, Side.ENEMY, False, TradeAccess.ONCE_DEFEATED, TradeAccess.ONCE_DEFEATED

    # Attila 4. Ruled: Burgundy is an enemy, and no enemy dock is usable.
    ATT4_BURGUNDY =             1042, "Burgundy",                   2, Side.ENEMY, False, TradeAccess.ONCE_DEFEATED, TradeAccess.CLOSED
    ATT4_METZ =                 1043, "Metz",                       3, Side.ENEMY, False, TradeAccess.ONCE_DEFEATED, TradeAccess.CLOSED
    ATT4_ORLEANS =              1044, "Orléans",                    4, Side.ENEMY, True,  TradeAccess.CLOSED,        TradeAccess.CLOSED
    ATT4_WESTERN_ROMAN_EMPIRE = 1045, "the Western Roman Empire",   5, Side.ENEMY, False, TradeAccess.CLOSED,        TradeAccess.CLOSED

    # Attila 5. The Franks (P6) stay neutral.
    ATT5_OSTROGOTHS =           1052, "the Ostrogoths",             2, Side.ALLY,  False, TradeAccess.OPEN,          TradeAccess.CLOSED
    ATT5_WESTERN_ROMAN_EMPIRE = 1053, "the Western Roman Empire",   3, Side.ENEMY, True,  TradeAccess.CLOSED,        TradeAccess.CLOSED
    ATT5_VISIGOTHS =            1054, "the Visigoths",              4, Side.ENEMY, False, TradeAccess.ONCE_DEFEATED, TradeAccess.CLOSED
    ATT5_ALANS =                1055, "the Alans",                  5, Side.ENEMY, False, TradeAccess.ONCE_DEFEATED, TradeAccess.CLOSED

    # Attila 6. No main opponent.
    ATT6_AQUILEIA =             1062, "Aquileia",                   2, Side.ENEMY, False, TradeAccess.CLOSED,        TradeAccess.CLOSED
    ATT6_MEDIOLANUM =           1063, "Mediolanum",                 3, Side.ENEMY, False, TradeAccess.CLOSED,        TradeAccess.CLOSED
    ATT6_VERONA =               1064, "Verona",                     4, Side.ENEMY, False, TradeAccess.CLOSED,        TradeAccess.CLOSED
    ATT6_PATAVIUM =             1065, "Patavium",                   5, Side.ENEMY, False, TradeAccess.CLOSED,        TradeAccess.CLOSED
    ATT6_WESTERN_ROMAN_EMPIRE = 1066, "the Western Roman Empire",   6, Side.ALLY,  False, TradeAccess.CLOSED,        TradeAccess.OPEN

    # Joan 1 and Joan 5 are fixed force: no economy, so no one recorded.

    # Joan 2. Ruled: no enemy market is usable - the scenario ends on a partial defeat.
    JOAN2_BURGUNDY =            2022, "Burgundy",                   2, Side.ENEMY, False, TradeAccess.CLOSED,        TradeAccess.CLOSED
    JOAN2_NORTHERN_ENGLISH =    2023, "the Northern English",       3, Side.ENEMY, False, TradeAccess.CLOSED,        TradeAccess.CLOSED
    JOAN2_ORLEANS =             2024, "Orléans",                    4, Side.ALLY,  False, TradeAccess.CLOSED,        TradeAccess.CLOSED
    JOAN2_BLOIS =               2025, "Blois",                      5, Side.ALLY,  False, TradeAccess.OPEN,          TradeAccess.CLOSED
    JOAN2_CHINON =              2026, "Chinon",                     6, Side.ALLY,  False, TradeAccess.CLOSED,        TradeAccess.CLOSED
    JOAN2_SOUTHERN_ENGLISH =    2027, "the Southern English",       7, Side.ENEMY, False, TradeAccess.CLOSED,        TradeAccess.CLOSED

    # Joan 3. Ruled: the English are the main opponent, but nothing guards their dock.
    JOAN3_BURGUNDY =            2032, "Burgundy",                   2, Side.ENEMY, False, TradeAccess.ONCE_DEFEATED, TradeAccess.CLOSED
    JOAN3_ENGLISH =             2033, "the English",                3, Side.ENEMY, True,  TradeAccess.CLOSED,        TradeAccess.OPEN
    JOAN3_FASTOLF =             2034, "Fastolf",                    4, Side.ENEMY, False, TradeAccess.ONCE_DEFEATED, TradeAccess.CLOSED

    # Joan 4. Ruled: Troyes, Chalons and Rheims are enemies.
    JOAN4_TROYES =              2042, "Troyes",                     2, Side.ENEMY, False, TradeAccess.CLOSED,        TradeAccess.CLOSED
    JOAN4_CHALONS =             2043, "Chalons",                    3, Side.ENEMY, False, TradeAccess.CLOSED,        TradeAccess.CLOSED
    JOAN4_RHEIMS =              2044, "Rheims",                     4, Side.ENEMY, False, TradeAccess.CLOSED,        TradeAccess.CLOSED
    JOAN4_ENGLISH_GUARDS =      2045, "the English Guards",         5, Side.ENEMY, False, TradeAccess.CLOSED,        TradeAccess.CLOSED

    # Joan 6.
    JOAN6_BURGUNDY =            2062, "Burgundy",                   2, Side.ENEMY, False, TradeAccess.ONCE_DEFEATED, TradeAccess.ONCE_DEFEATED
    JOAN6_ENGLISH =             2063, "the English",                3, Side.ENEMY, True,  TradeAccess.CLOSED,        TradeAccess.CLOSED
    JOAN6_SHREWSBURY =          2064, "Shrewsbury",                 4, Side.ENEMY, False, TradeAccess.ONCE_DEFEATED, TradeAccess.CLOSED

    # Genghis 1. No one to defeat: victory is the Kereyid monk. The Kara-Khitai (P2) stay neutral.
    GEN1_GENGHIS_KHAN =         3013, "Genghis Khan",               3, Side.ALLY,  False, TradeAccess.CLOSED,        TradeAccess.CLOSED
    GEN1_KEREYIDS =             3014, "the Kereyids",               4, Side.ALLY,  False, TradeAccess.CLOSED,        TradeAccess.CLOSED
    GEN1_TAYICHIUDS =           3015, "the Tayichi'uds",            5, Side.ALLY,  False, TradeAccess.CLOSED,        TradeAccess.CLOSED
    GEN1_UIGHURS =              3016, "the Uighurs",                6, Side.ALLY,  False, TradeAccess.CLOSED,        TradeAccess.CLOSED
    GEN1_NAIMAN =               3017, "the Naiman",                 7, Side.ALLY,  False, TradeAccess.CLOSED,        TradeAccess.CLOSED
    GEN1_UNGIRRADS =            3018, "the Ungirrads",              8, Side.ALLY,  False, TradeAccess.CLOSED,        TradeAccess.CLOSED

    # Genghis 2. The Tayichi'uds (P4) stay neutral.
    GEN2_KARA_KHITAI =          3022, "the Kara-Khitai",            2, Side.ENEMY, False, TradeAccess.ONCE_DEFEATED, TradeAccess.CLOSED
    GEN2_KUSHLUK =              3023, "Kushluk",                    3, Side.ENEMY, True,  TradeAccess.CLOSED,        TradeAccess.CLOSED

    # Genghis 3. The Engineers (P6) are ignored: they resign the moment the other four are gone.
    GEN3_TANGUTS =              3032, "the Tanguts",                2, Side.ENEMY, False, TradeAccess.CLOSED,        TradeAccess.CLOSED
    GEN3_XI_XIA =               3033, "Xi Xia",                     3, Side.ENEMY, False, TradeAccess.CLOSED,        TradeAccess.CLOSED
    GEN3_JIN =                  3034, "the Jin",                    4, Side.ENEMY, False, TradeAccess.CLOSED,        TradeAccess.CLOSED
    GEN3_SONG =                 3035, "the Song",                   5, Side.ENEMY, False, TradeAccess.CLOSED,        TradeAccess.CLOSED

    # Genghis 4. Ruled: Khwarazm is an enemy and the main opponent; no ally market is usable.
    GEN4_KIPCHAKS =             3042, "the Kipchaks",               2, Side.ENEMY, False, TradeAccess.ONCE_DEFEATED, TradeAccess.CLOSED
    GEN4_RUSSIANS =             3043, "the Russians",               3, Side.ENEMY, False, TradeAccess.ONCE_DEFEATED, TradeAccess.CLOSED
    GEN4_KHWARAZM =             3044, "Khwarazm",                   4, Side.ENEMY, True,  TradeAccess.CLOSED,        TradeAccess.CLOSED

    # Genghis 5. Ruled: no ally market or dock; the Polish and German markets are both usable.
    GEN5_POLISH =               3052, "the Polish",                 2, Side.ENEMY, False, TradeAccess.ONCE_DEFEATED, TradeAccess.CLOSED
    GEN5_BOHEMIANS =            3053, "the Bohemians",              3, Side.ENEMY, False, TradeAccess.CLOSED,        TradeAccess.CLOSED
    GEN5_GERMANS =              3054, "the Germans",                4, Side.ENEMY, False, TradeAccess.ONCE_DEFEATED, TradeAccess.CLOSED

    # Genghis 6.
    GEN6_HUNGARY =              3062, "Hungary",                    2, Side.ENEMY, False, TradeAccess.CLOSED,        TradeAccess.CLOSED
