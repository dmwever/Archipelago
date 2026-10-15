from typing import TYPE_CHECKING

from rule_builder.rules import False_, Has, Rule, True_
from ...locations.Ages import Age2AgeData
from ...locations.Buildings import Age2BuildingData
from ...locations.Locations import Age2ScenarioLocationData
from ...locations.Units import Age2UnitData
from ...items.Items import Age2ItemData

from ..ScenarioLogic import ScenarioStartingState

if TYPE_CHECKING:
    from ..Logic import Logic

class Genghis2StartingState(ScenarioStartingState):
    tayichiud_base: Rule = Has(Age2ItemData.AP_GENGHIS_2_TAYICHIUD_BASE.item_name)

    def __init__(self, logic: 'Logic'):
        super().__init__()
        self.logic = logic
        self.is_unlocked = Has(Age2ScenarioLocationData.GEN1_VICTORY.scenario.scenario_name + ": Unlock Next Scenario") & Has("Progressive Genghis Khan Scenario", 1)
        self.max_age = Age2AgeData.CASTLE
        self.has_water_access = False_()

        # Temujin opens with eleven riders and a Wonder. The Tayichi'ud village is the only
        # Town Centre or villager he can ever reach, so it is the whole economy.
        self.has_vils = self.tayichiud_base
        self.obtains_unit[Age2UnitData.VILLAGER_MALE] = self.tayichiud_base
        self.obtains_unit[Age2UnitData.VILLAGER_FEMALE] = self.tayichiud_base
        self.starts_with_building[Age2BuildingData.TOWN_CENTER] = self.tayichiud_base
        self.starts_with_building[Age2BuildingData.BARRACKS] = self.tayichiud_base
        self.starts_with_building[Age2BuildingData.MILL] = self.tayichiud_base
