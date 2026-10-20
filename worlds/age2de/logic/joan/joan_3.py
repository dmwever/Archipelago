from typing import TYPE_CHECKING

from rule_builder.rules import Has, Rule, True_
from ...locations.Locations import Age2ScenarioLocationData
from ...locations.Ages import Age2AgeData
from ...locations.UnitLines import Age2UnitLineData

from ...locations.Buildings import Age2BuildingData
from ...locations.Units import Age2UnitData as U
from ...items.Items import Age2ItemData
from ..ScenarioLogic import ScenarioStartingState
from ...locations.Players import Age2PlayerData


if TYPE_CHECKING:
    from ..Logic import Logic
    from ..ScenarioLogic import ScenarioLogic

class Joan3StartingState(ScenarioStartingState):
    has_boats: Rule = Has(Age2ItemData.AP_JOAN_3_TRANSPORT.item_name)

    def __init__(self, logic: 'Logic'):
        super().__init__()
        self.logic = logic
        self.is_unlocked = Has(Age2ScenarioLocationData.JOAN2_VICTORY.scenario.scenario_name + ": Unlock Next Scenario") & Has("Progressive Joan of Arc Scenario", 2)
        self.has_vils = True_()

        self.obtains_unit[U.TRANSPORT_SHIP] = self.has_boats
        self.obtains_unit[U.DEMOLITION_SHIP] = self.has_boats
        self.meets_additional_base_requirements = self.has_boats | (
            logic.buildings.has_building(Age2BuildingData.DOCK)
            & logic.units.has_unit_items(U.TRANSPORT_SHIP))

    def defeat_rules(self, scenario_logic: 'ScenarioLogic') -> dict[Age2PlayerData, Rule]:
        military = scenario_logic.military
        transport = U.TRANSPORT_SHIP
        can_cross_ocean: Rule = (
            self.has_boats |
            (
                scenario_logic.units.can_train_structurally(transport) &
                scenario_logic.economy.can_pay(transport.cost)
            )
        )
        can_cross_ocean = scenario_logic.named("can cross the sea", can_cross_ocean)
        return {
            Age2PlayerData.JOAN3_BURGUNDY: (
                scenario_logic.has_base() &
                can_cross_ocean &
                military.counters_building() &
                military.counters(Age2UnitLineData.MILITIA_LINE, Age2AgeData.CASTLE) &
                military.counters(Age2UnitLineData.SPEARMAN_LINE, Age2AgeData.CASTLE) &
                military.counters(Age2UnitLineData.MANGONEL_LINE, Age2AgeData.CASTLE)
            ),
            # Every castle on the map is English: taking a castle is defeating the English.
            Age2PlayerData.JOAN3_ENGLISH: (
                scenario_logic.has_base() &
                can_cross_ocean &
                military.has_siege() &
                military.counters(Age2UnitLineData.MILITIA_LINE, Age2AgeData.CASTLE) &
                military.counters(Age2UnitLineData.LONGBOWMAN_LINE, Age2AgeData.CASTLE) &
                military.counters(Age2UnitLineData.KNIGHT_LINE, Age2AgeData.CASTLE)
            ),
            Age2PlayerData.JOAN3_FASTOLF: (
                scenario_logic.has_base() &
                can_cross_ocean &
                military.counters_building() &
                military.counters(Age2UnitLineData.BATTERING_RAM_LINE, Age2AgeData.CASTLE) &
                military.counters(Age2UnitLineData.SCOUT_CAVALRY_LINE, Age2AgeData.FEUDAL) &
                military.counters(Age2UnitLineData.KNIGHT_LINE, Age2AgeData.CASTLE)
            ),
        }
