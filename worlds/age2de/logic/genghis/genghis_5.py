from typing import TYPE_CHECKING

from rule_builder.rules import False_, Has, Rule, True_
from ...locations.Buildings import Age2BuildingData
from ...locations.Locations import Age2ScenarioLocationData
from ...locations.Units import Age2UnitData
from ...items.Items import Age2ItemData
from ...locations.Ages import Age2AgeData
from ...locations.UnitLines import Age2UnitLineData

from ..ScenarioLogic import ScenarioStartingState
from ..ScenarioPlayer import ScenarioPlayer

if TYPE_CHECKING:
    from ..Logic import Logic
    from ..ScenarioLogic import ScenarioLogic

class Genghis5Player(ScenarioPlayer):
    BOHEMIANS = 3, "the Bohemians"
    GERMANS = 4, "the Germans"

class Genghis5StartingState(ScenarioStartingState):

    def __init__(self, logic: 'Logic'):
        super().__init__()
        self.logic = logic
        self.is_unlocked = Has(Age2ScenarioLocationData.GEN4_VICTORY.scenario.scenario_name + ": Unlock Next Scenario") & Has("Progressive Genghis Khan Scenario", 4)

        # One town centre, four villagers, three Mangudai and a Mangonel.
        self.starts_with_building[Age2BuildingData.TOWN_CENTER] = True_()

        # A scout rides in unasked early on.
        self.obtains_unit[Age2UnitData.SCOUT_CAVALRY] = True_()

    def defeat_rules(self, scenario_logic: 'ScenarioLogic') -> dict[ScenarioPlayer, Rule]:
        military = scenario_logic.military
        return {
            Genghis5Player.GERMANS: (
                scenario_logic.has_base() &
                military.has_military(Age2AgeData.CASTLE) &
                military.counters(Age2UnitLineData.ARCHER_LINE, Age2AgeData.CASTLE) &
                military.counters(Age2UnitLineData.SPEARMAN_LINE, Age2AgeData.CASTLE) &
                military.counters(Age2UnitLineData.TEUTONIC_KNIGHT_LINE, Age2AgeData.CASTLE) &
                military.counters(Age2UnitLineData.BATTERING_RAM_LINE, Age2AgeData.CASTLE) &
                military.has_siege() &
                scenario_logic.ages.can_reach(Age2AgeData.CASTLE)
            ),
            Genghis5Player.BOHEMIANS: (
                scenario_logic.has_base() &
                military.has_military(Age2AgeData.IMPERIAL) &
                military.counters(Age2UnitLineData.MILITIA_LINE, Age2AgeData.IMPERIAL) &
                military.counters(Age2UnitLineData.KNIGHT_LINE, Age2AgeData.IMPERIAL) &
                military.counters(Age2UnitLineData.MANGONEL_LINE, Age2AgeData.IMPERIAL) &
                military.counters(Age2UnitLineData.BATTERING_RAM_LINE, Age2AgeData.IMPERIAL) &
                military.counters(Age2UnitLineData.TREBUCHET_LINE, Age2AgeData.IMPERIAL) &
                military.counters(Age2UnitLineData.MONK_LINE, Age2AgeData.IMPERIAL) &
                military.has_long_range_siege() &
                scenario_logic.ages.can_reach(Age2AgeData.IMPERIAL)
            ),
        }
