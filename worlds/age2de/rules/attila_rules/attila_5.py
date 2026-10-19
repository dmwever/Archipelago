from rule_builder.rules import Rule

from ...locations.Locations import Age2ScenarioLocationData
from ...locations.Scenarios import Age2ScenarioData
from ...logic.attila.attila_5 import Attila5Player
from ..ScenarioRules import ScenarioRules


class Attila5Rules(ScenarioRules):
    def __init__(self, rules):
        super().__init__(rules, Age2ScenarioData.AP_ATTILA_5)

    def set_rules(self):
        super().set_rules()
        defeats = self.scenario_logic.defeats

        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT5_DEFEAT_ALANS], defeats(Attila5Player.ALANS))
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT5_DEFEAT_VISIGOTHS], defeats(Attila5Player.VISIGOTHS))
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT5_DEFEAT_ROMANS], defeats(Attila5Player.WESTERN_ROMAN_EMPIRE))

        can_win_scenario: Rule = (
            defeats(Attila5Player.WESTERN_ROMAN_EMPIRE) &
            defeats(Attila5Player.ALANS) &
            defeats(Attila5Player.VISIGOTHS)
        )
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT5_VICTORY], can_win_scenario)
        self.world.set_rule(self.world.get_location("Complete " + Age2ScenarioLocationData.ATT5_VICTORY.scenario.scenario_name), can_win_scenario)
