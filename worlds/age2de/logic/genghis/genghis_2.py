from typing import TYPE_CHECKING

from rule_builder.rules import False_, Has, Rule, True_
from ...locations.Buildings import Age2BuildingData
from ...locations.Locations import Age2ScenarioLocationData
from ...locations.Units import Age2UnitData
from ...items.Items import Age2ItemData
from ...locations.Ages import Age2AgeData
from ...locations.UnitLines import Age2UnitLineData

from ..ScenarioLogic import ScenarioStartingState
from ...locations.Players import Age2PlayerData

if TYPE_CHECKING:
    from ..Logic import Logic
    from ..ScenarioLogic import ScenarioLogic

class Genghis2StartingState(ScenarioStartingState):
    tayichiud_base: Rule = Has(Age2ItemData.AP_GENGHIS_2_TAYICHIUD_BASE.item_name)

    def __init__(self, logic: 'Logic'):
        super().__init__()
        self.logic = logic
        self.is_unlocked = Has(Age2ScenarioLocationData.GEN1_VICTORY.scenario.scenario_name + ": Unlock Next Scenario") & Has("Progressive Genghis Khan Scenario", 1)
        self.has_water_access = False_()

        # Temujin opens with eleven riders and a Wonder. The Tayichi'ud village is the only
        # Town Centre or villager he can ever reach, so it is the whole economy.
        self.has_vils = self.tayichiud_base
        self.obtains_unit[Age2UnitData.VILLAGER_MALE] = self.tayichiud_base
        self.obtains_unit[Age2UnitData.VILLAGER_FEMALE] = self.tayichiud_base
        self.starts_with_building[Age2BuildingData.TOWN_CENTER] = self.tayichiud_base
        self.starts_with_building[Age2BuildingData.BARRACKS] = self.tayichiud_base
        self.starts_with_building[Age2BuildingData.MILL] = self.tayichiud_base

    def defeat_rules(self, scenario_logic: 'ScenarioLogic') -> dict[Age2PlayerData, Rule]:
        military = scenario_logic.military
        return {
            Age2PlayerData.GEN2_KARA_KHITAI: (
                military.has_military(Age2AgeData.CASTLE) &
                military.counters(Age2UnitLineData.CAVALRY_ARCHER_LINE, Age2AgeData.CASTLE) &
                military.counters(Age2UnitLineData.MILITIA_LINE, Age2AgeData.CASTLE) &
                military.counters(Age2UnitLineData.SCOUT_CAVALRY_LINE, Age2AgeData.CASTLE) &
                military.counters(Age2UnitLineData.SKIRMISHER_LINE, Age2AgeData.CASTLE) &
                military.counters(Age2UnitLineData.ARCHER_LINE, Age2AgeData.CASTLE) &
                military.counters_building() &
                scenario_logic.ages.can_reach(Age2AgeData.CASTLE)
            ),
            Age2PlayerData.GEN2_KUSHLUK: (
                military.has_military(Age2AgeData.CASTLE) &
                military.counters(Age2UnitLineData.CAVALRY_ARCHER_LINE, Age2AgeData.CASTLE) &
                military.counters(Age2UnitLineData.MANGUDAI_LINE, Age2AgeData.CASTLE) &
                military.counters(Age2UnitLineData.MILITIA_LINE, Age2AgeData.CASTLE) &
                military.counters(Age2UnitLineData.SCOUT_CAVALRY_LINE, Age2AgeData.CASTLE) &
                military.counters(Age2UnitLineData.SKIRMISHER_LINE, Age2AgeData.CASTLE) &
                military.counters_building() &
                scenario_logic.ages.can_reach(Age2AgeData.CASTLE)
            ),
        }
