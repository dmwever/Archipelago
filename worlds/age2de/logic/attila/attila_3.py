from typing import TYPE_CHECKING

from rule_builder.rules import False_, Has, HasAny, Rule, True_
from ...locations.Locations import Age2ScenarioLocationData
from ...locations.Buildings import Age2BuildingData
from ...locations.Ages import Age2AgeData
from ...items.Items import Age2ItemData, Resource

from ..ScenarioLogic import ScenarioStartingState


if TYPE_CHECKING:
    from ..Logic import Logic

class Attila3StartingState(ScenarioStartingState):

    def __init__(self, logic: 'Logic'):
        super().__init__()
        self.logic = logic
        self.is_unlocked = Has(Age2ScenarioLocationData.ATT2_VICTORY.scenario.scenario_name + ": Unlock Next Scenario") & Has("Progressive Attila Scenario", 2)
        self.max_age = Age2AgeData.CASTLE
        self.has_base = True_()   # a Town Centre stands on the map at player one
        self.starts_with_building[Age2BuildingData.TOWN_CENTER] = True_()
        self.starts_with_building[Age2BuildingData.ARCHERY_RANGE] = True_()
        self.starts_with_building[Age2BuildingData.STABLE] = True_()
        self.starts_with_building[Age2BuildingData.MILL] = True_()
        self.starts_with_building[Age2BuildingData.BLACKSMITH] = True_()

        gold_lump = HasAny(Age2ItemData.AP_ATTILA_3_RED_GOLD.item_name,
                           Age2ItemData.AP_ATTILA_3_GREEN_GOLD.item_name)
        self.resource_sources[Resource.GOLD] = gold_lump
        self.easy_resource_sources[Resource.GOLD] = gold_lump
