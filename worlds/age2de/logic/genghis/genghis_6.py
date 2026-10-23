from typing import TYPE_CHECKING

from rule_builder.rules import False_, Has, Rule, True_
from ...locations.Buildings import Age2BuildingData
from ...locations.Locations import Age2ScenarioLocationData
from ...items.Items import Age2ItemData
from ...locations.Ages import Age2AgeData
from ...locations.UnitLines import Age2UnitLineData

from ..ScenarioLogic import ScenarioStartingState
from ...locations.Players import Age2PlayerData

if TYPE_CHECKING:
    from ..Logic import Logic
    from ..ScenarioLogic import ScenarioLogic

class Genghis6StartingState(ScenarioStartingState):

    def __init__(self, logic: 'Logic'):
        super().__init__()
        self.logic = logic
        self.is_unlocked = Has(Age2ScenarioLocationData.GEN5_VICTORY.scenario.scenario_name + ": Unlock Next Scenario") & Has("Progressive Genghis Khan Scenario", 5)

        # Ogedei holds the north bank in imperial already: a town centre, a castle, a stable
        # and an archery range behind seven guard towers.
        self.starts_with_building[Age2BuildingData.TOWN_CENTER] = True_()
        self.starts_with_building[Age2BuildingData.CASTLE] = True_()
        self.starts_with_building[Age2BuildingData.STABLE] = True_()
        self.starts_with_building[Age2BuildingData.ARCHERY_RANGE] = True_()

    def defeat_rules(self, scenario_logic: 'ScenarioLogic') -> dict[Age2PlayerData, Rule]:
        military = scenario_logic.military
        return {
            Age2PlayerData.GEN6_HUNGARY: (
                military.has_military(Age2AgeData.IMPERIAL) &
                military.counters(Age2UnitLineData.KNIGHT_LINE, Age2AgeData.IMPERIAL) &
                military.counters(Age2UnitLineData.SKIRMISHER_LINE, Age2AgeData.IMPERIAL) &
                military.counters(Age2UnitLineData.MAGYAR_HUSZAR_LINE, Age2AgeData.IMPERIAL) &
                military.counters(Age2UnitLineData.SCOUT_CAVALRY_LINE, Age2AgeData.IMPERIAL) &
                military.counters(Age2UnitLineData.SCORPION_LINE, Age2AgeData.IMPERIAL) &
                military.counters(Age2UnitLineData.BATTERING_RAM_LINE, Age2AgeData.IMPERIAL) &
                military.counters(Age2UnitLineData.TREBUCHET_LINE, Age2AgeData.IMPERIAL) &
                military.counters(Age2UnitLineData.MONK_LINE, Age2AgeData.IMPERIAL) &
                military.has_siege() &
                scenario_logic.ages.can_reach(Age2AgeData.IMPERIAL)
            ),
        }
