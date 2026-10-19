from typing import TYPE_CHECKING

from rule_builder.rules import Has, Rule, True_
from ...locations.Buildings import Age2BuildingData
from ...locations.Locations import Age2ScenarioLocationData
from ...locations.Ages import Age2AgeData
from ...locations.UnitLines import Age2UnitLineData

from ..ScenarioLogic import ScenarioStartingState
from ..ScenarioPlayer import ScenarioPlayer


if TYPE_CHECKING:
    from ..Logic import Logic
    from ..ScenarioLogic import ScenarioLogic

class Attila6Player(ScenarioPlayer):
    """The Western Roman Empire fights beside P1, so it has no member."""
    AQUILEIA = 2, "Aquileia"
    MEDIOLANUM = 3, "Mediolanum"
    VERONA = 4, "Verona"
    PATAVIUM = 5, "Patavium"

class Attila6StartingState(ScenarioStartingState):

    def __init__(self, logic: 'Logic'):
        super().__init__()
        self.logic = logic
        self.is_unlocked = Has(Age2ScenarioLocationData.ATT5_VICTORY.scenario.scenario_name + ": Unlock Next Scenario") & Has("Progressive Attila Scenario", 5)
        self.has_base = True_()   # a Town Centre stands on the map at player one
        self.starts_with_building[Age2BuildingData.TOWN_CENTER] = True_()

    def defeat_rules(self, scenario_logic: 'ScenarioLogic') -> dict[ScenarioPlayer, Rule]:
        military = scenario_logic.military
        return {
            Attila6Player.AQUILEIA: (
                scenario_logic.has_base() &
                military.counters(Age2UnitLineData.SPEARMAN_LINE, Age2AgeData.IMPERIAL) &
                military.counters(Age2UnitLineData.SCOUT_CAVALRY_LINE, Age2AgeData.IMPERIAL) &
                military.counters(Age2UnitLineData.KNIGHT_LINE, Age2AgeData.IMPERIAL) &
                military.counters(Age2UnitLineData.SCORPION_LINE, Age2AgeData.IMPERIAL) &
                military.has_siege()
            ),
            Attila6Player.MEDIOLANUM: (
                (
                    scenario_logic.has_base() &
                    military.has_navy(Age2AgeData.IMPERIAL) &
                    military.has_naval_bombardment()
                ) |
                (
                    scenario_logic.has_base() &
                    military.counters(Age2UnitLineData.ARCHER_LINE, Age2AgeData.IMPERIAL) &
                    military.counters(Age2UnitLineData.KNIGHT_LINE, Age2AgeData.IMPERIAL) &
                    military.counters(Age2UnitLineData.MANGONEL_LINE, Age2AgeData.IMPERIAL) &
                    military.counters(Age2UnitLineData.TREBUCHET_LINE, Age2AgeData.IMPERIAL)
                )
            ),
            Attila6Player.PATAVIUM: (
                scenario_logic.has_base() &
                military.counters(Age2UnitLineData.MILITIA_LINE, Age2AgeData.IMPERIAL) &
                military.counters(Age2UnitLineData.ARCHER_LINE, Age2AgeData.IMPERIAL) &
                military.counters(Age2UnitLineData.LONGBOWMAN_LINE, Age2AgeData.IMPERIAL) &
                military.counters(Age2UnitLineData.MANGONEL_LINE, Age2AgeData.IMPERIAL) &
                military.has_long_range_siege()
            ),
            Attila6Player.VERONA: (
                scenario_logic.has_base() &
                military.counters(Age2UnitLineData.ARCHER_LINE, Age2AgeData.IMPERIAL) &
                military.counters(Age2UnitLineData.THROWING_AXEMAN_LINE, Age2AgeData.IMPERIAL) &
                military.counters(Age2UnitLineData.KNIGHT_LINE, Age2AgeData.IMPERIAL) &
                military.counters(Age2UnitLineData.TREBUCHET_LINE, Age2AgeData.IMPERIAL) &
                military.counters(Age2UnitLineData.MONK_LINE, Age2AgeData.CASTLE) &
                military.has_long_range_siege()
            ),
        }
