from rule_builder.rules import Rule
from ...logic.attila.Attila6StartingState import Attila6StartingState
from ...locations.Ages import Age2AgeData

from ...locations.Locations import Age2ScenarioLocationData
from ...logic.Logic import ScenarioLogic
from ...locations.Scenarios import Age2ScenarioData
from ..ScenarioRules import ScenarioRules


class Attila6Rules(ScenarioRules):
    def __init__(self, rules):
        super().__init__(rules, Age2ScenarioData.AP_ATTILA_6)
        self.scenario_logic = ScenarioLogic(self.logic, Attila6StartingState(self.logic))
    
    def set_rules(self):
        super().set_rules()
        can_beat_red: Rule = (
            self.logic.military.counters_spear(Age2AgeData.IMPERIAL) &
            self.logic.military.counters_scout(Age2AgeData.IMPERIAL) &
            self.logic.military.counters_knight(Age2AgeData.IMPERIAL) &
            self.logic.military.counters_scorpion(Age2AgeData.IMPERIAL) &
            self.logic.military.has_siege()
        )
        
        can_beat_green: Rule = (
            (
                self.logic.military.has_navy(Age2AgeData.IMPERIAL) &
                self.logic.military.has_naval_bombardment()
            ) |
            (
                self.logic.military.counters_archer(Age2AgeData.IMPERIAL) &
                self.logic.military.counters_knight(Age2AgeData.IMPERIAL) &
                self.logic.military.counters_mangonel(Age2AgeData.IMPERIAL) &
                self.logic.military.counters_trebuchet()
            )
        )
        
        can_beat_purple: Rule = (
            self.logic.military.counters_militia(Age2AgeData.IMPERIAL) &
            self.logic.military.counters_archer(Age2AgeData.IMPERIAL) &
            self.logic.military.counters_longbowman(Age2AgeData.IMPERIAL) &
            self.logic.military.counters_mangonel(Age2AgeData.IMPERIAL) &
            self.logic.military.has_long_range_siege()
        )
        
        can_beat_orange: Rule = (
            self.logic.military.counters_archer(Age2AgeData.IMPERIAL) &
            self.logic.military.counters_throwing_axeman(Age2AgeData.IMPERIAL) &
            self.logic.military.counters_knight(Age2AgeData.IMPERIAL) &
            self.logic.military.counters_trebuchet() &
            self.logic.military.counters_monk() &
            self.logic.military.has_long_range_siege()
        )
        can_beat_blue: Rule = self.logic.military.has_military()
        victory = can_beat_orange & can_beat_green & can_beat_purple & can_beat_red
        
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT6_DEFEAT_AQUILEIA], can_beat_red)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT6_DESTROY_RED_WONDER], can_beat_red)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT6_DEFEAT_MEDIOLANUM], can_beat_green)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT6_DESTROY_GREEN_WONDER], can_beat_green)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT6_DEFEAT_PATAVIUM], can_beat_purple & can_beat_orange)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT6_DESTROY_PURPLE_WONDER], can_beat_purple)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT6_DESTROY_PURPLE_WONDER_2], can_beat_purple)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT6_DEFEAT_VERONA], can_beat_orange)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT6_DESTROY_ORANGE_WONDER], can_beat_orange)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT6_DEFEAT_THE_ITALIANS], victory)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT6_VICTORY], victory)