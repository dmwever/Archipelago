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

class Attila5Player(ScenarioPlayer):
    """The Ostrogoths fight beside P1 and the Franks stay neutral, so neither has a member."""
    WESTERN_ROMAN_EMPIRE = 3, "the Western Roman Empire"
    VISIGOTHS = 4, "the Visigoths"
    ALANS = 5, "the Alans"

class Attila5StartingState(ScenarioStartingState):

    def __init__(self, logic: 'Logic'):
        super().__init__()
        self.logic = logic
        self.is_unlocked = Has(Age2ScenarioLocationData.ATT4_VICTORY.scenario.scenario_name + ": Unlock Next Scenario") & Has("Progressive Attila Scenario", 4)

    def defeat_rules(self, scenario_logic: 'ScenarioLogic') -> dict[ScenarioPlayer, Rule]:
        military = scenario_logic.military
        return {
            Attila5Player.ALANS: (
                scenario_logic.has_base() &
                military.counters(Age2UnitLineData.CAVALRY_ARCHER_LINE, Age2AgeData.IMPERIAL) &
                military.counters(Age2UnitLineData.KNIGHT_LINE, Age2AgeData.IMPERIAL) &
                military.counters(Age2UnitLineData.MANGONEL_LINE, Age2AgeData.IMPERIAL) &
                military.counters(Age2UnitLineData.TREBUCHET_LINE, Age2AgeData.IMPERIAL) &
                military.has_long_range_siege()
            ),
            Attila5Player.VISIGOTHS: (
                scenario_logic.has_base() &
                military.counters(Age2UnitLineData.SPEARMAN_LINE, Age2AgeData.IMPERIAL) &
                military.counters(Age2UnitLineData.MILITIA_LINE, Age2AgeData.IMPERIAL) &
                military.counters(Age2UnitLineData.HUSKARL_LINE, Age2AgeData.IMPERIAL) &
                military.counters(Age2UnitLineData.BATTERING_RAM_LINE, Age2AgeData.CASTLE) &
                military.counters(Age2UnitLineData.TREBUCHET_LINE, Age2AgeData.IMPERIAL) &
                military.has_long_range_siege()
            ),
            Attila5Player.WESTERN_ROMAN_EMPIRE: (
                scenario_logic.has_base() &
                military.counters(Age2UnitLineData.CENTURION_LINE, Age2AgeData.IMPERIAL) &
                military.counters(Age2UnitLineData.MILITIA_LINE, Age2AgeData.IMPERIAL) &
                military.counters(Age2UnitLineData.SCORPION_LINE, Age2AgeData.IMPERIAL) &
                military.counters(Age2UnitLineData.TREBUCHET_LINE, Age2AgeData.IMPERIAL) &
                military.has_long_range_siege()
            ),
        }
