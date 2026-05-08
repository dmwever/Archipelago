
from ...locations.Locations import Age2ScenarioLocationData

from ...locations.Ages import Age2AgeData

from rule_builder.rules import Rule

from ...logic.joan.joan_4 import Joan4StartingState

from ...logic.Logic import ScenarioLogic
from ...locations.Scenarios import Age2ScenarioData
from ..ScenarioRules import ScenarioRules


class Joan4Rules(ScenarioRules):
    def __init__(self, rules):
        super().__init__(rules, Age2ScenarioData.AP_JOAN_4)
        self.scenario_logic = ScenarioLogic(self.logic, Joan4StartingState(self.logic))
    
    def set_rules(self):
        super().set_rules()
        can_beat_green: Rule = (
            (
                self.scenario_logic.has_tc() &
                self.logic.military.counters_building() &
                self.logic.military.has_navy(Age2AgeData.IMPERIAL) &
                self.logic.military.counters_ram() &
                self.logic.military.counters_scorpion(Age2AgeData.IMPERIAL) &
                self.logic.military.counters_knight(Age2AgeData.IMPERIAL)
            ) |
            (
                self.scenario_logic.has_tc() &
                self.logic.military.has_navy(Age2AgeData.IMPERIAL) &
                self.logic.military.has_naval_bombardment()
            )
        )
        can_beat_orange: Rule = (
            (
                self.scenario_logic.has_tc() &
                self.logic.military.has_siege() &
                self.logic.military.counters_knight(Age2AgeData.CASTLE) &
                self.logic.military.counters_spear(Age2AgeData.CASTLE)
            )|
            (
                self.scenario_logic.has_tc() &
                self.logic.military.has_navy(Age2AgeData.IMPERIAL) &
                self.logic.military.has_naval_bombardment()
            )
        )
        can_beat_yellow: Rule = (
            self.scenario_logic.has_tc() &
            self.logic.military.has_siege() &
            self.logic.military.counters_longbowman(Age2AgeData.IMPERIAL) &
            self.logic.military.counters_knight(Age2AgeData.IMPERIAL) &
            self.logic.military.counters_mangonel(Age2AgeData.IMPERIAL) &
            self.logic.military.counters_trebuchet()
        )
        
        self.world.set_rule(self.locations[Age2ScenarioLocationData.JOAN4_DESTROY_CHALONS_TC], can_beat_green)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.JOAN4_DESTROY_TROYES_TC], can_beat_orange)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.JOAN4_DESTROY_RHEIMS_TC], can_beat_yellow)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.JOAN4_VICTORY], can_beat_green & can_beat_orange & can_beat_yellow)
        self.world.set_rule(self.world.get_location("Complete " + Age2ScenarioLocationData.JOAN4_VICTORY.scenario.scenario_name), can_beat_green & can_beat_orange & can_beat_yellow)