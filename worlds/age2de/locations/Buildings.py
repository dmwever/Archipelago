import enum

from .Ages import Age2AgeData

from ..items.Items import Age2ItemData

class Age2BuildingData(enum.IntEnum):
    
    def __new__(cls, id: int, *args, **kwargs):
        value = id
        obj = int.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(
        self, id: int, location_name: str, item: Age2ItemData, age: Age2AgeData
    ) -> None:
        self.id = id
        self.location_name = location_name
        self.item = item
        self.age = age
        
    WONDER =                200, "Build Wonder", Age2ItemData.WONDER, Age2AgeData.IMPERIAL
    OUTPOST =               201, "Build Outpost", Age2ItemData.OUTPOST, Age2AgeData.DARK
    TOWN_CENTER =           202, "Build Town Center", Age2ItemData.TOWN_CENTER, Age2AgeData.DARK
    HOUSE =                 203, "Build House", Age2ItemData.HOUSE, Age2AgeData.DARK
    MILL =                  204, "Build Mill", Age2ItemData.MILL, Age2AgeData.DARK
    MINING_CAMP =           205, "Build Mining Camp", Age2ItemData.MINING_CAMP, Age2AgeData.DARK
    LUMBER_CAMP =           206, "Build Lumber Camp", Age2ItemData.LUMBER_CAMP, Age2AgeData.DARK
    FARM =                  207, "Build Farm", Age2ItemData.FARM, Age2AgeData.DARK
    FISH_TRAP =             208, "Build Fish Trap", Age2ItemData.FISH_TRAP, Age2AgeData.FEUDAL
    DOCK =                  209, "Build Dock", Age2ItemData.DOCK, Age2AgeData.DARK

    MARKET =                210, "Build Market", Age2ItemData.MARKET, Age2AgeData.FEUDAL
    UNIVERSITY =            211, "Build University", Age2ItemData.UNIVERSITY, Age2AgeData.CASTLE
    BLACKSMITH =            212, "Build Blacksmith", Age2ItemData.BLACKSMITH, Age2AgeData.FEUDAL
    MONASTERY =             213, "Build Monastery", Age2ItemData.MONASTERY, Age2AgeData.CASTLE

    BARRACKS =              214, "Build Barracks", Age2ItemData.BARRACKS, Age2AgeData.DARK
    ARCHERY_RANGE =         215, "Build Archery Range", Age2ItemData.ARCHERY_RANGE, Age2AgeData.FEUDAL
    STABLE =                216, "Build Stable", Age2ItemData.STABLE, Age2AgeData.FEUDAL
    SIEGE_WORKSHOP =        217, "Build Siege Workshop", Age2ItemData.SIEGE_WORKSHOP, Age2AgeData.CASTLE
    CASTLE =                218, "Build Castle", Age2ItemData.CASTLE, Age2AgeData.CASTLE

    PALISADE_GATE =         219, "Build Palisade Gate", Age2ItemData.PALISADE_GATE, Age2AgeData.DARK
    GATE =                  220, "Build Stone Gate", Age2ItemData.GATE, Age2AgeData.FEUDAL
    PALISADE_WALL =         221, "Build Palisade Wall", Age2ItemData.PALISADE_WALL, Age2AgeData.DARK
    STONE_WALL =            222, "Build Stone Wall", Age2ItemData.STONE_WALL, Age2AgeData.FEUDAL
    WATCH_TOWER =           223, "Build Watch Tower", Age2ItemData.WATCH_TOWER, Age2AgeData.FEUDAL
    BOMBARD_TOWER =         224, "Build Bombard Tower", Age2ItemData.BOMBARD_TOWER, Age2AgeData.IMPERIAL

    FOLWARK =               225, "Build Folwark", Age2ItemData.FOLWARK, Age2AgeData.DARK
    MULE_CART =             226, "Build Mule Cart", Age2ItemData.MULE_CART, Age2AgeData.DARK
    PASTURE =               227, "Build Pasture", Age2ItemData.PASTURE, Age2AgeData.DARK
    HARBOR =                228, "Build Harbor", Age2ItemData.HARBOR, Age2AgeData.CASTLE
    CARAVANSERAI =          229, "Build Caravanserai", Age2ItemData.CARAVANSERAI, Age2AgeData.IMPERIAL
    FEITORIA =              230, "Build Feitoria", Age2ItemData.FEITORIA, Age2AgeData.IMPERIAL
    SETTLEMENT =            231, "Build Settlement", Age2ItemData.SETTLEMENT, Age2AgeData.DARK

    FORTIFIED_CHURCH =      232, "Build Fortified Church", Age2ItemData.FORTIFIED_CHURCH, Age2AgeData.CASTLE
    KREPOST =               233, "Build Krepost", Age2ItemData.KREPOST, Age2AgeData.CASTLE
    DONJON =                234, "Build Donjon", Age2ItemData.DONJON, Age2AgeData.DARK
    