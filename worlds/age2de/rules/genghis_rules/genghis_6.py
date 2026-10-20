from rule_builder.rules import Rule

from ...locations.Locations import Age2ScenarioLocationData
from ...locations.Scenarios import Age2ScenarioData
from ...locations.Players import Age2PlayerData
from ..ScenarioRules import ScenarioRules


class Genghis6Rules(ScenarioRules):
    def __init__(self, rules):
        super().__init__(rules, Age2ScenarioData.AP_GENGHIS_6)

    def set_rules(self):
        super().set_rules()

        can_win_scenario: Rule = self.scenario_logic.players.defeats(Age2PlayerData.GEN6_HUNGARY)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.GEN6_VICTORY], can_win_scenario)
        self.world.set_rule(self.world.get_location("Complete " + Age2ScenarioLocationData.GEN6_VICTORY.scenario.scenario_name), can_win_scenario)
