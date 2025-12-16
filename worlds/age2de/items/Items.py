from dataclasses import dataclass
import enum

from worlds.age2de.locations.Scenarios import Age2ScenarioData

@dataclass
class Resources:
    type: int
    amount: int

@dataclass
class TC:
    type: int
    amount: int
    
@dataclass
class TriggerActivation:
    trigger: int

type ScenarioItemType = (
    Resources | TriggerActivation
)

@dataclass
class ScenarioItem:
    vanilla_scenario: Age2ScenarioData
    """The scenario the player would require this item for victory"""
    item: ScenarioItemType
    amount: int = 1


type FillerItemType = (
    Resources
)

type ItemType = (
    ScenarioItem | Resources | TriggerActivation | TC
)


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
    FILLER_WOOD_SMALL =             1, "+100 Wood",  Resources(1, 100)
    FILLER_FOOD_SMALL =             2, "+100 Food",  Resources(2, 100)
    FILLER_GOLD_SMALL =             3, "+100 Gold",  Resources(3, 100)
    FILLER_STONE_SMALL =            4, "+100 Stone", Resources(4, 100)
    
    #1000 - 2999 = Progression Items
    
    # Scenario Progression Items
    TOWN_CENTER_WOOD =                  1000, "Starting Town Center Wood",          ScenarioItem(Age2ScenarioData.AP_ATTILA_2, TC(1, 275))
    TOWN_CENTER_STONE =                 1001, "Starting Town Center Stone",         ScenarioItem(Age2ScenarioData.AP_ATTILA_2, TC(2, 100))
    AP_ATTILA_2_VILLAGERS_TRIGGER =     1002, "Attila, The Great Ride: Villagers",  ScenarioItem(Age2ScenarioData.AP_ATTILA_2, TriggerActivation(0))
    
    #3000 - 3999 = Scenarios (500), Campaigns (100)
    
    #4000 - 4999 = Troops, Future Use
    
    #Troop Items
    AP_ATTILA_2_SCYTHIAN_TROOP =     4000, "Attila, The Great Ride: Scythian Troops",    ScenarioItem(Age2ScenarioData.AP_ATTILA_2, TriggerActivation(1))
    

        
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