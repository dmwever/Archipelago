from typing import TYPE_CHECKING

from rule_builder.rules import False_, Has, Rule, True_
from ...locations.Buildings import Age2BuildingData
from ...locations.Locations import Age2ScenarioLocationData
from ...locations.Units import Age2UnitData
from ...items.Items import Age2ItemData

from ..ScenarioLogic import ScenarioStartingState


if TYPE_CHECKING:
    from ..Logic import Logic

class Genghis4StartingState(ScenarioStartingState):
    kipchak_camp: Rule = Has(Age2ItemData.AP_GENGHIS_4_KIPCHAK_CAMP.item_name)

    def __init__(self, logic: 'Logic'):
        super().__init__()
        self.logic = logic
        self.is_unlocked = Has(Age2ScenarioLocationData.GEN3_VICTORY.scenario.scenario_name + ": Unlock Next Scenario") & Has("Progressive Genghis Khan Scenario", 3)

        # Two town centres and five villagers, north and south: the first chapter that
        # opens with an economy of its own.
        self.starts_with_building[Age2BuildingData.TOWN_CENTER] = True_()


        # The Kipchaks hand their camp over once they surrender, buildings and all.
        self.starts_with_building[Age2BuildingData.ARCHERY_RANGE] = self.kipchak_camp
        self.starts_with_building[Age2BuildingData.MARKET] = self.kipchak_camp
        self.starts_with_building[Age2BuildingData.MONASTERY] = self.kipchak_camp
        self.starts_with_building[Age2BuildingData.MILL] = self.kipchak_camp
        self.starts_with_building[Age2BuildingData.MINING_CAMP] = self.kipchak_camp

        # Two champions step out of the trade carts when they reach the Shah, and reaching
        # him costs nothing.
        self.obtains_unit[Age2UnitData.CHAMPION] = True_()
