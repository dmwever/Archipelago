from typing import TYPE_CHECKING

from rule_builder.rules import False_, Has, Rule, True_
from ...locations.Locations import Age2ScenarioLocationData
from ...locations.Buildings import Age2BuildingData
from ...locations.Ages import Age2AgeData
from ...items.Items import Age2ItemData
from ...locations.UnitLines import Age2UnitLineData

from ..ScenarioLogic import ScenarioStartingState
from ..ScenarioPlayer import ScenarioPlayer


if TYPE_CHECKING:
    from ..Logic import Logic
    from ..ScenarioLogic import ScenarioLogic

class Attila4Player(ScenarioPlayer):
    BURGUNDY = 2, "Burgundy"
    METZ = 3, "Metz"
    ORLEANS = 4, "Orléans"
    WESTERN_ROMAN_EMPIRE = 5, "the Western Roman Empire"

class Attila4StartingState(ScenarioStartingState):

    def __init__(self, logic: 'Logic'):
        super().__init__()
        self.logic = logic
        self.is_unlocked = Has(Age2ScenarioLocationData.ATT3_VICTORY.scenario.scenario_name + ": Unlock Next Scenario") & Has("Progressive Attila Scenario", 3)
        # No water the logic counts on: no Dock, so no ships and no deep fish.
        self.has_water_access = False_()

    def defeat_rules(self, scenario_logic: 'ScenarioLogic') -> dict[ScenarioPlayer, Rule]:
        military = scenario_logic.military
        # The Roman army stands with Orléans, so it falls to the same army.
        can_defeat_orleans: Rule = (
            scenario_logic.has_base() &
            military.counters(Age2UnitLineData.KNIGHT_LINE, Age2AgeData.IMPERIAL) &
            military.counters(Age2UnitLineData.SPEARMAN_LINE, Age2AgeData.IMPERIAL) &
            military.counters(Age2UnitLineData.THROWING_AXEMAN_LINE, Age2AgeData.IMPERIAL) &
            military.counters(Age2UnitLineData.SCORPION_LINE, Age2AgeData.IMPERIAL) &
            military.counters(Age2UnitLineData.MONK_LINE, Age2AgeData.CASTLE) &
            military.counters(Age2UnitLineData.TREBUCHET_LINE, Age2AgeData.IMPERIAL) &
            military.has_long_range_siege() &
            scenario_logic.ages.can_reach(Age2AgeData.IMPERIAL)
        )
        return {
            Attila4Player.BURGUNDY: (
                scenario_logic.has_base() &
                military.counters(Age2UnitLineData.ARCHER_LINE, Age2AgeData.CASTLE) &
                military.counters(Age2UnitLineData.MILITIA_LINE, Age2AgeData.CASTLE) &
                military.counters(Age2UnitLineData.BATTERING_RAM_LINE, Age2AgeData.CASTLE)
            ),
            Attila4Player.METZ: (
                scenario_logic.has_base() &
                military.counters(Age2UnitLineData.MILITIA_LINE, Age2AgeData.IMPERIAL) &
                military.counters(Age2UnitLineData.KNIGHT_LINE, Age2AgeData.IMPERIAL) &
                military.counters(Age2UnitLineData.THROWING_AXEMAN_LINE, Age2AgeData.IMPERIAL) &
                military.counters(Age2UnitLineData.BATTERING_RAM_LINE, Age2AgeData.CASTLE) &
                military.has_siege() &
                scenario_logic.ages.can_reach(Age2AgeData.IMPERIAL)
            ),
            Attila4Player.ORLEANS: can_defeat_orleans,
            Attila4Player.WESTERN_ROMAN_EMPIRE: can_defeat_orleans,
        }
