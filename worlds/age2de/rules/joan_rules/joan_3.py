from rule_builder.rules import Rule

from ...locations.Locations import Age2ScenarioLocationData
from ...locations.Scenarios import Age2ScenarioData
from ...locations.Players import Age2PlayerData
from ..ScenarioRules import ScenarioRules


class Joan3Rules(ScenarioRules):
    def __init__(self, rules):
        super().__init__(rules, Age2ScenarioData.AP_JOAN_3)

    def set_rules(self):
        super().set_rules()
        can_defeat_english: Rule = self.scenario_logic.defeats(Age2PlayerData.JOAN3_ENGLISH)
        can_defeat_fastolf: Rule = self.scenario_logic.defeats(Age2PlayerData.JOAN3_FASTOLF)

        self.world.set_rule(self.locations[Age2ScenarioLocationData.JOAN3_SLAY_FASTOLF], can_defeat_fastolf)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.JOAN3_VICTORY], can_defeat_english & can_defeat_fastolf)
        self.world.set_rule(self.world.get_location("Complete " + Age2ScenarioLocationData.JOAN3_VICTORY.scenario.scenario_name), can_defeat_english & can_defeat_fastolf)

        if self.world.pool.scenarios.all_scenario_branches:
            self.world.set_rule(self.locations[Age2ScenarioLocationData.JOAN3_DESTROY_CENTRAL_CASTLE], can_defeat_english)
            self.world.set_rule(self.locations[Age2ScenarioLocationData.JOAN3_DESTROY_REAR_CASTLE], can_defeat_english)
            self.world.set_rule(self.locations[Age2ScenarioLocationData.JOAN3_DESTROY_LEFT_CASTLE], can_defeat_english)
            self.world.set_rule(self.locations[Age2ScenarioLocationData.JOAN3_DESTROY_RIGHT_CASTLE], can_defeat_english)
        else:
            self.world.set_rule(self.locations[Age2ScenarioLocationData.JOAN3_DESTROY_ONE_CASTLE], can_defeat_english)
            self.world.set_rule(self.locations[Age2ScenarioLocationData.JOAN3_DESTROY_TWO_CASTLES], can_defeat_english & can_defeat_fastolf)
