from typing import TYPE_CHECKING

from rule_builder.rules import False_, Has, Rule, True_
from ...locations.Locations import Age2ScenarioLocationData
from ...locations.Buildings import Age2BuildingData
from ...locations.Ages import Age2AgeData
from ...items.Items import Age2ItemData

from ..ScenarioLogic import ScenarioStartingState


if TYPE_CHECKING:
    from ..Logic import Logic

class Attila3StartingState(ScenarioStartingState):

    def __init__(self, logic: 'Logic'):
        super().__init__()
        self.rules = logic
        self.is_unlocked = Has(Age2ScenarioLocationData.ATT2_VICTORY.scenario.scenario_name + ": Unlock Next Scenario") & Has("Progressive Attila Scenario", 2)
        self.can_reach_age[Age2AgeData.FEUDAL] = True_()
        self.can_reach_age[Age2AgeData.CASTLE] = True_()
        self.starts_with_building[Age2BuildingData.ARCHERY_RANGE] = True_()
        self.starts_with_building[Age2BuildingData.STABLE] = True_()
        self.starts_with_building[Age2BuildingData.MILL] = True_()
        self.starts_with_building[Age2BuildingData.BLACKSMITH] = True_()