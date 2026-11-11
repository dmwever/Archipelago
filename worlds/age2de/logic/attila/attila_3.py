from typing import TYPE_CHECKING

from rule_builder.rules import Has, HasAny, Rule, True_
from ...locations.Locations import Age2ScenarioLocationData
from ...locations.Buildings import Age2BuildingData
from ...items.Items import Age2ItemData, Resource

from ..ScenarioLogic import ScenarioStartingState
from ...locations.Players import Age2PlayerData


if TYPE_CHECKING:
    from ..Logic import Logic
    from ..ScenarioLogic import ScenarioLogic

class Attila3StartingState(ScenarioStartingState):

    def __init__(self, logic: 'Logic'):
        super().__init__()
        self.logic = logic
        self.is_unlocked = Has(Age2ScenarioLocationData.ATT2_VICTORY.scenario.scenario_name + ": Unlock Next Scenario") & Has("Progressive Attila Scenario", 2)
        self.starts_with_building[Age2BuildingData.TOWN_CENTER] = True_()
        self.starts_with_building[Age2BuildingData.ARCHERY_RANGE] = True_()
        self.starts_with_building[Age2BuildingData.STABLE] = True_()
        self.starts_with_building[Age2BuildingData.MILL] = True_()
        self.starts_with_building[Age2BuildingData.BLACKSMITH] = True_()

        gold_lump = HasAny(Age2ItemData.AP_ATTILA_3_RED_GOLD.item_name,
                           Age2ItemData.AP_ATTILA_3_GREEN_GOLD.item_name)
        self.easy_resource_sources[Resource.GOLD] = gold_lump

    def defeat_rules(self, scenario_logic: 'ScenarioLogic') -> dict[Age2PlayerData, Rule]:
        military = scenario_logic.military
        # The scenario treats the two cities as interchangeable, so they share one rule.
        can_defeat_a_city: Rule = military.has_military() & military.counters_building()
        return {
            Age2PlayerData.ATT3_CONSTANTINOPLE: military.has_military() & military.has_siege(),
            Age2PlayerData.ATT3_MARCIANOPOLIS: can_defeat_a_city,
            Age2PlayerData.ATT3_PHILIPPOPOLIS: can_defeat_a_city,
        }

    def trade_guard_rules(
        self,
        scenario_logic: 'ScenarioLogic',
    ) -> dict[tuple[Age2PlayerData, Age2BuildingData], Rule]:
        military = scenario_logic.military
        return {
            (Age2PlayerData.ATT3_CONSTANTINOPLE, Age2BuildingData.DOCK): military.can_guard_boats(),
        }
