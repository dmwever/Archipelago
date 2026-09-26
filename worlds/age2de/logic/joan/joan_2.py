from typing import TYPE_CHECKING

from rule_builder.rules import False_, Has, HasAny, Rule, True_
from ...locations.Locations import Age2ScenarioLocationData
from ...locations.Buildings import Age2BuildingData
from ...locations.Ages import Age2AgeData
from ...items.Items import Age2ItemData

from ...locations.Units import Age2UnitData as U
from ..ScenarioLogic import ScenarioStartingState, VANILLA_AGE_START


if TYPE_CHECKING:
    from ..Logic import Logic

class Joan2StartingState(ScenarioStartingState):

    def __init__(self, logic: 'Logic'):
        super().__init__()
        self.logic = logic
        self.is_unlocked = Has(Age2ScenarioLocationData.JOAN1_VICTORY.scenario.scenario_name + ": Unlock Next Scenario") & Has(Age2ItemData.PROGRESSIVE_JOAN_SCENARIO.item_name)
        self.max_age = Age2AgeData.CASTLE
        self.has_base = Has(Age2ItemData.AP_JOAN_2_ORLEANS.item_name)
        self.has_vils = Has(Age2ItemData.AP_JOAN_2_ORLEANS.item_name)
        self.starts_with_building[Age2BuildingData.ARCHERY_RANGE] = Has(Age2ItemData.AP_JOAN_2_ORLEANS.item_name)
        self.starts_with_building[Age2BuildingData.BARRACKS] = Has(Age2ItemData.AP_JOAN_2_ORLEANS.item_name)
        self.starts_with_building[Age2BuildingData.STABLE] = Has(Age2ItemData.AP_JOAN_2_ORLEANS.item_name)
        self.starts_with_building[Age2BuildingData.BLACKSMITH] = Has(Age2ItemData.AP_JOAN_2_ORLEANS.item_name)
        self.starts_with_building[Age2BuildingData.MARKET] = Has(Age2ItemData.AP_JOAN_2_ORLEANS.item_name)

        carts = Has(Age2ItemData.AP_JOAN_2_TRADE_CARTS.item_name)
        orleans = Has(Age2ItemData.AP_JOAN_2_ORLEANS.item_name)
        self.obtains_unit[U.CROSSBOWMAN] = carts
        self.obtains_unit[U.KNIGHT] = carts
        self.obtains_unit[U.TRADE_CART] = carts
        self.obtains_unit[U.VILLAGER_MALE] = orleans
        self.obtains_unit[U.VILLAGER_FEMALE] = orleans
        self.obtains_unit[U.TRANSPORT_SHIP] = Has(Age2ItemData.AP_JOAN_2_DOCK.item_name)
