
import enum
from BaseClasses import Location
from worlds.age2de import AGE2_DE
from worlds.age2de.locations.Scenarios import Age2ScenarioData

class Age2LocationType(enum.Flag):
    VICTORY = enum.auto()
    OBJECTIVE = enum.auto()
    SIDE_QUEST = enum.auto()

def global_location_id(scenario_id: int, local_location_id: int) -> int:
    return scenario_id * 100 + local_location_id

class Age2Location(Location):  # or from Locations import MyGameLocation
    game = AGE2_DE  # name of the game/world this location is in
    
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
    
    #Attila 2 specific locations
    ATT2_VICTORY =          10200, "Attila, The Great Ride: Victory",                            Age2ScenarioData.C1_ATTILA_2, Age2LocationType.VICTORY
    ATT2_RED_TC =           10201, "Attila, The Great Ride: Destroy the Red Town Center",        Age2ScenarioData.C1_ATTILA_2, Age2LocationType.SIDE_QUEST
    ATT2_GREEN_LUMBER =     10202, "Attila, The Great Ride: Destroy the Green Lumber Camp",      Age2ScenarioData.C1_ATTILA_2, Age2LocationType.SIDE_QUEST
    ATT2_PURPLE_VILS =      10203, "Attila, The Great Ride: Destroy the Purple Houses",          Age2ScenarioData.C1_ATTILA_2, Age2LocationType.SIDE_QUEST
    ATT2_GREY_MINING =      10204, "Attila, The Great Ride: Destroy the Grey Mining Camps",      Age2ScenarioData.C1_ATTILA_2, Age2LocationType.SIDE_QUEST
    ATT2_CYAN_TC =          10205, "Attila, The Great Ride: Destroy the Cyan Town Center",       Age2ScenarioData.C1_ATTILA_2, Age2LocationType.SIDE_QUEST
    ATT2_SCYTHIAN_VILS =    10206, "Attila, The Great Ride: Give 6 Villagers to the Scythians",  Age2ScenarioData.C1_ATTILA_2, Age2LocationType.SIDE_QUEST
    ATT2_BUILD_TC =         10207, "Attila, The Great Ride: Build a Town Center",                Age2ScenarioData.C1_ATTILA_2, Age2LocationType.OBJECTIVE
    ATT2_BEAT_THE_ROMANS =  10207, "Attila, The Great Ride: Beat the Romans",                    Age2ScenarioData.C1_ATTILA_2, Age2LocationType.OBJECTIVE
    
    
location_from_id = {_location.id: _location for _location in Age2Location}
location_name_to_id = {_location.global_name(): _location.id for _location in Age2Location}
location_id_to_name = {_location.id: _location.global_name() for _location in Age2Location}
SCENARIO_TO_LOCATIONS: dict[Age2ScenarioData, list[Age2Location]] = {_scenario: [] for _scenario in Age2ScenarioData}
for _location in Age2Location:
    SCENARIO_TO_LOCATIONS[_location.scenario].append(_location)