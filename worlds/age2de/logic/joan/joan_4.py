from typing import TYPE_CHECKING

from rule_builder.rules import False_, Has, HasAny, Rule, True_
from ...locations.Locations import Age2ScenarioLocationData
from ...locations.Buildings import Age2BuildingData
from ...locations.Ages import Age2AgeData
from ...items.Items import Age2ItemData
from ...locations.UnitLines import Age2UnitLineData

from ...locations.Units import Age2UnitData as U
from ..ScenarioLogic import ScenarioStartingState
from ..ScenarioPlayer import ScenarioPlayer


if TYPE_CHECKING:
    from ..Logic import Logic
    from ..ScenarioLogic import ScenarioLogic

class Joan4Player(ScenarioPlayer):
    TROYES = 2, "Troyes"
    CHALONS = 3, "Chalons"
    RHEIMS = 4, "Rheims"

class Joan4StartingState(ScenarioStartingState):

    def __init__(self, logic: 'Logic'):
        super().__init__()
        self.logic = logic
        self.is_unlocked = Has(Age2ScenarioLocationData.JOAN3_VICTORY.scenario.scenario_name + ": Unlock Next Scenario") & Has("Progressive Joan of Arc Scenario", 3)
        self.has_vils = Has(Age2ItemData.AP_JOAN_4_FRENCH_CAMP.item_name)

        camp = Has(Age2ItemData.AP_JOAN_4_FRENCH_CAMP.item_name)
        self.obtains_unit[U.CROSSBOWMAN] = camp
        self.obtains_unit[U.VILLAGER_MALE] = camp
        self.obtains_unit[U.VILLAGER_FEMALE] = camp

    def defeat_rules(self, scenario_logic: 'ScenarioLogic') -> dict[ScenarioPlayer, Rule]:
        military = scenario_logic.military
        # The Rising withholds the Cannon Galleon, and the Franks have no other ship that shoots
        # buildings: Chalons and Troyes fall to a land army only.
        return {
            Joan4Player.TROYES: (
                scenario_logic.has_base() &
                military.has_siege() &
                military.counters(Age2UnitLineData.KNIGHT_LINE, Age2AgeData.CASTLE) &
                military.counters(Age2UnitLineData.SPEARMAN_LINE, Age2AgeData.CASTLE)
            ),
            Joan4Player.CHALONS: (
                scenario_logic.has_base() &
                military.counters_building() &
                military.counters(Age2UnitLineData.BATTERING_RAM_LINE, Age2AgeData.CASTLE) &
                military.counters(Age2UnitLineData.SCORPION_LINE, Age2AgeData.IMPERIAL) &
                military.counters(Age2UnitLineData.KNIGHT_LINE, Age2AgeData.IMPERIAL)
            ),
            Joan4Player.RHEIMS: (
                scenario_logic.has_base() &
                military.has_siege() &
                military.counters(Age2UnitLineData.LONGBOWMAN_LINE, Age2AgeData.IMPERIAL) &
                military.counters(Age2UnitLineData.KNIGHT_LINE, Age2AgeData.IMPERIAL) &
                military.counters(Age2UnitLineData.MANGONEL_LINE, Age2AgeData.IMPERIAL) &
                military.counters(Age2UnitLineData.TREBUCHET_LINE, Age2AgeData.IMPERIAL)
            ),
        }
