from dataclasses import dataclass
import enum

from BaseClasses import ItemClassification
from ..locations.Civilizations import Age2CivData
from ..locations.Campaigns import Age2CampaignData
from ..locations.Scenarios import Age2ScenarioData

class Resource(enum.Enum):
    WOOD = 1,
    FOOD = 2,
    GOLD = 3,
    STONE = 4

class Age(enum.Enum):
    DARK = 0,
    FEUDAL = 1,
    CASTLE = 2,
    IMPERIAL = 3

@dataclass
class Resources:
    type: Resource
    amount: int

@dataclass
class TCResources:
    type: Resource
    amount: int

@dataclass
class Victory:
    pass

@dataclass
class Building:
    game_id: int
    total_cost: float
    age: Age
    needed_resources: dict[Resource, float]
    
@dataclass
class ScenarioItem:
    vanilla_scenario: Age2ScenarioData

@dataclass
class Mercenary:
    vanilla_scenario: Age2ScenarioData
    # troop_count: dict[int, int] # UnitId, Count

@dataclass
class ProgressiveScenario:
    vanilla_campaign: Age2CampaignData
    num_additional_scenarios: int

@dataclass
class Campaign:
    vanilla_campaign: Age2CampaignData

@dataclass
class StartingResources:
    type: Resource
    amount: int

type FillerItemType = (
    Resources | StartingResources
)

type ItemType = (
    ScenarioItem | StartingResources | ProgressiveScenario | Mercenary | Campaign | Resources | TCResources | Victory | Building
)

item_type_to_classification = {
    ScenarioItem: ItemClassification.progression,
    ProgressiveScenario: ItemClassification.progression,
    Campaign: ItemClassification.progression,
    TCResources: ItemClassification.progression,
    Age: ItemClassification.progression,
    Building: ItemClassification.progression,
    Mercenary: ItemClassification.useful,
    Resources: ItemClassification.filler,
    StartingResources: ItemClassification.useful,
    Victory: ItemClassification.progression,
}

