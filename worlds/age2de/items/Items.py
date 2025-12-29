from dataclasses import dataclass
import enum

from BaseClasses import ItemClassification
from ..locations.Scenarios import Age2ScenarioData

@dataclass
class Resources:
    type: int
    amount: int

@dataclass
class TCResources:
    type: int
    amount: int
    
@dataclass
class TriggerActivation:
    trigger: int

@dataclass
class ScenarioItem:
    vanilla_scenario: Age2ScenarioData

@dataclass
class StartingResources:
    type: int
    amount: int

type FillerItemType = (
    Resources | StartingResources
)

type ItemType = (
    ScenarioItem | StartingResources | Resources | TriggerActivation | TCResources
)

item_type_to_classification = {
    ScenarioItem: ItemClassification.progression,
    TCResources: ItemClassification.progression,
    Resources: ItemClassification.filler,
    StartingResources: ItemClassification.filler,
    TriggerActivation: ItemClassification.progression,
}

class Age2Item(enum.IntEnum):
    def __new__(cls, id: int, name: str, type: ItemType) -> 'Age2Item':
        value = id
        obj = int.__new__(cls, value)
        obj._value_ = value
        return obj

    def __init__(self, id: int, name: str, type: ItemType) -> None:
        self.id = id
        self.item_name = name
        self.type = type
    
    #1 - 999 = Resources (25), Ages (25), Civs (150), Buildings (100), Units (350), Techs (350) 
    
    # Filler Resources
    FILLER_WOOD_SMALL =             1, "+100 Wood",   Resources(1, 100)
    FILLER_FOOD_SMALL =             2, "+100 Food",   Resources(2, 100)
    FILLER_GOLD_SMALL =             3, "+100 Gold",   Resources(3, 100)
    FILLER_STONE_SMALL =            4, "+50 Stone",   Resources(4, 50)
    FILLER_WOOD_MEDIUM =            5, "+250 Wood",   Resources(1, 250)
    FILLER_FOOD_MEDIUM =            6, "+250 Food",   Resources(2, 250)
    FILLER_GOLD_MEDIUM =            7, "+250 Gold",   Resources(3, 250)
    FILLER_STONE_MEDIUM =           8, "+125 Stone",  Resources(4, 125)
    FILLER_WOOD_LARGE =             9, "+1000 Wood",  Resources(1, 1000)
    FILLER_FOOD_LARGE =            10, "+1000 Food",  Resources(2, 1000)
    FILLER_GOLD_LARGE =            11, "+1000 Gold",  Resources(3, 1000)
    FILLER_STONE_LARGE =           12, "+500 Stone",  Resources(4, 500)
    
    #Starting Resources
    STARTING_WOOD_SMALL =             13, "+50 Starting Wood",   StartingResources(1, 50)
    STARTING_FOOD_SMALL =             14, "+50 Starting Food",   StartingResources(2, 50)
    STARTING_GOLD_SMALL =             15, "+50 Starting Gold",   StartingResources(3, 50)
    STARTING_STONE_SMALL =            16, "+25 Starting Stone",   StartingResources(4, 25)
    STARTING_WOOD_MEDIUM =            17, "+100 Starting Wood",   StartingResources(1, 100)
    STARTING_FOOD_MEDIUM =            18, "+100 Starting Food",   StartingResources(2, 100)
    STARTING_GOLD_MEDIUM =            19, "+100 Starting Gold",   StartingResources(3, 100)
    STARTING_STONE_MEDIUM =           20, "+50 Starting Stone",  StartingResources(4, 50)
    STARTING_WOOD_LARGE =             21, "+250 Starting Wood",  StartingResources(1, 250)
    STARTING_FOOD_LARGE =             22, "+250 Starting Food",  StartingResources(2, 250)
    STARTING_GOLD_LARGE =             23, "+250 Starting Gold",  StartingResources(3, 250)
    STARTING_STONE_LARGE =            24, "+125 Starting Stone",  StartingResources(4, 125)
    
    #1000 - 2999 = Progression Items
    TOWN_CENTER_WOOD =                  1000, "Starting Town Center Wood",          TCResources(1, 275)
    TOWN_CENTER_STONE =                 1001, "Starting Town Center Stone",         TCResources(2, 100)
    
    # Scenario Progression Items
    AP_ATTILA_2_VILLAGERS_TRIGGER =     1002, "Attila, The Great Ride: Villagers",              ScenarioItem(Age2ScenarioData.AP_ATTILA_2)
    AP_ATTILA_1_BLEDAS_CAMP_TRIGGER =   1003, "Attila, The Scourge of God: Bleda's Camp",       ScenarioItem(Age2ScenarioData.AP_ATTILA_1)
    AP_ATTILA_1_ATTILAS_CAMP_TRIGGER =  1004, "Attila, The Scourge of God: Attila's Camp",      ScenarioItem(Age2ScenarioData.AP_ATTILA_1)
    
    #3000 - 3999 = Scenarios (500), Campaigns (100)
    
    #4000 - 4999 = Troops, Future Use
    
    #Troop Items
    AP_ATTILA_2_SCYTHIAN_TROOP =     4000, "Scythian Troops",       ScenarioItem(Age2ScenarioData.AP_ATTILA_2)
    AP_ATTILA_1_MANGUDAI_TRIGGER =   4001, "Scythian Mangudai",     ScenarioItem(Age2ScenarioData.AP_ATTILA_1)
    

        
NAME_TO_ITEM: dict[str, Age2Item] = {}
ID_TO_ITEM: dict[int, Age2Item] = {}
CATEGORY_TO_ITEMS: dict[type, list[Age2Item]] = {}
item_id_to_name: dict[int, str] = {}
item_name_to_id: dict[str, int] = {}
for item in Age2Item:
    assert item.item_name not in item_name_to_id, f"Duplicate item name: {item.item_name}"
    assert item.id not in item_id_to_name, f"Duplicate item ID: {item.id}"
    NAME_TO_ITEM[item.item_name] = item
    ID_TO_ITEM[item.id] = item
    item_id_to_name[item.id] = item.item_name
    item_name_to_id[item.item_name] = item.id
    CATEGORY_TO_ITEMS.setdefault(item.type.__class__, []).append(item)