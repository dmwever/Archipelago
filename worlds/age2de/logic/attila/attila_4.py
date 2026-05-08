from typing import TYPE_CHECKING

from rule_builder.rules import False_, Has, Rule, True_
from ...locations.Locations import Age2ScenarioLocationData
from ...locations.Buildings import Age2BuildingData
from ...locations.Ages import Age2AgeData
from ...items.Items import Age2ItemData

from ..ScenarioLogic import ScenarioStartingState


if TYPE_CHECKING:
    from ..Logic import Logic

class Attila4StartingState(ScenarioStartingState):

    def __init__(self, logic: 'Logic'):
        super().__init__()
        self.logic = logic
        self.is_unlocked = Has(Age2ScenarioLocationData.ATT3_VICTORY.scenario.scenario_name + ": Unlock Next Scenario") & Has("Progressive Attila Scenario", 3)
        self.has_tc = self.logic.buildings.can_build_tc()
        self.can_reach_age[Age2AgeData.FEUDAL] = True_()
        self.can_reach_age[Age2AgeData.CASTLE] = True_()
        self.can_reach_age[Age2AgeData.IMPERIAL] = self.logic.ages.can_reach_imperial()