class Age2ItemData(enum.IntEnum):
    def __new__(cls, id: int, name: str, type: ItemType) -> 'Age2ItemData':
        value = id
        obj = int.__new__(cls, value)
        obj._value_ = value
        return obj

    def __init__(self, id: int, name: str, type: ItemType) -> None:
        self.id = id
        self.item_name = name
        self.type = type
        self.type_data = self.type.__class__
    
    VICTORY =                       0, "Victory", Victory()
    
    #1 - 999 = Resources (25), Ages (25), Civs (150), Buildings (100), Units (350), Techs (350) 
    
    # Filler Resources
    FILLER_WOOD_SMALL =             1, "+100 Wood",   Resources(Resource.WOOD, 100)
    FILLER_FOOD_SMALL =             2, "+100 Food",   Resources(Resource.FOOD, 100)
    FILLER_GOLD_SMALL =             3, "+100 Gold",   Resources(Resource.GOLD, 100)
    FILLER_STONE_SMALL =            4, "+50 Stone",   Resources(Resource.STONE, 50)
    FILLER_WOOD_MEDIUM =            5, "+250 Wood",   Resources(Resource.WOOD, 250)
    FILLER_FOOD_MEDIUM =            6, "+250 Food",   Resources(Resource.FOOD, 250)
    FILLER_GOLD_MEDIUM =            7, "+250 Gold",   Resources(Resource.GOLD, 250)
    FILLER_STONE_MEDIUM =           8, "+125 Stone",  Resources(Resource.STONE, 125)
    FILLER_WOOD_LARGE =             9, "+1000 Wood",  Resources(Resource.WOOD, 1000)
    FILLER_FOOD_LARGE =            10, "+1000 Food",  Resources(Resource.FOOD, 1000)
    FILLER_GOLD_LARGE =            11, "+1000 Gold",  Resources(Resource.GOLD, 1000)
    FILLER_STONE_LARGE =           12, "+500 Stone",  Resources(Resource.STONE, 500)
    
    #Starting Resources
    STARTING_WOOD_SMALL =             13, "+50 Starting Wood",      StartingResources(Resource.WOOD, 50)
    STARTING_FOOD_SMALL =             14, "+50 Starting Food",      StartingResources(Resource.FOOD, 50)
    STARTING_GOLD_SMALL =             15, "+50 Starting Gold",      StartingResources(Resource.GOLD, 50)
    STARTING_STONE_SMALL =            16, "+25 Starting Stone",     StartingResources(Resource.STONE, 25)
    STARTING_WOOD_MEDIUM =            17, "+100 Starting Wood",     StartingResources(Resource.WOOD, 100)
    STARTING_FOOD_MEDIUM =            18, "+100 Starting Food",     StartingResources(Resource.FOOD, 100)
    STARTING_GOLD_MEDIUM =            19, "+100 Starting Gold",     StartingResources(Resource.GOLD, 100)
    STARTING_STONE_MEDIUM =           20, "+50 Starting Stone",     StartingResources(Resource.STONE, 50)
    STARTING_WOOD_LARGE =             21, "+250 Starting Wood",     StartingResources(Resource.WOOD, 250)
    STARTING_FOOD_LARGE =             22, "+250 Starting Food",     StartingResources(Resource.FOOD, 250)
    STARTING_GOLD_LARGE =             23, "+250 Starting Gold",     StartingResources(Resource.GOLD, 250)
    STARTING_STONE_LARGE =            24, "+125 Starting Stone",    StartingResources(Resource.STONE, 125)
    
    #Ages
    FEUDAL_AGE =        26, "Feudal Age", Age.FEUDAL
    CASTLE_AGE =        27, "Castle Age", Age.CASTLE
    IMPERIAL_AGE =      28, "Imperial Age", Age.IMPERIAL
    
    #200 - 300 = Buildings
    WONDER =                        200, "Wonder",              Building(276, 3000.0,   Age.IMPERIAL,   { Resource.WOOD: 1000.0, Resource.GOLD: 1000.0, Resource.STONE: 1000.0 })
    OUTPOST =                       201, "Outpost",             Building(598, 30.0,     Age.DARK,       { Resource.WOOD: 25.0, Resource.STONE: 5.0 })
    TOWN_CENTER =                   202, "Town Center",         Building(621, 375.0,    Age.DARK,       { Resource.WOOD: 275.0, Resource.STONE: 100.0 })
    HOUSE =                         203, "House",               Building(70, 25.0,      Age.DARK,       { Resource.WOOD: 25.0 })
    MILL =                          204, "Mill",                Building(68, 100.0,     Age.DARK,       { Resource.WOOD: 100.0 })
    MINING_CAMP =                   205, "Mining Camp",         Building(584, 100.0,    Age.DARK,       { Resource.WOOD: 100.0 })
    LUMBER_CAMP =                   206, "Lumber Camp",         Building(562, 100.0,    Age.DARK,       { Resource.WOOD: 100.0 })
    FARM =                          207, "Farm",                Building(50, 60.0,      Age.DARK,       { Resource.WOOD: 60.0 })
    FISH_TRAP =                     208, "Fish Trap",           Building(199, 100.0,    Age.FEUDAL,     { Resource.WOOD: 100.0 })
    DOCK =                          209, "Dock",                Building(45, 150.0,     Age.DARK,       { Resource.WOOD: 150.0 })
    MARKET =                        210, "Market",              Building(84, 175.0,     Age.FEUDAL,     { Resource.WOOD: 175.0 })
    UNIVERSITY =                    211, "University",          Building(209, 200.0,    Age.CASTLE,     { Resource.WOOD: 200.0 })
    BLACKSMITH =                    212, "Blacksmith",          Building(103, 150.0,    Age.FEUDAL,     { Resource.WOOD: 150.0 })
    MONASTERY =                     213, "Monastery",           Building(104, 175.0,    Age.CASTLE,     { Resource.WOOD: 175.0 })
    BARRACKS =                      214, "Barracks",            Building(12, 175.0,     Age.DARK,       { Resource.WOOD: 175.0 })
    ARCHERY_RANGE =                 215, "Archery Range",       Building(87, 175.0,     Age.FEUDAL,     { Resource.WOOD: 175.0 })
    STABLE =                        216, "Stable",              Building(101, 175.0,    Age.FEUDAL,     { Resource.WOOD: 175.0 })
    SIEGE_WORKSHOP =                217, "Siege Workshop",      Building(49, 200.0,     Age.CASTLE,     { Resource.WOOD: 200.0 })
    CASTLE =                        218, "Castle",              Building(82, 650.0,     Age.CASTLE,     { Resource.STONE: 650.0 })
    PALISADE_GATE =                 219, "Palisade Gate",       Building(792, 20.0,     Age.DARK,       { Resource.WOOD: 20.0 })
    GATE =                          220, "Stone Gate",          Building(487, 30.0,     Age.FEUDAL,     { Resource.STONE: 30.0 })
    PALISADE_WALL =                 221, "Palisade Wall",       Building(72, 3.0,       Age.DARK,       { Resource.WOOD: 3.0 })
    STONE_WALL =                    222, "Stone Wall",          Building(117, 5.0,      Age.FEUDAL,     { Resource.STONE: 5.0 })
    WATCH_TOWER =                   223, "Watch Tower",         Building(79, 160.0,     Age.FEUDAL,     { Resource.WOOD: 35.0, Resource.STONE: 125.0 })
    BOMBARD_TOWER =                 224, "Bombard Tower",       Building(236, 225.0,    Age.IMPERIAL,   { Resource.STONE: 125.0, Resource.GOLD: 100.0 })
    FOLWARK =                       225, "Folwark",             Building(1734, 100.0,   Age.DARK,       { Resource.WOOD: 100.0 })
    MULE_CART =                     226, "Mule Cart",           Building(1808, 100.0,   Age.DARK,       { Resource.FOOD: 20.0, Resource.WOOD: 80.0 })
    PASTURE =                       227, "Pasture",             Building(1889, 110.0,   Age.DARK,       { Resource.WOOD: 110.0 })
    HARBOR =                        228, "Harbor",              Building(1189, 150.0,   Age.CASTLE,     { Resource.WOOD: 150.0 })
    CARAVANSERAI =                  229, "Caravanserai",        Building(1754, 225.0,   Age.IMPERIAL,   { Resource.WOOD: 175.0, Resource.STONE: 50.0 })
    FEITORIA =                      230, "Feitoria",            Building(1021, 650.0,   Age.IMPERIAL,   { Resource.STONE: 300.0, Resource.GOLD: 350.0 })
    SETTLEMENT =                    231, "Settlement",          Building(2556, 125.0,   Age.DARK,       { Resource.WOOD: 125.0 })
    FORTIFIED_CHURCH =              232, "Fortified Church",    Building(1806, 200.0,   Age.CASTLE,     { Resource.WOOD: 200.0 })
    KREPOST =                       233, "Krepost",             Building(1251, 350.0,   Age.CASTLE,     { Resource.STONE: 350.0 })
    DONJON =                        234, "Donjon",              Building(1665, 225.0,   Age.DARK,       { Resource.WOOD: 50.0, Resource.STONE: 175 })
    
    #1000 - 2999 = Progression Items
    TOWN_CENTER_WOOD =                  1000, "Starting Town Center Wood",          TCResources(Resource.WOOD, 275)
    TOWN_CENTER_STONE =                 1001, "Starting Town Center Stone",         TCResources(Resource.FOOD, 100)
    
    # Scenario Progression Items
    AP_ATTILA_1_BLEDAS_CAMP =   1002, "Attila, The Scourge of God: Bleda's Camp",           ScenarioItem(Age2ScenarioData.AP_ATTILA_1)
    AP_ATTILA_1_ATTILAS_CAMP =  1003, "Attila, The Scourge of God: Attila's Camp",          ScenarioItem(Age2ScenarioData.AP_ATTILA_1)
    AP_ATTILA_2_VILLAGERS =     1004, "Attila, The Great Ride: Villagers",                  ScenarioItem(Age2ScenarioData.AP_ATTILA_2)
    AP_ATTILA_3_RED_GOLD =      1005, "Attila, The Walls of Constantinople: Red Gold",      ScenarioItem(Age2ScenarioData.AP_ATTILA_3)
    AP_ATTILA_3_GREEN_GOLD =    1006, "Attila, The Walls of Constantinople: Green Gold",    ScenarioItem(Age2ScenarioData.AP_ATTILA_3)
    
    #3000 - 3999 = Scenarios (500), Campaigns (100)
    
    # Progressive Scenarios (Campaign Count - 1)
    PROGRESSIVE_ATTILA_SCENARIO = 3000, "Progressive Attila Scenario", ProgressiveScenario(Age2CampaignData.ATTILA, 5)
    
    #Campaign Unlocks (Unlocks first level)
    ATTILA_THE_HUN = 3500, "Attila the Hun Campaign", Campaign(Age2CampaignData.ATTILA)
    
    #4000 - 4999 = Troops, Future Use
    
    #Troop Items
    AP_ATTILA_1_MANGUDAI =                  4000, "Scythian Mangudai",          Mercenary(Age2ScenarioData.AP_ATTILA_1)
    AP_ATTILA_1_ROMAN_VILLAGERS =           4001, "Roman Villagers",            Mercenary(Age2ScenarioData.AP_ATTILA_1)
    AP_ATTILA_2_DYRRHACHIUMS_PRISONERS =    4002, "Dyrrhachium's Prisoners",    Mercenary(Age2ScenarioData.AP_ATTILA_2)
    AP_ATTILA_2_SCYTHIAN_TROOP =            4003, "Scythian Troops",            Mercenary(Age2ScenarioData.AP_ATTILA_2)
    

        
NAME_TO_ITEM: dict[str, Age2ItemData] = {}
ID_TO_ITEM: dict[int, Age2ItemData] = {}
CATEGORY_TO_ITEMS: dict[type, list[Age2ItemData]] = {}
SCENARIO_TO_ITEMS: dict[Age2ScenarioData, list[Age2ItemData]] = {_scenario: [] for _scenario in Age2ScenarioData}
filler_items: list[Age2ItemData] = []
item_id_to_name: dict[int, str] = {}
item_name_to_id: dict[str, int] = {}
for item in Age2ItemData:
    assert item.item_name not in item_name_to_id, f"Duplicate item name: {item.item_name}"
    assert item.id not in item_id_to_name, f"Duplicate item ID: {item.id}"
    NAME_TO_ITEM[item.item_name] = item
    ID_TO_ITEM[item.id] = item
    if item_type_to_classification[item.type_data] == ItemClassification.filler:
        filler_items.append(item)
    item_id_to_name[item.id] = item.item_name
    item_name_to_id[item.item_name] = item.id
    CATEGORY_TO_ITEMS.setdefault(item.type_data, []).append(item)
    if item.type_data == ScenarioItem:
        SCENARIO_TO_ITEMS[item.type.vanilla_scenario].append(item)