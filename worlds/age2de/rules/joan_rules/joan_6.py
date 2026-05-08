from math import log

from ...locations.Ages import Age2AgeData

from ...items.Items import Age2ItemData

from rule_builder.rules import Has, HasAll

from ...locations.Locations import Age2ScenarioLocationData

from ...logic.joan.joan_6 import Joan6StartingState

from ...logic.Logic import ScenarioLogic
from ...locations.Scenarios import Age2ScenarioData
from ..ScenarioRules import ScenarioRules


class Joan6Rules(ScenarioRules):
    def __init__(self, rules):
        super().__init__(rules, Age2ScenarioData.AP_JOAN_6)
        self.scenario_logic = ScenarioLogic(self.logic, Joan6StartingState(self.logic))
    
    def set_rules(self):
        super().set_rules()
        
        can_defeat_purple = (
            self.scenario_logic.has_tc() &
            self.logic.military.has_siege() &
            self.logic.military.counters_militia(Age2AgeData.IMPERIAL) &
            self.logic.military.counters_spear(Age2AgeData.IMPERIAL) &
            self.logic.military.counters_monk()
        )
        
        can_siege_town = (
            HasAll(
                Age2ItemData.AP_JOAN_6_ARMY.item_name, 
                Age2ItemData.AP_JOAN_6_ARTILLERY.item_name
            ) |
            can_defeat_purple
        )
        can_defeat_orange = (
            self.scenario_logic.has_tc() &
            self.logic.military.has_siege() &
            self.logic.military.counters_knight(Age2AgeData.IMPERIAL) &
            self.logic.military.counters_scout(Age2AgeData.IMPERIAL) &
            self.logic.military.counters_ram() &
            self.logic.military.counters_trebuchet()
        )
        can_defeat_red = (
            self.scenario_logic.has_tc() &
            self.logic.military.has_siege() &
            self.logic.military.counters_longbowman(Age2AgeData.IMPERIAL) &
            self.logic.military.counters_knight(Age2AgeData.IMPERIAL) &
            self.logic.military.counters_mangonel(Age2AgeData.IMPERIAL) &
            self.logic.military.counters_trebuchet()
        )
        
        self.world.set_rule(self.locations[Age2ScenarioLocationData.JOAN6_BURGUNDIAN_TOWN], can_siege_town)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.JOAN6_VICTORY], can_siege_town & can_defeat_red)
        self.world.set_rule(self.world.get_location("Complete " + Age2ScenarioLocationData.JOAN6_VICTORY.scenario.scenario_name), can_siege_town & can_defeat_red)