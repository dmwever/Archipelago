



from dataclasses import dataclass
import enum

from worlds.age2de.locations.Scenarios import Age2ScenarioData

@dataclass
class Resources:
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



type ItemType = (
    ScenarioItem | Resources
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
        
    # Scenario Progression Items
    C1_ATTILA_2_WOOD =          1, "Attila, The Great Ride: Wood",               ScenarioItem(Age2ScenarioData.AP_ATTILA_2, Resources(1, 700))
    C1_ATTILA_2_FOOD =          2, "Attila, The Great Ride: Food",               ScenarioItem(Age2ScenarioData.AP_ATTILA_2, Resources(2, 900))
    C1_ATTILA_2_GOLD_STONE =    3, "Attila, The Great Ride: Gold and Stone",     ScenarioItem(Age2ScenarioData.AP_ATTILA_2, Resources(3, 300))
    C1_ATTILA_2_VILLAGERS =     4, "Attila, The Great Ride: Villagers",          ScenarioItem(Age2ScenarioData.AP_ATTILA_2, TriggerActivation(0))
    
    #Scenario Side Quest Items
    C1_ATTILA_2_SCYTHIANS =     5, "Attila, The Great Ride: Scythian Troops",    ScenarioItem(Age2ScenarioData.AP_ATTILA_2, TriggerActivation(1))
    
    # Filler Resources
    FILLER_WOOD =             8,  "+100 Wood",  Resources(1, 100)
    FILLER_FOOD =             7,  "+100 Food",  Resources(2, 100)
    FILLER_GOLD =             9,  "+100 Gold",  Resources(3, 100)
    FILLER_STONE =            10, "+100 Stone", Resources(4, 100)

        
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