from typing import TYPE_CHECKING

from rule_builder.rules import False_, Has, HasAny, Rule, True_
from ...locations.Locations import Age2ScenarioLocationData
from ...locations.Buildings import Age2BuildingData
from ...items.Items import Age2ItemData, Resource

from ..ScenarioLogic import ScenarioStartingState
from ..ScenarioPlayer import ScenarioPlayer


if TYPE_CHECKING:
    from ..Logic import Logic
    from ..ScenarioLogic import ScenarioLogic

class Attila3Player(ScenarioPlayer):
    CONSTANTINOPLE = 2, "Constantinople"
    MARCIANOPOLIS = 3, "Marcianopolis"
    PHILIPPOPOLIS = 4, "Philippopolis"

class Attila3StartingState(ScenarioStartingState):

    def __init__(self, logic: 'Logic'):
        super().__init__()
        self.logic = logic
        self.is_unlocked = Has(Age2ScenarioLocationData.ATT2_VICTORY.scenario.scenario_name + ": Unlock Next Scenario") & Has("Progressive Attila Scenario", 2)
        self.has_base = True_()   # a Town Centre stands on the map at player one
        self.starts_with_building[Age2BuildingData.TOWN_CENTER] = True_()
        self.starts_with_building[Age2BuildingData.ARCHERY_RANGE] = True_()
        self.starts_with_building[Age2BuildingData.STABLE] = True_()
        self.starts_with_building[Age2BuildingData.MILL] = True_()
        self.starts_with_building[Age2BuildingData.BLACKSMITH] = True_()

        gold_lump = HasAny(Age2ItemData.AP_ATTILA_3_RED_GOLD.item_name,
                           Age2ItemData.AP_ATTILA_3_GREEN_GOLD.item_name)
        self.easy_resource_sources[Resource.GOLD] = gold_lump

    def defeat_rules(self, scenario_logic: 'ScenarioLogic') -> dict[ScenarioPlayer, Rule]:
        military = scenario_logic.military
        # The scenario treats the two cities as interchangeable, so they share one rule.
        can_defeat_a_city: Rule = military.has_military() & military.counters_building()
        return {
            Attila3Player.CONSTANTINOPLE: military.has_military() & military.has_siege(),
            Attila3Player.MARCIANOPOLIS: can_defeat_a_city,
            Attila3Player.PHILIPPOPOLIS: can_defeat_a_city,
        }
