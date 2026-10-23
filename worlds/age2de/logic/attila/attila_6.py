from typing import TYPE_CHECKING

from rule_builder.rules import Has, Rule, True_
from ...locations.Buildings import Age2BuildingData
from ...locations.Locations import Age2ScenarioLocationData
from ...locations.Ages import Age2AgeData
from ...locations.UnitLines import Age2UnitLineData

from ..ScenarioLogic import ScenarioStartingState
from ...locations.Players import Age2PlayerData


if TYPE_CHECKING:
    from ..Logic import Logic
    from ..ScenarioLogic import ScenarioLogic

class Attila6StartingState(ScenarioStartingState):

    def __init__(self, logic: 'Logic'):
        super().__init__()
        self.logic = logic
        self.is_unlocked = Has(Age2ScenarioLocationData.ATT5_VICTORY.scenario.scenario_name + ": Unlock Next Scenario") & Has("Progressive Attila Scenario", 5)
        self.starts_with_building[Age2BuildingData.TOWN_CENTER] = True_()

    def defeat_rules(self, scenario_logic: 'ScenarioLogic') -> dict[Age2PlayerData, Rule]:
        military = scenario_logic.military
        return {
            Age2PlayerData.ATT6_AQUILEIA: (
                military.counters(Age2UnitLineData.SPEARMAN_LINE, Age2AgeData.IMPERIAL) &
                military.counters(Age2UnitLineData.SCOUT_CAVALRY_LINE, Age2AgeData.IMPERIAL) &
                military.counters(Age2UnitLineData.KNIGHT_LINE, Age2AgeData.IMPERIAL) &
                military.counters(Age2UnitLineData.SCORPION_LINE, Age2AgeData.IMPERIAL) &
                military.has_siege()
            ),
            Age2PlayerData.ATT6_MEDIOLANUM: (
                (
                    military.has_navy(Age2AgeData.IMPERIAL) &
                    military.has_naval_bombardment()
                ) |
                (
                    military.counters(Age2UnitLineData.ARCHER_LINE, Age2AgeData.IMPERIAL) &
                    military.counters(Age2UnitLineData.KNIGHT_LINE, Age2AgeData.IMPERIAL) &
                    military.counters(Age2UnitLineData.MANGONEL_LINE, Age2AgeData.IMPERIAL) &
                    military.counters(Age2UnitLineData.TREBUCHET_LINE, Age2AgeData.IMPERIAL)
                )
            ),
            Age2PlayerData.ATT6_PATAVIUM: (
                military.counters(Age2UnitLineData.MILITIA_LINE, Age2AgeData.IMPERIAL) &
                military.counters(Age2UnitLineData.ARCHER_LINE, Age2AgeData.IMPERIAL) &
                military.counters(Age2UnitLineData.LONGBOWMAN_LINE, Age2AgeData.IMPERIAL) &
                military.counters(Age2UnitLineData.MANGONEL_LINE, Age2AgeData.IMPERIAL) &
                military.has_long_range_siege()
            ),
            Age2PlayerData.ATT6_VERONA: (
                military.counters(Age2UnitLineData.ARCHER_LINE, Age2AgeData.IMPERIAL) &
                military.counters(Age2UnitLineData.THROWING_AXEMAN_LINE, Age2AgeData.IMPERIAL) &
                military.counters(Age2UnitLineData.KNIGHT_LINE, Age2AgeData.IMPERIAL) &
                military.counters(Age2UnitLineData.TREBUCHET_LINE, Age2AgeData.IMPERIAL) &
                military.counters(Age2UnitLineData.MONK_LINE, Age2AgeData.CASTLE) &
                military.has_long_range_siege()
            ),
        }
