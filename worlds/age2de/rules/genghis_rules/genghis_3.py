from rule_builder.rules import Has, Rule

from ...items.Items import Age2ItemData
from ...locations.Ages import Age2AgeData
from ...locations.Locations import Age2ScenarioLocationData
from ...locations.Scenarios import Age2ScenarioData
from ...locations.UnitLines import Age2UnitLineData
from ..ScenarioRules import ScenarioRules


class Genghis3Rules(ScenarioRules):
    """Four enemies worth fighting and a fifth that gives up on its own: the Engineers resign
    the moment the Tanguts, Xi Xia, Jin and Song are all gone, so victory is owed four defeats
    rather than five. Counters follow what each script trains, never what it merely starts with.
    """

    def __init__(self, rules):
        super().__init__(rules, Age2ScenarioData.AP_GENGHIS_3)

    def set_rules(self):
        super().set_rules()
        military = self.scenario_logic.military
        units = self.scenario_logic.units

        transport: Rule = Has(Age2ItemData.AP_GENGHIS_3_TRANSPORT.item_name)
        bombards: Rule = Has(Age2ItemData.AP_GENGHIS_3_BOMBARDS.item_name)
        has_siege: Rule = military.has_siege() | bombards
        has_long_siege: Rule = military.has_long_range_siege() | bombards

        self.world.set_rule(self.locations[Age2ScenarioLocationData.GEN3_FIND_ENGINEERS], transport)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.GEN3_FIND_BOMBARDS], transport)
        
        can_invade_china: Rule = (
            units.can_field(Age2UnitLineData.TRANSPORT_SHIP_LINE, Age2AgeData.FEUDAL) |
            has_siege
        )

        can_force_landing: Rule = (
            units.can_field(Age2UnitLineData.TRANSPORT_SHIP_LINE, Age2AgeData.FEUDAL) &
            military.has_navy(Age2AgeData.FEUDAL)
        )

        can_kill_tanguts: Rule = (
            self.scenario_logic.has_base() &
            can_invade_china &
            military.has_military(Age2AgeData.CASTLE) &
            military.counters(Age2UnitLineData.BATTERING_RAM_LINE, Age2AgeData.CASTLE) &
            military.counters(Age2UnitLineData.ROCKET_CART_LINE, Age2AgeData.CASTLE) &
            military.counters(Age2UnitLineData.ARCHER_LINE, Age2AgeData.CASTLE) &
            military.counters(Age2UnitLineData.FIRE_LANCER_LINE, Age2AgeData.CASTLE) &
            military.counters(Age2UnitLineData.MOUNTED_TREBUCHET_LINE, Age2AgeData.CASTLE) &
            military.counters(Age2UnitLineData.MONK_LINE, Age2AgeData.CASTLE) &
            military.counters_building() &
            self.scenario_logic.ages.can_reach(Age2AgeData.CASTLE)
        )

        can_kill_xi_xia: Rule = (
            self.scenario_logic.has_base() &
            can_invade_china &
            military.has_military(Age2AgeData.CASTLE) &
            military.counters(Age2UnitLineData.CHU_KO_NU_LINE, Age2AgeData.CASTLE) &
            military.counters(Age2UnitLineData.SCORPION_LINE, Age2AgeData.CASTLE) &
            military.counters(Age2UnitLineData.TREBUCHET_LINE, Age2AgeData.CASTLE) &
            military.counters(Age2UnitLineData.SCOUT_CAVALRY_LINE, Age2AgeData.CASTLE) &
            has_siege &
            self.scenario_logic.ages.can_reach(Age2AgeData.CASTLE)
        )

        can_kill_jin: Rule = (
            self.scenario_logic.has_base() &
            can_force_landing &
            military.has_military(Age2AgeData.IMPERIAL) &
            military.counters(Age2UnitLineData.IRON_PAGODA_LINE, Age2AgeData.IMPERIAL) &
            military.counters(Age2UnitLineData.GRENADIER_LINE, Age2AgeData.IMPERIAL) &
            military.counters(Age2UnitLineData.STEPPE_LANCER_LINE, Age2AgeData.IMPERIAL) &
            military.counters(Age2UnitLineData.ROCKET_CART_LINE, Age2AgeData.IMPERIAL) &
            military.counters(Age2UnitLineData.MONK_LINE, Age2AgeData.IMPERIAL) &
            military.counters(Age2UnitLineData.GALLEY_LINE, Age2AgeData.IMPERIAL) &
            has_long_siege &
            self.scenario_logic.ages.can_reach(Age2AgeData.IMPERIAL)
        )

        can_kill_song: Rule = (
            self.scenario_logic.has_base() &
            can_invade_china &
            military.has_military(Age2AgeData.CASTLE) &
            military.counters(Age2UnitLineData.ARCHER_LINE, Age2AgeData.CASTLE) &
            military.counters(Age2UnitLineData.SKIRMISHER_LINE, Age2AgeData.CASTLE) &
            military.counters(Age2UnitLineData.MILITIA_LINE, Age2AgeData.CASTLE) &
            military.counters(Age2UnitLineData.ROCKET_CART_LINE, Age2AgeData.CASTLE) &
            military.counters(Age2UnitLineData.FIRE_LANCER_LINE, Age2AgeData.CASTLE) &
            military.counters(Age2UnitLineData.MONK_LINE, Age2AgeData.CASTLE) &
            military.counters_building() &
            self.scenario_logic.ages.can_reach(Age2AgeData.CASTLE)
        )

        self.world.set_rule(self.locations[Age2ScenarioLocationData.GEN3_DEFEAT_TANGUTS], can_kill_tanguts)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.GEN3_DEFEAT_XI_XIA], can_kill_xi_xia)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.GEN3_DEFEAT_JIN], can_kill_jin)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.GEN3_DEFEAT_SONG], can_kill_song)

        can_beat_scenario: Rule = can_kill_tanguts & can_kill_xi_xia & can_kill_jin & can_kill_song
        self.world.set_rule(self.locations[Age2ScenarioLocationData.GEN3_VICTORY], can_beat_scenario)
        self.world.set_rule(self.world.get_location("Complete " + Age2ScenarioLocationData.GEN3_VICTORY.scenario.scenario_name), can_beat_scenario)
