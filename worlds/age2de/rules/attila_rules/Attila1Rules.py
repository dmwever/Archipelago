from rule_builder.rules import Has, Rule

from ...items.Items import Age2ItemData
from ...locations.Ages import Age2AgeData
from ...locations.Locations import Age2ScenarioLocationData
from ...logic.attila.Attila1StartingState import Attila1StartingState
from ...logic.Logic import ScenarioLogic
from ...locations.Scenarios import Age2ScenarioData
from ..ScenarioRules import ScenarioRules


class Attila1Rules(ScenarioRules):
    def __init__(self, rules):
        super().__init__(rules, Age2ScenarioData.AP_ATTILA_1)
        self.scenario_logic = ScenarioLogic(self.logic, Attila1StartingState(self.logic))
    
    def set_rules(self):
        super().set_rules()
        
        can_beat_purple: Rule = (
            self.scenario_logic.has_tc() &
            self.logic.has_military()
        )
        
        can_beat_blue: Rule = (
            self.scenario_logic.can_reach_age(Age2AgeData.FEUDAL) &
            self.scenario_logic.has_tc() &
            self.logic.has_military()
        )
        
        can_beat_red: Rule = (
            self.scenario_logic.can_reach_age(Age2AgeData.CASTLE) &
            self.scenario_logic.has_tc() &
            self.logic.buildings.has_siege() &
            self.logic.military.counters_knight() &
            self.logic.military.counters_mangonel() &
            self.logic.military.counters_war_elephant()
        )
        
        can_beat_green: Rule = (
            self.scenario_logic.can_reach_age(Age2AgeData.CASTLE) &
            self.scenario_logic.has_tc() &
            self.logic.buildings.has_siege() &
            self.logic.military.counters_cav_archer() &
            self.logic.military.counters_mangudai()
        )
        
        self.world.set_rule(
            self.locations[Age2ScenarioLocationData.ATT1_VICTORY],
            can_beat_blue & (can_beat_green | can_beat_red)
        )
        self.world.set_rule(
            self.locations[Age2ScenarioLocationData.ATT1_DEFEAT_FIRST_PLAYER],
            can_beat_blue
        )
        self.world.set_rule(
            self.locations[Age2ScenarioLocationData.ATT1_CAPTURE_HORSES_CAMP],
            Has(Age2ItemData.AP_ATTILA_1_BLEDAS_CAMP.item_name)
        )
        
        self.world.set_rule(self.world.get_location("Complete " + Age2ScenarioLocationData.ATT1_VICTORY.scenario.scenario_name), 
            can_beat_blue & (can_beat_green | can_beat_red))