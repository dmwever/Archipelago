from typing import TYPE_CHECKING

from rule_builder.rules import Has, Rule
from ...locations.Buildings import Age2BuildingData
from ...locations.Locations import Age2ScenarioLocationData
from ...locations.Units import Age2UnitData
from ...items.Items import Age2ItemData
from ...locations.Ages import Age2AgeData
from ...locations.UnitLines import Age2UnitLineData

from ..ScenarioLogic import ScenarioStartingState
from ...locations.Players import Age2PlayerData

if TYPE_CHECKING:
    from ..Logic import Logic
    from ..ScenarioLogic import ScenarioLogic

class Genghis3StartingState(ScenarioStartingState):
    transport: Rule = Has(Age2ItemData.AP_GENGHIS_3_TRANSPORT.item_name)
    engineers: Rule = Has(Age2ItemData.AP_GENGHIS_3_ENGINEERS.item_name)
    bombards: Rule = Has(Age2ItemData.AP_GENGHIS_3_BOMBARDS.item_name)

    def __init__(self, logic: 'Logic'):
        super().__init__()
        self.logic = logic
        self.is_unlocked = Has(Age2ScenarioLocationData.GEN2_VICTORY.scenario.scenario_name + ": Unlock Next Scenario") & Has("Progressive Genghis Khan Scenario", 2)

        self.restorable_transport = self.transport & logic.units.survives_caveman(
            Age2UnitData.TRANSPORT_SHIP)
        self.restorable_bombards = self.bombards & logic.units.survives_caveman(
            Age2UnitData.BOMBARD_CANNON)

        self.has_vils = self.engineers & self.restorable_transport
        self.obtains_unit[Age2UnitData.TRANSPORT_SHIP] = self.transport

        self.starts_with_building[Age2BuildingData.SIEGE_WORKSHOP] = (
            self.bombards | self.engineers)

    def defeat_rules(self, scenario_logic: 'ScenarioLogic') -> dict[Age2PlayerData, Rule]:
        military = scenario_logic.military
        units = scenario_logic.units

        has_siege: Rule = military.has_siege() | self.restorable_bombards
        has_siege = scenario_logic.named("has siege or the bombards", has_siege)
        has_long_siege: Rule = military.has_long_range_siege() | self.restorable_bombards
        has_long_siege = scenario_logic.named(
            "has long-range siege or the bombards",
            has_long_siege,
        )

        can_invade_china: Rule = (
            units.can_field(Age2UnitLineData.TRANSPORT_SHIP_LINE, Age2AgeData.FEUDAL) |
            has_siege
        )
        can_invade_china = scenario_logic.named("can invade China", can_invade_china)

        can_force_landing: Rule = (
            units.can_field(Age2UnitLineData.TRANSPORT_SHIP_LINE, Age2AgeData.FEUDAL) &
            military.has_navy(Age2AgeData.FEUDAL)
        )
        can_force_landing = scenario_logic.named("can force a landing", can_force_landing)

        can_defeat_tanguts: Rule = (
            can_invade_china &
            military.has_military(Age2AgeData.CASTLE) &
            military.counters(Age2UnitLineData.BATTERING_RAM_LINE, Age2AgeData.CASTLE) &
            military.counters(Age2UnitLineData.ROCKET_CART_LINE, Age2AgeData.CASTLE) &
            military.counters(Age2UnitLineData.ARCHER_LINE, Age2AgeData.CASTLE) &
            military.counters(Age2UnitLineData.FIRE_LANCER_LINE, Age2AgeData.CASTLE) &
            military.counters(Age2UnitLineData.MOUNTED_TREBUCHET_LINE, Age2AgeData.CASTLE) &
            military.counters(Age2UnitLineData.MONK_LINE, Age2AgeData.CASTLE) &
            military.counters_building() &
            scenario_logic.ages.can_reach(Age2AgeData.CASTLE)
        )
        can_defeat_xi_xia: Rule = (
            can_invade_china &
            military.has_military(Age2AgeData.CASTLE) &
            military.counters(Age2UnitLineData.CHU_KO_NU_LINE, Age2AgeData.CASTLE) &
            military.counters(Age2UnitLineData.SCORPION_LINE, Age2AgeData.CASTLE) &
            military.counters(Age2UnitLineData.TREBUCHET_LINE, Age2AgeData.CASTLE) &
            military.counters(Age2UnitLineData.SCOUT_CAVALRY_LINE, Age2AgeData.CASTLE) &
            has_siege &
            scenario_logic.ages.can_reach(Age2AgeData.CASTLE)
        )

        return {
            Age2PlayerData.GEN3_TANGUTS: can_defeat_tanguts,
            Age2PlayerData.GEN3_XI_XIA: can_defeat_xi_xia,
            Age2PlayerData.GEN3_JIN: (
                can_force_landing &
                military.has_military(Age2AgeData.IMPERIAL) &
                military.counters(Age2UnitLineData.IRON_PAGODA_LINE, Age2AgeData.IMPERIAL) &
                military.counters(Age2UnitLineData.GRENADIER_LINE, Age2AgeData.IMPERIAL) &
                military.counters(Age2UnitLineData.STEPPE_LANCER_LINE, Age2AgeData.IMPERIAL) &
                military.counters(Age2UnitLineData.ROCKET_CART_LINE, Age2AgeData.IMPERIAL) &
                military.counters(Age2UnitLineData.MONK_LINE, Age2AgeData.IMPERIAL) &
                military.counters(Age2UnitLineData.GALLEY_LINE, Age2AgeData.IMPERIAL) &
                has_long_siege &
                scenario_logic.ages.can_reach(Age2AgeData.IMPERIAL)
            ),
            Age2PlayerData.GEN3_SONG: (
                can_invade_china &
                military.has_military(Age2AgeData.CASTLE) &
                military.counters(Age2UnitLineData.ARCHER_LINE, Age2AgeData.CASTLE) &
                military.counters(Age2UnitLineData.SKIRMISHER_LINE, Age2AgeData.CASTLE) &
                military.counters(Age2UnitLineData.MILITIA_LINE, Age2AgeData.CASTLE) &
                military.counters(Age2UnitLineData.ROCKET_CART_LINE, Age2AgeData.CASTLE) &
                military.counters(Age2UnitLineData.FIRE_LANCER_LINE, Age2AgeData.CASTLE) &
                military.counters(Age2UnitLineData.MONK_LINE, Age2AgeData.CASTLE) &
                military.counters_building() &
                scenario_logic.ages.can_reach(Age2AgeData.CASTLE) &
                (can_defeat_tanguts | can_defeat_xi_xia)
            ),
        }
