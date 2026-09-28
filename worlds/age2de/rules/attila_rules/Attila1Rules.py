from rule_builder.rules import Has, Rule

from ...items.Items import Age2ItemData
from ...locations.Ages import Age2AgeData
from ...locations.UnitLines import Age2UnitLineData
from ...locations.Locations import Age2ScenarioLocationData
from ...logic.attila.attila_1 import Attila1StartingState
from ...logic.ScenarioLogic import ScenarioLogic
from ...locations.Scenarios import Age2ScenarioData
from ..ScenarioRules import ScenarioRules


class Attila1Rules(ScenarioRules):
    def __init__(self, rules):
        super().__init__(rules, Age2ScenarioData.AP_ATTILA_1)
        self.scenario_logic = ScenarioLogic(self.logic, Attila1StartingState(self.logic), self.scenario)
    
    def set_rules(self):
        super().set_rules()
        
        can_beat_purple: Rule = (
            self.scenario_logic.has_base() &
            self.scenario_logic.military.has_military()
        )
        
        can_beat_blue: Rule = (
            self.scenario_logic.ages.can_reach(Age2AgeData.FEUDAL) &
            self.scenario_logic.has_base() &
            self.scenario_logic.military.has_military()
        )
        
        can_beat_red: Rule = (
            self.scenario_logic.ages.can_reach(Age2AgeData.CASTLE) &
            self.scenario_logic.has_base() &
            self.scenario_logic.military.has_siege() &
            self.scenario_logic.military.counters(Age2UnitLineData.KNIGHT_LINE, Age2AgeData.CASTLE) &
            self.scenario_logic.military.counters(Age2UnitLineData.MANGONEL_LINE, Age2AgeData.CASTLE) &
            self.scenario_logic.military.counters(Age2UnitLineData.WAR_ELEPHANT_LINE, Age2AgeData.CASTLE)
        )
        
        can_beat_green: Rule = (
            self.scenario_logic.ages.can_reach(Age2AgeData.CASTLE) &
            self.scenario_logic.has_base() &
            self.scenario_logic.military.has_siege() &
            self.scenario_logic.military.counters(Age2UnitLineData.CAVALRY_ARCHER_LINE, Age2AgeData.CASTLE) &
            self.scenario_logic.military.counters(Age2UnitLineData.MANGUDAI_LINE, Age2AgeData.CASTLE)
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