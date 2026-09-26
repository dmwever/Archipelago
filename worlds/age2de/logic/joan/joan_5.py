from typing import TYPE_CHECKING

from rule_builder.rules import False_, Has, HasAny, Rule, True_
from ...locations.Locations import Age2ScenarioLocationData
from ...locations.Buildings import Age2BuildingData
from ...locations.Ages import Age2AgeData
from ...items.Items import Age2ItemData

from ...locations.Units import Age2UnitData as U
from ..ScenarioLogic import ScenarioStartingState


if TYPE_CHECKING:
    from ..Logic import Logic

class Joan5StartingState(ScenarioStartingState):

    def __init__(self, logic: 'Logic'):
        super().__init__()
        self.logic = logic
        self.is_unlocked = Has(Age2ScenarioLocationData.JOAN4_VICTORY.scenario.scenario_name + ": Unlock Next Scenario") & Has("Progressive Joan of Arc Scenario", 4)
        self.has_vils = False_()
        self.fixed_force = True
        
        self.obtains_unit[U.VILLAGER_MALE] = HasAny(
            Age2ItemData.AP_JOAN_5_REFUGEE_1.item_name,
            Age2ItemData.AP_JOAN_5_REFUGEE_2.item_name,
            Age2ItemData.AP_JOAN_5_REFUGEE_3.item_name,
            Age2ItemData.AP_JOAN_5_REFUGEE_5.item_name,
            Age2ItemData.AP_JOAN_5_REFUGEE_6.item_name,
            Age2ItemData.AP_JOAN_5_REFUGEE_10.item_name)
        self.obtains_unit[U.VILLAGER_FEMALE] = HasAny(
            Age2ItemData.AP_JOAN_5_REFUGEE_4.item_name,
            Age2ItemData.AP_JOAN_5_REFUGEE_7.item_name,
            Age2ItemData.AP_JOAN_5_REFUGEE_8.item_name,
            Age2ItemData.AP_JOAN_5_REFUGEE_9.item_name)
