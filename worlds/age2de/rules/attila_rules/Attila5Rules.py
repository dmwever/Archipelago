from rule_builder.rules import Has, Rule, True_
from ...logic.attila.Attila5StartingState import Attila5StartingState
from ...logic.attila.Attila3StartingState import Age2BuildingData
from ...locations.Ages import Age2AgeData
from ...logic.attila.Attila4StartingState import Attila4StartingState

from ...items.Items import Age2ItemData
from ...locations.Locations import Age2ScenarioLocationData
from ...logic.Logic import ScenarioLogic
from ...locations.Scenarios import Age2ScenarioData
from ..ScenarioRules import ScenarioRules


class Attila5Rules(ScenarioRules):
    def __init__(self, rules):
        super().__init__(rules, Age2ScenarioData.AP_ATTILA_5)
        self.scenario_logic = ScenarioLogic(self.logic, Attila5StartingState(self.logic))
    
    def set_rules(self):
        super().set_rules()
        can_beat_cyan: Rule = (
            self.scenario_logic.has_tc() &
            self.logic.military.counters_cav_archer(Age2AgeData.IMPERIAL) &
            self.logic.military.counters_knight(Age2AgeData.IMPERIAL) &
            self.logic.military.counters_mangonel(Age2AgeData.IMPERIAL) &
            self.logic.military.counters_trebuchet() &
            self.logic.military.has_long_range_siege()
        )
        can_beat_green: Rule = (
            self.scenario_logic.has_tc() &
            self.logic.military.counters_spear(Age2AgeData.IMPERIAL) &
            self.logic.military.counters_militia(Age2AgeData.IMPERIAL) &
            self.logic.military.counters_huskarl(Age2AgeData.IMPERIAL) &
            self.logic.military.counters_ram() &
            self.logic.military.counters_trebuchet() &
            self.logic.military.has_long_range_siege()
        )
        can_beat_blue: Rule = (
            self.scenario_logic.has_tc() &
            self.logic.military.counters_centurion(Age2AgeData.IMPERIAL) &
            self.logic.military.counters_legionary(Age2AgeData.IMPERIAL) &
            self.logic.military.counters_scorpion(Age2AgeData.IMPERIAL) &
            self.logic.military.counters_trebuchet() &
            self.logic.military.has_long_range_siege()
        )
        
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT5_DEFEAT_ALANS], can_beat_cyan)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT5_DEFEAT_VISIGOTHS], can_beat_green)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT5_DEFEAT_ROMANS], can_beat_blue)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT5_VICTORY], can_beat_blue & can_beat_cyan & can_beat_green)