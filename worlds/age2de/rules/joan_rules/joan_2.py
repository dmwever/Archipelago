from rule_builder.rules import Has, HasAny, Rule
from ...Options import ScenarioBranching
from ...logic.joan.joan_2 import Joan2StartingState

from ...items.Items import Age2ItemData
from ...locations.Ages import Age2AgeData
from ...locations.Locations import Age2ScenarioLocationData
from ...logic.Logic import ScenarioLogic
from ...locations.Scenarios import Age2ScenarioData
from ..ScenarioRules import ScenarioRules


class Joan2Rules(ScenarioRules):
    def __init__(self, rules):
        super().__init__(rules, Age2ScenarioData.AP_JOAN_2)
        self.scenario_logic = ScenarioLogic(self.logic, Joan2StartingState(self.logic))
    
    def set_rules(self):
        super().set_rules()
        can_cross: Rule = HasAny(Age2ItemData.AP_JOAN_2_TRADE_CARTS.item_name, Age2ItemData.AP_JOAN_2_DOCK.item_name)
        can_beat_purple: Rule = can_cross & self.scenario_logic.has_tc() & self.logic.military.counters_building()
        can_beat_red: Rule = can_cross & self.scenario_logic.has_tc() & self.logic.has_siege()
        can_beat_orange: Rule = can_cross & self.scenario_logic.has_tc() & self.logic.has_siege()
        victory: Rule = (can_beat_red | can_beat_orange) & Has(Age2ItemData.AP_JOAN_2_TRADE_CARTS.item_name)
        
        if self.world.options.scenarioBranching == ScenarioBranching.option_all:
            self.world.set_rule(self.locations[Age2ScenarioLocationData.JOAN2_NORTHEAST_CASTLE], can_beat_red)
            self.world.set_rule(self.locations[Age2ScenarioLocationData.JOAN2_NORTHWEST_CASTLE], can_beat_red)
            self.world.set_rule(self.locations[Age2ScenarioLocationData.JOAN2_SOUTHWEST_CASTLE], can_beat_orange)
            self.world.set_rule(self.locations[Age2ScenarioLocationData.JOAN2_SOUTHEAST_CASTLE], can_beat_orange)
        else:
            self.world.set_rule(self.locations[Age2ScenarioLocationData.JOAN2_ANY_CASTLE], can_beat_red | can_beat_orange)
            
        self.world.set_rule(self.locations[Age2ScenarioLocationData.JOAN2_BRING_CARTS_TO_ORLEANS], Has(Age2ItemData.AP_JOAN_2_TRADE_CARTS.item_name))
        self.world.set_rule(self.locations[Age2ScenarioLocationData.JOAN2_CONQUER_BRIDGE], Has(Age2ItemData.AP_JOAN_2_TRADE_CARTS.item_name))
        self.world.set_rule(self.locations[Age2ScenarioLocationData.JOAN2_BRING_JOAN_TO_ORLEANS], can_cross)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.JOAN2_FIND_FARMING_VILLAGE], can_cross)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.JOAN2_VICTORY], victory)
        self.world.set_rule(self.world.get_location("Complete " + Age2ScenarioLocationData.JOAN2_VICTORY.scenario.scenario_name), victory)