from typing import TYPE_CHECKING

from rule_builder.rules import Has, True_
from ...locations.Locations import Age2ScenarioLocationData
from ...locations.Ages import Age2AgeData

from ..ScenarioLogic import ScenarioStartingState, NOT_DARK_START


if TYPE_CHECKING:
    from ..Logic import Logic

class Joan3StartingState(ScenarioStartingState):

    def __init__(self, logic: 'Logic'):
        super().__init__()
        self.rules = logic
        self.is_unlocked = Has(Age2ScenarioLocationData.JOAN2_VICTORY.scenario.scenario_name + ": Unlock Next Scenario") & Has("Progressive Joan of Arc Scenario", 2)
        self.has_base = logic.can_build_base()
        self.has_vils = True_()
        self.can_reach_age[Age2AgeData.DARK] = True_()
        self.can_reach_age[Age2AgeData.FEUDAL] = logic.ages.can_reach(Age2AgeData.FEUDAL) | NOT_DARK_START
        self.can_reach_age[Age2AgeData.CASTLE] = logic.ages.can_reach(Age2AgeData.CASTLE)