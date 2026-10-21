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

    def defeat_rules(self, scenario_logic: 'ScenarioLogic') -> dict[Age2PlayerData, Rule]:
        military = scenario_logic.military
        return {
            # The Kipchaks offer no resistance: they surrender their camp.
            Age2PlayerData.GEN4_KIPCHAKS: True_(),
            Age2PlayerData.GEN4_RUSSIANS: (
                scenario_logic.has_base() &
                military.has_military(Age2AgeData.CASTLE) &
                military.counters(Age2UnitLineData.MILITIA_LINE, Age2AgeData.CASTLE) &
                military.counters(Age2UnitLineData.BOYAR_LINE, Age2AgeData.CASTLE) &
                military.counters(Age2UnitLineData.KNIGHT_LINE, Age2AgeData.CASTLE) &
                military.counters(Age2UnitLineData.BATTERING_RAM_LINE, Age2AgeData.CASTLE) &
                military.has_siege() &
                scenario_logic.ages.can_reach(Age2AgeData.CASTLE)
            ),
            Age2PlayerData.GEN4_KHWARAZM: (
                scenario_logic.has_base() &
                military.has_military(Age2AgeData.IMPERIAL) &
                military.counters(Age2UnitLineData.WAR_ELEPHANT_LINE, Age2AgeData.IMPERIAL) &
                military.counters(Age2UnitLineData.KNIGHT_LINE, Age2AgeData.IMPERIAL) &
                military.counters(Age2UnitLineData.CAVALRY_ARCHER_LINE, Age2AgeData.IMPERIAL) &
                military.counters(Age2UnitLineData.SCORPION_LINE, Age2AgeData.IMPERIAL) &
                military.counters(Age2UnitLineData.TREBUCHET_LINE, Age2AgeData.IMPERIAL) &
                military.counters(Age2UnitLineData.MONK_LINE, Age2AgeData.IMPERIAL) &
                military.has_long_range_siege() &
                scenario_logic.ages.can_reach(Age2AgeData.IMPERIAL)
            ),
        }
