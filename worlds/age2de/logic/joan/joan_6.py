from typing import TYPE_CHECKING

from rule_builder.rules import False_, Has, HasAny, Rule, True_
from ...locations.Locations import Age2ScenarioLocationData
from ...locations.Buildings import Age2BuildingData
from ...locations.Ages import Age2AgeData
from ...items.Items import Age2ItemData
from ...locations.UnitLines import Age2UnitLineData

from ...locations.Units import Age2UnitData as U
from ...locations.Heroes import Age2HeroData as H
from ..ScenarioLogic import ScenarioStartingState
from ...locations.Players import Age2PlayerData


if TYPE_CHECKING:
    from ..Logic import Logic
    from ..ScenarioLogic import ScenarioLogic

class Joan6StartingState(ScenarioStartingState):

    def __init__(self, logic: 'Logic'):
        super().__init__()
        self.logic = logic
        self.is_unlocked = Has(Age2ScenarioLocationData.JOAN5_VICTORY.scenario.scenario_name + ": Unlock Next Scenario") & Has("Progressive Joan of Arc Scenario", 5)
        self.has_vils = Has(Age2ItemData.AP_JOAN_6_ARMY.item_name)

        army = Has(Age2ItemData.AP_JOAN_6_ARMY.item_name)
        self.must_steal_base = army   # the French army is how you take the English camp
        self.obtains_unit[U.ARCHER] = army
        self.obtains_unit[U.MILITIA] = army
        self.obtains_unit[U.SCOUT_CAVALRY] = army
        self.obtains_unit[U.KNIGHT] = army
        self.obtains_unit[U.TREBUCHET_PACKED] = army
        self.obtains_unit[U.VILLAGER_MALE] = army
        self.obtains_unit[U.VILLAGER_FEMALE] = army
        self.obtains_unit[H.LA_HIRE] = army
        self.obtains_unit[H.CONSTABLE_RICHEMONT] = army

    def defeat_rules(self, scenario_logic: 'ScenarioLogic') -> dict[Age2PlayerData, Rule]:
        military = scenario_logic.military
        return {
            Age2PlayerData.JOAN6_BURGUNDY: (
                scenario_logic.has_base() &
                military.has_siege() &
                military.counters(Age2UnitLineData.MILITIA_LINE, Age2AgeData.IMPERIAL) &
                military.counters(Age2UnitLineData.SPEARMAN_LINE, Age2AgeData.IMPERIAL) &
                military.counters(Age2UnitLineData.MONK_LINE, Age2AgeData.CASTLE)
            ),
            Age2PlayerData.JOAN6_ENGLISH: (
                scenario_logic.has_base() &
                military.has_siege() &
                military.counters(Age2UnitLineData.LONGBOWMAN_LINE, Age2AgeData.IMPERIAL) &
                military.counters(Age2UnitLineData.KNIGHT_LINE, Age2AgeData.IMPERIAL) &
                military.counters(Age2UnitLineData.MANGONEL_LINE, Age2AgeData.IMPERIAL) &
                military.counters(Age2UnitLineData.TREBUCHET_LINE, Age2AgeData.IMPERIAL)
            ),
            Age2PlayerData.JOAN6_SHREWSBURY: (
                scenario_logic.has_base() &
                military.has_siege() &
                military.counters(Age2UnitLineData.KNIGHT_LINE, Age2AgeData.IMPERIAL) &
                military.counters(Age2UnitLineData.SCOUT_CAVALRY_LINE, Age2AgeData.IMPERIAL) &
                military.counters(Age2UnitLineData.BATTERING_RAM_LINE, Age2AgeData.CASTLE) &
                military.counters(Age2UnitLineData.TREBUCHET_LINE, Age2AgeData.IMPERIAL)
            ),
        }
