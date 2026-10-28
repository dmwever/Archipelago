from typing import TYPE_CHECKING

from rule_builder.rules import Has, Rule
from ...locations.Locations import Age2ScenarioLocationData
from ...locations.Buildings import Age2BuildingData
from ...locations.Ages import Age2AgeData
from ...items.Items import Resource
from ...locations.UnitLines import Age2UnitLineData

from ..ScenarioLogic import ScenarioStartingState
from ...locations.Players import Age2PlayerData


if TYPE_CHECKING:
    from ..Logic import Logic
    from ..ScenarioLogic import ScenarioLogic

class Attila4StartingState(ScenarioStartingState):

    def __init__(self, logic: 'Logic'):
        super().__init__()
        self.logic = logic
        self.is_unlocked = Has(Age2ScenarioLocationData.ATT3_VICTORY.scenario.scenario_name + ": Unlock Next Scenario") & Has("Progressive Attila Scenario", 3)
    def can_tribute_burgundy(self, scenario_logic: 'ScenarioLogic') -> Rule:
        return (scenario_logic.has_building(Age2BuildingData.MARKET) &
                scenario_logic.economy.has_easy_source(Resource.GOLD))

    def can_ally_burgundy(self, scenario_logic: 'ScenarioLogic') -> Rule:
        can_ally: Rule = (
            self.can_tribute_burgundy(scenario_logic) &
            scenario_logic.has_building(Age2BuildingData.CASTLE) &
            scenario_logic.ages.can_reach(Age2AgeData.CASTLE)
        )
        return scenario_logic.named("can ally with Burgundy", can_ally)

    def defeat_rules(self, scenario_logic: 'ScenarioLogic') -> dict[Age2PlayerData, Rule]:
        military = scenario_logic.military
        # The Roman army stands with Orléans, so it falls to the same army.
        can_defeat_orleans: Rule = (
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
            Age2PlayerData.ATT4_BURGUNDY: (
                military.counters(Age2UnitLineData.ARCHER_LINE, Age2AgeData.CASTLE) &
                military.counters(Age2UnitLineData.MILITIA_LINE, Age2AgeData.CASTLE) &
                military.counters(Age2UnitLineData.BATTERING_RAM_LINE, Age2AgeData.CASTLE)
            ),
            Age2PlayerData.ATT4_METZ: (
                military.counters(Age2UnitLineData.MILITIA_LINE, Age2AgeData.IMPERIAL) &
                military.counters(Age2UnitLineData.KNIGHT_LINE, Age2AgeData.IMPERIAL) &
                military.counters(Age2UnitLineData.THROWING_AXEMAN_LINE, Age2AgeData.IMPERIAL) &
                military.counters(Age2UnitLineData.BATTERING_RAM_LINE, Age2AgeData.CASTLE) &
                military.has_siege() &
                scenario_logic.ages.can_reach(Age2AgeData.IMPERIAL)
            ),
            Age2PlayerData.ATT4_ORLEANS: can_defeat_orleans,
            Age2PlayerData.ATT4_WESTERN_ROMAN_EMPIRE: can_defeat_orleans,
        }

    def trade_guard_rules(
        self,
        scenario_logic: 'ScenarioLogic',
    ) -> dict[tuple[Age2PlayerData, Age2BuildingData], Rule]:
        return {
            (Age2PlayerData.ATT4_BURGUNDY, Age2BuildingData.MARKET): (
                self.can_ally_burgundy(scenario_logic)
            ),
        }
