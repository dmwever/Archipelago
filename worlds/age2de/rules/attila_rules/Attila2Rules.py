from rule_builder.rules import Has, Rule
from ...logic.attila.Attila2StartingState import Attila2StartingState

from ...items.Items import Age2ItemData
from ...locations.Ages import Age2AgeData
from ...locations.Locations import Age2ScenarioLocationData
from ...logic.attila.Attila1StartingState import Attila1StartingState
from ...logic.Logic import ScenarioLogic
from ...locations.Scenarios import Age2ScenarioData
from ..ScenarioRules import ScenarioRules


class Attila2Rules(ScenarioRules):
    scythian_troop: Rule = Has(Age2ItemData.AP_ATTILA_2_SCYTHIAN_TROOP.item_name)
    def __init__(self, rules):
        super().__init__(rules, Age2ScenarioData.AP_ATTILA_2)
        self.scenario_logic = ScenarioLogic(self.logic, Attila2StartingState(self.logic))
    
    def set_rules(self):
        super().set_rules()
        can_beat_blue: Rule =  (
            self.scythian_troop |
            (
                self.scenario_logic.has_tc() &
                self.logic.has_siege() &
                self.logic.military.counters_knight() &
                self.logic.military.counters_militia(Age2AgeData.CASTLE) &
                self.logic.military.counters_spear(Age2AgeData.CASTLE)
            )
        )
        can_build_tc = self.scenario_logic.has_tc()
        
        self.world.set_rule(self.world.get_location(Age2ScenarioLocationData.ATT2_VICTORY.global_name()), can_beat_blue & can_build_tc)
        self.world.set_rule(self.world.get_location("Complete " + Age2ScenarioLocationData.ATT2_VICTORY.scenario.scenario_name), can_beat_blue & can_build_tc)
        self.world.set_rule(self.world.get_location(Age2ScenarioLocationData.ATT2_BUILD_TC.global_name()), can_build_tc)
        self.world.set_rule(self.world.get_location(Age2ScenarioLocationData.ATT2_BEAT_THE_ROMANS.global_name()), can_beat_blue)
