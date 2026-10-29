from typing import TYPE_CHECKING

from rule_builder.rules import False_, Has, HasAny, Rule, True_
from ...locations.Locations import Age2ScenarioLocationData
from ...locations.Buildings import Age2BuildingData
from ...items.Items import Age2ItemData
from ...locations.Ages import Age2AgeData
from ...locations.UnitLines import Age2UnitLineData

from ...locations.Units import Age2UnitData as U
from ..custom_logic.EconomyRoutes import Strength
from ..ScenarioLogic import ScenarioStartingState
from ...locations.Players import Age2PlayerData


if TYPE_CHECKING:
    from ..Logic import Logic
    from ..ScenarioLogic import ScenarioLogic

class Joan2StartingState(ScenarioStartingState):

    def __init__(self, logic: 'Logic'):
        super().__init__()
        self.logic = logic
        self.is_unlocked = Has(Age2ScenarioLocationData.JOAN1_VICTORY.scenario.scenario_name + ": Unlock Next Scenario") & Has(Age2ItemData.PROGRESSIVE_JOAN_SCENARIO.item_name)
        has_carts = Has(Age2ItemData.AP_JOAN_2_TRADE_CARTS.item_name)
        has_dock = Has(Age2ItemData.AP_JOAN_2_DOCK.item_name)
        can_reach_orleans = Has(Age2ItemData.AP_JOAN_2_ORLEANS.item_name) & (has_carts | has_dock)

        self.has_vils = can_reach_orleans
        self.housing[Strength.AT_SCALE] = can_reach_orleans
        self.starts_with_building[Age2BuildingData.TOWN_CENTER] = can_reach_orleans
        self.starts_with_building[Age2BuildingData.MILL] = can_reach_orleans
        self.starts_with_building[Age2BuildingData.ARCHERY_RANGE] = can_reach_orleans
        self.starts_with_building[Age2BuildingData.BARRACKS] = can_reach_orleans
        self.starts_with_building[Age2BuildingData.STABLE] = can_reach_orleans
        self.starts_with_building[Age2BuildingData.BLACKSMITH] = can_reach_orleans
        self.starts_with_building[Age2BuildingData.MARKET] = can_reach_orleans
        self.starts_with_building[Age2BuildingData.DOCK] = has_dock

        self.obtains_unit[U.CROSSBOWMAN] = has_carts
        self.obtains_unit[U.KNIGHT] = has_carts
        self.obtains_unit[U.TRADE_CART] = has_carts
        self.obtains_unit[U.VILLAGER_MALE] = can_reach_orleans
        self.obtains_unit[U.VILLAGER_FEMALE] = can_reach_orleans
        self.obtains_unit[U.TRANSPORT_SHIP] = has_dock

    def defeat_rules(self, scenario_logic: 'ScenarioLogic') -> dict[Age2PlayerData, Rule]:
        military = scenario_logic.military
        return {
            Age2PlayerData.JOAN2_BURGUNDY: military.counters_building(),
            Age2PlayerData.JOAN2_NORTHERN_ENGLISH: (
                military.has_siege() &
                military.counters(Age2UnitLineData.LONGBOWMAN_LINE, Age2AgeData.CASTLE) &
                military.counters(Age2UnitLineData.MILITIA_LINE, Age2AgeData.CASTLE)
            ),
            Age2PlayerData.JOAN2_SOUTHERN_ENGLISH: (
                military.has_siege() &
                military.counters(Age2UnitLineData.KNIGHT_LINE, Age2AgeData.CASTLE) &
                military.counters(Age2UnitLineData.BATTERING_RAM_LINE, Age2AgeData.CASTLE)
            ),
        }
