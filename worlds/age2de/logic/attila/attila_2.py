from typing import TYPE_CHECKING

from rule_builder.rules import False_, Has, Rule, True_
from ...locations.Locations import Age2ScenarioLocationData
from ...locations.Buildings import Age2BuildingData
from ...locations.Ages import Age2AgeData
from ...items.Items import Age2ItemData

from ..ScenarioLogic import ScenarioStartingState, DARK_START, VANILLA_AGE_START


if TYPE_CHECKING:
    from ..Logic import Logic

class Attila2StartingState(ScenarioStartingState):
    purple_vils: Rule = Has(Age2ItemData.AP_ATTILA_2_VILLAGERS.item_name)

    def __init__(self, logic: 'Logic'):
        super().__init__()
        self.logic = logic
        self.is_unlocked = Has(Age2ScenarioLocationData.ATT1_VICTORY.scenario.scenario_name + ": Unlock Next Scenario") & Has("Progressive Attila Scenario")
        self.max_age = Age2AgeData.CASTLE
        self.has_vils = self.purple_vils
