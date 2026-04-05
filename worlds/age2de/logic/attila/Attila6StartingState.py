from typing import TYPE_CHECKING

from rule_builder.rules import Has, True_
from ...locations.Locations import Age2ScenarioLocationData
from ...locations.Ages import Age2AgeData

from ..ScenarioLogic import ScenarioStartingState


if TYPE_CHECKING:
    from ..Logic import Logic

class Attila6StartingState(ScenarioStartingState):

    def __init__(self, logic: 'Logic'):
        super().__init__()
        self.logic = logic
        self.is_unlocked = Has(Age2ScenarioLocationData.ATT5_VICTORY.scenario.scenario_name + ": Unlock Next Scenario") & Has("Progressive Attila Scenario", 5)
        self.can_reach_age[Age2AgeData.FEUDAL] = True_()
        self.can_reach_age[Age2AgeData.CASTLE] = True_()
        self.can_reach_age[Age2AgeData.IMPERIAL] = True_()