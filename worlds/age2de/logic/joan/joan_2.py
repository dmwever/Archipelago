from typing import TYPE_CHECKING

from rule_builder.rules import False_, Has, HasAny, Rule, True_
from ...locations.Locations import Age2ScenarioLocationData
from ...locations.Buildings import Age2BuildingData
from ...items.Items import Age2ItemData
from ...locations.Ages import Age2AgeData
from ...locations.UnitLines import Age2UnitLineData

from ...locations.Units import Age2UnitData as U
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
        has_orleans = Has(Age2ItemData.AP_JOAN_2_ORLEANS.item_name)

        self.has_vils = has_orleans
        self.starts_with_building[Age2BuildingData.TOWN_CENTER] = has_orleans
        self.starts_with_building[Age2BuildingData.MILL] = has_orleans
        self.starts_with_building[Age2BuildingData.ARCHERY_RANGE] = has_orleans
        self.starts_with_building[Age2BuildingData.BARRACKS] = has_orleans
        self.starts_with_building[Age2BuildingData.STABLE] = has_orleans
        self.starts_with_building[Age2BuildingData.BLACKSMITH] = has_orleans
        self.starts_with_building[Age2BuildingData.MARKET] = has_orleans

        self.obtains_unit[U.CROSSBOWMAN] = has_carts
        self.obtains_unit[U.KNIGHT] = has_carts
        self.obtains_unit[U.TRADE_CART] = has_carts
        self.obtains_unit[U.VILLAGER_MALE] = has_orleans
        self.obtains_unit[U.VILLAGER_FEMALE] = has_orleans
        self.obtains_unit[U.TRANSPORT_SHIP] = Has(Age2ItemData.AP_JOAN_2_DOCK.item_name)

    def defeat_rules(self, scenario_logic: 'ScenarioLogic') -> dict[Age2PlayerData, Rule]:
        military = scenario_logic.military
        return {
            Age2PlayerData.JOAN2_BURGUNDY: scenario_logic.has_base() & military.counters_building(),
            Age2PlayerData.JOAN2_NORTHERN_ENGLISH: (
                scenario_logic.has_base() &
                military.has_siege() &
                military.counters(Age2UnitLineData.LONGBOWMAN_LINE, Age2AgeData.CASTLE) &
                military.counters(Age2UnitLineData.MILITIA_LINE, Age2AgeData.CASTLE)
            ),
            Age2PlayerData.JOAN2_SOUTHERN_ENGLISH: (
                scenario_logic.has_base() &
                military.has_siege() &
                military.counters(Age2UnitLineData.KNIGHT_LINE, Age2AgeData.CASTLE) &
                military.counters(Age2UnitLineData.BATTERING_RAM_LINE, Age2AgeData.CASTLE)
            ),
        }
