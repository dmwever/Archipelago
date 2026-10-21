from rule_builder.rules import Rule

from ...locations.Locations import Age2ScenarioLocationData
from ...locations.Scenarios import Age2ScenarioData
from ...locations.Players import Age2PlayerData
from ..ScenarioRules import ScenarioRules


class Joan4Rules(ScenarioRules):
    def __init__(self, rules):
        super().__init__(rules, Age2ScenarioData.AP_JOAN_4)

    def set_rules(self):
        super().set_rules()
        can_defeat_chalons: Rule = self.scenario_logic.player_logic.defeats(Age2PlayerData.JOAN4_CHALONS)
        can_defeat_troyes: Rule = self.scenario_logic.player_logic.defeats(Age2PlayerData.JOAN4_TROYES)
        can_defeat_rheims: Rule = self.scenario_logic.player_logic.defeats(Age2PlayerData.JOAN4_RHEIMS)
        can_win_scenario: Rule = can_defeat_chalons & can_defeat_troyes & can_defeat_rheims

        self.world.set_rule(self.locations[Age2ScenarioLocationData.JOAN4_DESTROY_CHALONS_TC], can_defeat_chalons)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.JOAN4_DESTROY_TROYES_TC], can_defeat_troyes)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.JOAN4_DESTROY_RHEIMS_TC], can_defeat_rheims)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.JOAN4_VICTORY], can_win_scenario)
        self.world.set_rule(self.world.get_location("Complete " + Age2ScenarioLocationData.JOAN4_VICTORY.scenario.scenario_name), can_win_scenario)
