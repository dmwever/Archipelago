
import enum
from typing import TYPE_CHECKING
from BaseClasses import Location
from worlds.age2de.locations.Scenarios import Age2ScenarioData

class Age2LocationType(enum.Flag):
    VICTORY = enum.auto()
    OBJECTIVE = enum.auto()
    OBJECTIVE_BRANCHING_ALL = enum.auto()
    OBJECTIVE_BRANCHING_ANY = enum.auto()
    SIDE_QUEST = enum.auto()

def global_location_id(scenario_id: int, local_location_id: int) -> int:
    return scenario_id * 100 + local_location_id

class Age2Location(enum.IntEnum):
    
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
    
    
location_from_id = {_location.id: _location for _location in Age2Location}
location_name_to_id = {_location.global_name(): _location.id for _location in Age2Location}
location_id_to_name = {_location.id: _location.global_name() for _location in Age2Location}
SCENARIO_TO_LOCATIONS: dict[Age2ScenarioData, list[Age2Location]] = {_scenario: [] for _scenario in Age2ScenarioData}
for _location in Age2Location:
    SCENARIO_TO_LOCATIONS[_location.scenario].append(_location)