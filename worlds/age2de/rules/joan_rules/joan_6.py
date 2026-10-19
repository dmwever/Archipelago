from rule_builder.rules import HasAll, Rule

from ...items.Items import Age2ItemData
from ...locations.Locations import Age2ScenarioLocationData
from ...locations.Scenarios import Age2ScenarioData
from ...logic.joan.joan_6 import Joan6Player
from ..ScenarioRules import ScenarioRules


class Joan6Rules(ScenarioRules):
    def __init__(self, rules):
        super().__init__(rules, Age2ScenarioData.AP_JOAN_6)

    def set_rules(self):
        super().set_rules()
        can_siege_town: Rule = (
            HasAll(
                Age2ItemData.AP_JOAN_6_ARMY.item_name,
                Age2ItemData.AP_JOAN_6_ARTILLERY.item_name
            ) |
            self.scenario_logic.defeats(Joan6Player.BURGUNDY)
        )
        can_siege_town = self.scenario_logic.named("can besiege the town", can_siege_town)
        can_defeat_english: Rule = self.scenario_logic.defeats(Joan6Player.ENGLISH)

        self.world.set_rule(self.locations[Age2ScenarioLocationData.JOAN6_BURGUNDIAN_TOWN], can_siege_town)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.JOAN6_VICTORY], can_siege_town & can_defeat_english)
        self.world.set_rule(self.world.get_location("Complete " + Age2ScenarioLocationData.JOAN6_VICTORY.scenario.scenario_name), can_siege_town & can_defeat_english)
