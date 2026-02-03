
import enum
from .Scenarios import Age2ScenarioData

class Age2LocationType(enum.Flag):
    VICTORY = enum.auto()
    OBJECTIVE = enum.auto()
    OBJECTIVE_SCENARIO_COLLECTION = enum.auto()
    OBJECTIVE_BRANCHING_ALL = enum.auto()
    OBJECTIVE_BRANCHING_ANY = enum.auto()
    SIDE_QUEST = enum.auto()

def global_location_id(scenario_id: int, local_location_id: int) -> int:
    return scenario_id * 100 + local_location_id

class Age2LocationData(enum.IntEnum):
    
    def __new__(cls, id: int, *args, **kwargs):
        value = id
        obj = int.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(
        self, id: int, location_name: str, scenario: Age2ScenarioData, type: Age2LocationType, vanilla_item: str = ''
    ) -> None:
        self.id = id
        assert id >= global_location_id(scenario.id, 0)
        assert id < global_location_id(scenario.id + 1, 0)
        self.location_name = location_name
        self.scenario = scenario
        self.type = type
        self.vanilla_item = vanilla_item
    
    def global_name(self) -> str:
        return f"{self.scenario.scenario_name}: {self.location_name}" 
    
    #Attila specific locations
    ATT1_VICTORY =                      10100, "Victory",                               Age2ScenarioData.AP_ATTILA_1, Age2LocationType.VICTORY
    ATT1_UNITE_THE_HUNS =               10101, "Unite the Huns Under Attila",           Age2ScenarioData.AP_ATTILA_1, Age2LocationType.OBJECTIVE
    ATT1_FREE_VILLAGERS =               10102, "Free the Villagers From Rome",          Age2ScenarioData.AP_ATTILA_1, Age2LocationType.SIDE_QUEST
    ATT1_RESOLVE_SCOUT_ANY =            10103, "Free or Kill the Scythian Scout",       Age2ScenarioData.AP_ATTILA_1, Age2LocationType.OBJECTIVE_BRANCHING_ANY
    ATT1_CAPTURE_HORSES_CAMP =          10104, "Capture Bleda's Horses",                Age2ScenarioData.AP_ATTILA_1, Age2LocationType.SIDE_QUEST
    ATT1_CAPTURE_HORSE_RUINS =          10105, "Capture Horse at Ruins",                Age2ScenarioData.AP_ATTILA_1, Age2LocationType.SIDE_QUEST
    ATT1_CAPTURE_HORSES_LUMBER =        10106, "Capture Horses Near Lumber",            Age2ScenarioData.AP_ATTILA_1, Age2LocationType.SIDE_QUEST
    ATT1_CAPTURE_HORSES_BEHIND_BASE =   10107, "Capture Horses Behind Base",            Age2ScenarioData.AP_ATTILA_1, Age2LocationType.SIDE_QUEST
    ATT1_CAPTURE_HORSES_WEST =          10108, "Cpature Horses to the West",            Age2ScenarioData.AP_ATTILA_1, Age2LocationType.SIDE_QUEST
    ATT1_CAPTURE_HORSES_ROMAN =         10109, "Capture Horses Near the Roman Base",    Age2ScenarioData.AP_ATTILA_1, Age2LocationType.SIDE_QUEST
    ATT1_KILL_THE_BOAR =                10110, "Kill the Iron Boar",                    Age2ScenarioData.AP_ATTILA_1, Age2LocationType.OBJECTIVE_BRANCHING_ALL
    ATT1_BETRAY_BLEDA =                 10111, "Betray Bleda",                          Age2ScenarioData.AP_ATTILA_1, Age2LocationType.OBJECTIVE_BRANCHING_ALL
    ATT1_BLOW_BLEDA_OFF =               10112, "Refuse Bleda's Challenge",              Age2ScenarioData.AP_ATTILA_1, Age2LocationType.OBJECTIVE_BRANCHING_ALL
    ATT1_FREE_SCOUT =                   10113, "Free the Scythian Scout",               Age2ScenarioData.AP_ATTILA_1, Age2LocationType.OBJECTIVE_BRANCHING_ALL
    ATT1_KILL_SCOUT =                   10114, "Kill the Scythian Scout",               Age2ScenarioData.AP_ATTILA_1, Age2LocationType.OBJECTIVE_BRANCHING_ALL
    ATT1_GIVE_HORSES =                  10115, "Give Scythia 10 Horses",                Age2ScenarioData.AP_ATTILA_1, Age2LocationType.SIDE_QUEST
    ATT1_DEFEAT_FIRST_PLAYER =          10116, "Defeat One Player",                     Age2ScenarioData.AP_ATTILA_1, Age2LocationType.OBJECTIVE
    
    ATT2_VICTORY =          10200, "Victory",                            Age2ScenarioData.AP_ATTILA_2, Age2LocationType.VICTORY
    ATT2_RED_TC =           10201, "Destroy the Red Town Center",        Age2ScenarioData.AP_ATTILA_2, Age2LocationType.SIDE_QUEST
    ATT2_GREEN_LUMBER =     10202, "Destroy the Green Lumber Camp",      Age2ScenarioData.AP_ATTILA_2, Age2LocationType.SIDE_QUEST
    ATT2_PURPLE_VILS =      10203, "Destroy the Purple Houses",          Age2ScenarioData.AP_ATTILA_2, Age2LocationType.SIDE_QUEST
    ATT2_GREY_MINING =      10204, "Destroy the Grey Mining Camps",      Age2ScenarioData.AP_ATTILA_2, Age2LocationType.SIDE_QUEST
    ATT2_CYAN_TC =          10205, "Destroy the Cyan Town Center",       Age2ScenarioData.AP_ATTILA_2, Age2LocationType.SIDE_QUEST
    ATT2_SCYTHIAN_VILS =    10206, "Give 6 Villagers to the Scythians",  Age2ScenarioData.AP_ATTILA_2, Age2LocationType.SIDE_QUEST
    ATT2_BUILD_TC =         10207, "Build a Town Center",                Age2ScenarioData.AP_ATTILA_2, Age2LocationType.OBJECTIVE
    ATT2_BEAT_THE_ROMANS =  10208, "Beat the Romans",                    Age2ScenarioData.AP_ATTILA_2, Age2LocationType.OBJECTIVE
    
    ATT3_VICTORY =              10300, "Victory",                           Age2ScenarioData.AP_ATTILA_3, Age2LocationType.VICTORY
    ATT3_GREEN_DOCK_NORTH =     10301, "Destroy Green's Northern Dock.",    Age2ScenarioData.AP_ATTILA_3, Age2LocationType.OBJECTIVE_SCENARIO_COLLECTION
    ATT3_GREEN_DOCK_SOUTH =     10302, "Destroy Green's Southern Dock.",    Age2ScenarioData.AP_ATTILA_3, Age2LocationType.OBJECTIVE_SCENARIO_COLLECTION
    ATT3_FIND_GOLD =            10303, "Find Gold",                         Age2ScenarioData.AP_ATTILA_3, Age2LocationType.OBJECTIVE_SCENARIO_COLLECTION
    ATT3_GREEN_TC =             10304, "Destroy Green's Town Center",       Age2ScenarioData.AP_ATTILA_3, Age2LocationType.OBJECTIVE_SCENARIO_COLLECTION
    ATT3_BLUE_DOCK_NORTH =      10305, "Destroy Blue's Northern Dock",      Age2ScenarioData.AP_ATTILA_3, Age2LocationType.OBJECTIVE_SCENARIO_COLLECTION
    ATT3_BLUE_DOCKS_SOUTH =     10306, "Destroy Blue's Southern Docks",     Age2ScenarioData.AP_ATTILA_3, Age2LocationType.OBJECTIVE_SCENARIO_COLLECTION
    ATT3_BUILD_CASTLE =         10307, "Build a Castle",                    Age2ScenarioData.AP_ATTILA_3, Age2LocationType.OBJECTIVE_SCENARIO_COLLECTION
    ATT3_RED_TRADE_CARTS =      10308, "Destroy Red's Trade Carts",         Age2ScenarioData.AP_ATTILA_3, Age2LocationType.OBJECTIVE_SCENARIO_COLLECTION
    ATT3_RED_TC =               10309, "Destroy Red's Town Center",         Age2ScenarioData.AP_ATTILA_3, Age2LocationType.OBJECTIVE_SCENARIO_COLLECTION
    ATT3_BLUE_COGS =            10310, "Destroy Blue's Trade Cogs",         Age2ScenarioData.AP_ATTILA_3, Age2LocationType.OBJECTIVE_SCENARIO_COLLECTION
    ATT3_RED_DOCK =             10311, "Destroy Red's Dock",                Age2ScenarioData.AP_ATTILA_3, Age2LocationType.OBJECTIVE_SCENARIO_COLLECTION
    ATT3_RED_MARKET =           10312, "Destroy Red's Market",              Age2ScenarioData.AP_ATTILA_3, Age2LocationType.OBJECTIVE_SCENARIO_COLLECTION
    ATT3_THREATEN_WONDER =      10313, "Threaten Wonder",                   Age2ScenarioData.AP_ATTILA_3, Age2LocationType.OBJECTIVE_SCENARIO_COLLECTION
    ATT3_DESTROY_WONDER =       10314, "Destroy Wonder",                    Age2ScenarioData.AP_ATTILA_3, Age2LocationType.OBJECTIVE_SCENARIO_COLLECTION
    ATT3_BLUE_MONASTERY =       10315, "Destroy Blue's Monastery",          Age2ScenarioData.AP_ATTILA_3, Age2LocationType.OBJECTIVE_SCENARIO_COLLECTION
    
location_from_id = {_location.id: _location for _location in Age2LocationData}
location_name_to_id = {_location.global_name(): _location.id for _location in Age2LocationData}
location_id_to_name = {_location.id: _location.global_name() for _location in Age2LocationData}
SCENARIO_TO_LOCATIONS: dict[Age2ScenarioData, list[Age2LocationData]] = {_scenario: [] for _scenario in Age2ScenarioData}
for _location in Age2LocationData:
    SCENARIO_TO_LOCATIONS[_location.scenario].append(_location)

REGION_TO_LOCATIONS: dict[str, list[Age2LocationData]] = {}
for location in Age2LocationData:
    REGION_TO_LOCATIONS.setdefault(location.scenario.scenario_name, []).append(location)

TYPE_TO_LOCATIONS: dict[Age2LocationType, list[Age2LocationData]] = {}
for location in Age2LocationData:
    TYPE_TO_LOCATIONS.setdefault(location.type, []).append(location)

VICTORY_LOCATIONS: dict[str, Age2LocationData] = {}
for location in TYPE_TO_LOCATIONS.get(Age2LocationType.VICTORY):
    VICTORY_LOCATIONS[location.scenario.scenario_name] = location