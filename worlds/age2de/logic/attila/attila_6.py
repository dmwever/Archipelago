from typing import TYPE_CHECKING

from rule_builder.rules import Has, True_
from ...locations.Buildings import Age2BuildingData
from ...locations.Locations import Age2ScenarioLocationData
from ...locations.Ages import Age2AgeData

from ..ScenarioLogic import ScenarioStartingState, DARK_START, VANILLA_AGE_START


if TYPE_CHECKING:
    from ..Logic import Logic

class Attila6StartingState(ScenarioStartingState):

    def __init__(self, logic: 'Logic'):
        super().__init__()
        self.logic = logic
        self.is_unlocked = Has(Age2ScenarioLocationData.ATT5_VICTORY.scenario.scenario_name + ": Unlock Next Scenario") & Has("Progressive Attila Scenario", 5)
        self.has_base = logic.buildings.has_building(Age2BuildingData.HOUSE)
        self.age_playable[Age2AgeData.DARK] = logic.ages.can_reach(Age2AgeData.DARK) & DARK_START
        self.age_playable[Age2AgeData.FEUDAL] = logic.ages.can_reach(Age2AgeData.FEUDAL) & DARK_START
        self.age_playable[Age2AgeData.CASTLE] = logic.ages.can_reach(Age2AgeData.CASTLE) & DARK_START
        self.age_playable[Age2AgeData.IMPERIAL] = logic.ages.can_reach(Age2AgeData.IMPERIAL) | VANILLA_AGE_START
