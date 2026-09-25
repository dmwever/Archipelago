from rule_builder.rules import Rule
from ...logic.attila.attila_5 import Attila5StartingState
from ...locations.Ages import Age2AgeData
from ...locations.UnitLines import Age2UnitLineData

from ...locations.Locations import Age2ScenarioLocationData
from ...logic.ScenarioLogic import ScenarioLogic
from ...locations.Scenarios import Age2ScenarioData
from ..ScenarioRules import ScenarioRules


class Attila5Rules(ScenarioRules):
    def __init__(self, rules):
        super().__init__(rules, Age2ScenarioData.AP_ATTILA_5)
        self.scenario_logic = ScenarioLogic(self.logic, Attila5StartingState(self.logic), self.scenario)
    
    def set_rules(self):
        super().set_rules()
        can_beat_cyan: Rule = (
            self.scenario_logic.has_base() &
            self.scenario_logic.military.counters(Age2UnitLineData.CAVALRY_ARCHER_LINE, Age2AgeData.IMPERIAL) &
            self.scenario_logic.military.counters(Age2UnitLineData.KNIGHT_LINE, Age2AgeData.IMPERIAL) &
            self.scenario_logic.military.counters(Age2UnitLineData.MANGONEL_LINE, Age2AgeData.IMPERIAL) &
            self.scenario_logic.military.counters(Age2UnitLineData.TREBUCHET_LINE, Age2AgeData.IMPERIAL) &
            self.scenario_logic.military.has_long_range_siege()
        )
        can_beat_green: Rule = (
            self.scenario_logic.has_base() &
            self.scenario_logic.military.counters(Age2UnitLineData.SPEARMAN_LINE, Age2AgeData.IMPERIAL) &
            self.scenario_logic.military.counters(Age2UnitLineData.MILITIA_LINE, Age2AgeData.IMPERIAL) &
            self.scenario_logic.military.counters(Age2UnitLineData.HUSKARL_LINE, Age2AgeData.IMPERIAL) &
            self.scenario_logic.military.counters(Age2UnitLineData.BATTERING_RAM_LINE, Age2AgeData.CASTLE) &
            self.scenario_logic.military.counters(Age2UnitLineData.TREBUCHET_LINE, Age2AgeData.IMPERIAL) &
            self.scenario_logic.military.has_long_range_siege()
        )
        can_beat_blue: Rule = (
            self.scenario_logic.has_base() &
            self.scenario_logic.military.counters(Age2UnitLineData.CENTURION_LINE, Age2AgeData.IMPERIAL) &
            self.scenario_logic.military.counters(Age2UnitLineData.MILITIA_LINE, Age2AgeData.IMPERIAL) &
            self.scenario_logic.military.counters(Age2UnitLineData.SCORPION_LINE, Age2AgeData.IMPERIAL) &
            self.scenario_logic.military.counters(Age2UnitLineData.TREBUCHET_LINE, Age2AgeData.IMPERIAL) &
            self.scenario_logic.military.has_long_range_siege()
        )
        
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT5_DEFEAT_ALANS], can_beat_cyan)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT5_DEFEAT_VISIGOTHS], can_beat_green)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT5_DEFEAT_ROMANS], can_beat_blue)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT5_VICTORY], can_beat_blue & can_beat_cyan & can_beat_green)
        self.world.set_rule(self.world.get_location("Complete " + Age2ScenarioLocationData.ATT5_VICTORY.scenario.scenario_name), can_beat_blue & can_beat_cyan & can_beat_green)