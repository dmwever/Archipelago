from rule_builder.rules import Rule

from ...locations.Locations import Age2ScenarioLocationData
from ...locations.Scenarios import Age2ScenarioData
from ...logic.genghis.genghis_6 import Genghis6Player
from ..ScenarioRules import ScenarioRules


class Genghis6Rules(ScenarioRules):
    def __init__(self, rules):
        super().__init__(rules, Age2ScenarioData.AP_GENGHIS_6)

    def set_rules(self):
        super().set_rules()

        can_win_scenario: Rule = self.scenario_logic.defeats(Genghis6Player.HUNGARY)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.GEN6_VICTORY], can_win_scenario)
        self.world.set_rule(self.world.get_location("Complete " + Age2ScenarioLocationData.GEN6_VICTORY.scenario.scenario_name), can_win_scenario)
