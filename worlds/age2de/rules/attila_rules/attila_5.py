from rule_builder.rules import Has, Rule

from ...items.Items import Age2ItemData
from ...locations.Locations import Age2ScenarioLocationData
from ...locations.Scenarios import Age2ScenarioData
from ...locations.Players import Age2PlayerData
from ..ScenarioRules import ScenarioRules


class Attila5Rules(ScenarioRules):
    def __init__(self, rules):
        super().__init__(rules, Age2ScenarioData.AP_ATTILA_5)

    def set_rules(self):
        super().set_rules()
        defeats = self.scenario_logic.player_logic.defeats
        has_deathmatch_resources = Has(Age2ItemData.AP_ATTILA_5_DEATHMATCH.item_name)

        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT5_DEFEAT_ALANS], 
            defeats(Age2PlayerData.ATT5_ALANS) & has_deathmatch_resources
        )
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT5_DEFEAT_VISIGOTHS],
            defeats(Age2PlayerData.ATT5_VISIGOTHS) & has_deathmatch_resources
        )
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT5_DEFEAT_ROMANS],
            defeats(Age2PlayerData.ATT5_WESTERN_ROMAN_EMPIRE) & has_deathmatch_resources
        )

        can_win_scenario: Rule = (
            defeats(Age2PlayerData.ATT5_WESTERN_ROMAN_EMPIRE) &
            defeats(Age2PlayerData.ATT5_ALANS) &
            defeats(Age2PlayerData.ATT5_VISIGOTHS) &
            has_deathmatch_resources
        )
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT5_VICTORY], can_win_scenario)
        self.world.set_rule(self.world.get_location("Complete " + Age2ScenarioLocationData.ATT5_VICTORY.scenario.scenario_name), can_win_scenario)
