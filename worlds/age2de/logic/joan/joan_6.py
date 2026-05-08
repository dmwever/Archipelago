from typing import TYPE_CHECKING

from rule_builder.rules import False_, Has, HasAny, Rule, True_
from ...locations.Locations import Age2ScenarioLocationData
from ...locations.Buildings import Age2BuildingData
from ...locations.Ages import Age2AgeData
from ...items.Items import Age2ItemData

from ..ScenarioLogic import ScenarioStartingState


if TYPE_CHECKING:
    from ..Logic import Logic

class Joan6StartingState(ScenarioStartingState):

    def __init__(self, logic: 'Logic'):
        super().__init__()
        self.rules = logic
        self.is_unlocked = Has(Age2ScenarioLocationData.JOAN5_VICTORY.scenario.scenario_name + ": Unlock Next Scenario") & Has("Progressive Joan of Arc Scenario", 5)
        self.has_tc = Has(Age2ItemData.AP_JOAN_6_ARMY.item_name) & self.rules.buildings.can_build_tc()
        self.has_vils = Has(Age2ItemData.AP_JOAN_6_ARMY.item_name)
        self.can_reach_age[Age2AgeData.FEUDAL] = True_()
        self.can_reach_age[Age2AgeData.CASTLE] = True_()
        self.can_reach_age[Age2AgeData.IMPERIAL] = self.has_tc