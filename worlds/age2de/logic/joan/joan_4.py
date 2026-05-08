from typing import TYPE_CHECKING

from rule_builder.rules import False_, Has, HasAny, Rule, True_
from ...locations.Locations import Age2ScenarioLocationData
from ...locations.Buildings import Age2BuildingData
from ...locations.Ages import Age2AgeData
from ...items.Items import Age2ItemData

from ..ScenarioLogic import ScenarioStartingState


if TYPE_CHECKING:
    from ..Logic import Logic

class Joan4StartingState(ScenarioStartingState):

    def __init__(self, logic: 'Logic'):
        super().__init__()
        self.rules = logic
        self.is_unlocked = Has(Age2ScenarioLocationData.JOAN3_VICTORY.scenario.scenario_name + ": Unlock Next Scenario") & Has("Progressive Joan of Arc Scenario", 3)
        self.has_tc = Has(Age2ItemData.AP_JOAN_4_FRENCH_CAMP.item_name)
        self.has_vils = Has(Age2ItemData.AP_JOAN_4_FRENCH_CAMP.item_name)
        self.can_reach_age[Age2AgeData.FEUDAL] = True_()
        self.can_reach_age[Age2AgeData.CASTLE] = True_()
        self.can_reach_age[Age2AgeData.IMPERIAL] = Has(Age2ItemData.AP_JOAN_4_FRENCH_CAMP.item_name)