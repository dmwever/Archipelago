from rule_builder.rules import Has, HasAny, Rule

from ...items.Items import Age2ItemData
from ...locations.Ages import Age2AgeData
from ...locations.Locations import Age2ScenarioLocationData
from ...locations.Scenarios import Age2ScenarioData
from ...locations.UnitLines import Age2UnitLineData
from ..ScenarioRules import ScenarioRules


class Joan2Rules(ScenarioRules):
    def __init__(self, rules):
        super().__init__(rules, Age2ScenarioData.AP_JOAN_2)
    
    def set_rules(self):
        super().set_rules()
        can_cross: Rule = HasAny(Age2ItemData.AP_JOAN_2_TRADE_CARTS.item_name, Age2ItemData.AP_JOAN_2_DOCK.item_name)
        can_conquer_bridge: Rule = (Has(Age2ItemData.AP_JOAN_2_TRADE_CARTS.item_name)
                                    | self.scenario_logic.military.has_military())
        can_beat_purple: Rule = self.scenario_logic.has_base() & self.scenario_logic.military.counters_building()
        can_beat_red: Rule = (
            self.scenario_logic.has_base() &
            self.scenario_logic.military.has_siege() &
            self.scenario_logic.military.counters(Age2UnitLineData.LONGBOWMAN_LINE, Age2AgeData.CASTLE) &
            self.scenario_logic.military.counters(Age2UnitLineData.MILITIA_LINE, Age2AgeData.CASTLE)
        )
        can_beat_orange: Rule = (
            self.scenario_logic.has_base() &
            self.scenario_logic.military.has_siege() &
            self.scenario_logic.military.counters(Age2UnitLineData.KNIGHT_LINE, Age2AgeData.CASTLE) &
            self.scenario_logic.military.counters(Age2UnitLineData.BATTERING_RAM_LINE, Age2AgeData.CASTLE)
        )
        victory: Rule = can_beat_red & can_beat_orange

        if self.world.pool.scenarios.all_scenario_branches:
            self.world.set_rule(self.locations[Age2ScenarioLocationData.JOAN2_NORTHEAST_CASTLE], can_beat_red)
            self.world.set_rule(self.locations[Age2ScenarioLocationData.JOAN2_NORTHWEST_CASTLE], can_beat_red)
            self.world.set_rule(self.locations[Age2ScenarioLocationData.JOAN2_SOUTHWEST_CASTLE], can_beat_orange)
            self.world.set_rule(self.locations[Age2ScenarioLocationData.JOAN2_SOUTHEAST_CASTLE], can_beat_orange)
            
        self.world.set_rule(self.locations[Age2ScenarioLocationData.JOAN2_BRING_CARTS_TO_ORLEANS], Has(Age2ItemData.AP_JOAN_2_TRADE_CARTS.item_name))
        self.world.set_rule(self.locations[Age2ScenarioLocationData.JOAN2_CONQUER_BRIDGE], can_conquer_bridge)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.JOAN2_BRING_JOAN_TO_ORLEANS], can_cross)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.JOAN2_FIND_FARMING_VILLAGE], can_cross)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.JOAN2_VICTORY], victory)
        self.world.set_rule(self.world.get_location("Complete " + Age2ScenarioLocationData.JOAN2_VICTORY.scenario.scenario_name), victory)