from typing import TYPE_CHECKING

from rule_builder.rules import False_, Has, Rule, True_
from ...locations.Locations import Age2ScenarioLocationData
from ...locations.Buildings import Age2BuildingData
from ...locations.Ages import Age2AgeData
from ...items.Items import Age2ItemData

from ..ScenarioLogic import ScenarioStartingState


if TYPE_CHECKING:
    from ..Logic import Logic

class Attila1StartingState(ScenarioStartingState):
    purple_vils: Rule = Has(Age2ItemData.AP_ATTILA_2_VILLAGERS.item_name)

    def __init__(self, logic: 'Logic'):
        super().__init__()
        self.rules = logic
        self.is_unlocked = Has(Age2ScenarioLocationData.ATT1_VICTORY.scenario.scenario_name + ": Unlock Next Scenario") & Has("Progressive Attila Scenario")
        self.has_vils = self.purple_vils
        self.has_tc = logic.buildings.can_build_tc() & self.purple_vils
        self.has_ages[Age2AgeData.DARK] = True_()
        self.can_reach_age[Age2AgeData.FEUDAL] = True_()
        self.can_reach_age[Age2AgeData.CASTLE] = True_()