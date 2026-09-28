
from ...locations.Locations import Age2ScenarioLocationData

from ...locations.Ages import Age2AgeData
from ...locations.UnitLines import Age2UnitLineData

from rule_builder.rules import Rule

from ...logic.joan.joan_4 import Joan4StartingState

from ...logic.ScenarioLogic import ScenarioLogic
from ...locations.Scenarios import Age2ScenarioData
from ..ScenarioRules import ScenarioRules


class Joan4Rules(ScenarioRules):
    def __init__(self, rules):
        super().__init__(rules, Age2ScenarioData.AP_JOAN_4)
        self.scenario_logic = ScenarioLogic(self.logic, Joan4StartingState(self.logic), self.scenario)
    
    def set_rules(self):
        super().set_rules()
        can_beat_green: Rule = (
            (
                self.scenario_logic.has_base() &
                self.scenario_logic.military.counters_building() &
                self.scenario_logic.military.has_navy(Age2AgeData.IMPERIAL) &
                self.scenario_logic.military.counters(Age2UnitLineData.BATTERING_RAM_LINE, Age2AgeData.CASTLE) &
                self.scenario_logic.military.counters(Age2UnitLineData.SCORPION_LINE, Age2AgeData.IMPERIAL) &
                self.scenario_logic.military.counters(Age2UnitLineData.KNIGHT_LINE, Age2AgeData.IMPERIAL)
            ) |
            (
                self.scenario_logic.has_base() &
                self.scenario_logic.military.has_navy(Age2AgeData.IMPERIAL) &
                self.scenario_logic.military.has_naval_bombardment()
            )
        )
        can_beat_orange: Rule = (
            (
                self.scenario_logic.has_base() &
                self.scenario_logic.military.has_siege() &
                self.scenario_logic.military.counters(Age2UnitLineData.KNIGHT_LINE, Age2AgeData.CASTLE) &
                self.scenario_logic.military.counters(Age2UnitLineData.SPEARMAN_LINE, Age2AgeData.CASTLE)
            )|
            (
                self.scenario_logic.has_base() &
                self.scenario_logic.military.has_navy(Age2AgeData.IMPERIAL) &
                self.scenario_logic.military.has_naval_bombardment()
            )
        )
        can_beat_yellow: Rule = (
            self.scenario_logic.has_base() &
            self.scenario_logic.military.has_siege() &
            self.scenario_logic.military.counters(Age2UnitLineData.LONGBOWMAN_LINE, Age2AgeData.IMPERIAL) &
            self.scenario_logic.military.counters(Age2UnitLineData.KNIGHT_LINE, Age2AgeData.IMPERIAL) &
            self.scenario_logic.military.counters(Age2UnitLineData.MANGONEL_LINE, Age2AgeData.IMPERIAL) &
            self.scenario_logic.military.counters(Age2UnitLineData.TREBUCHET_LINE, Age2AgeData.IMPERIAL)
        )
        
        self.world.set_rule(self.locations[Age2ScenarioLocationData.JOAN4_DESTROY_CHALONS_TC], can_beat_green)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.JOAN4_DESTROY_TROYES_TC], can_beat_orange)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.JOAN4_DESTROY_RHEIMS_TC], can_beat_yellow)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.JOAN4_VICTORY], can_beat_green & can_beat_orange & can_beat_yellow)
        self.world.set_rule(self.world.get_location("Complete " + Age2ScenarioLocationData.JOAN4_VICTORY.scenario.scenario_name), can_beat_green & can_beat_orange & can_beat_yellow)