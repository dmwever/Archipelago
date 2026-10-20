from rule_builder.rules import Has, Rule

from ...items.Items import Age2ItemData
from ...locations.Locations import Age2ScenarioLocationData
from ...locations.Scenarios import Age2ScenarioData
from ...locations.Players import Age2PlayerData
from ..ScenarioRules import ScenarioRules


class Attila1Rules(ScenarioRules):
    def __init__(self, rules):
        super().__init__(rules, Age2ScenarioData.AP_ATTILA_1)

    def set_rules(self):
        super().set_rules()
        defeats = self.scenario_logic.defeats

        can_win_scenario: Rule = (
            defeats(Age2PlayerData.ATT1_EASTERN_ROMAN_EMPIRE) &
            (defeats(Age2PlayerData.ATT1_SCYTHIANS) | defeats(Age2PlayerData.ATT1_PERSIANS))
        )
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT1_VICTORY], can_win_scenario)
        self.world.set_rule(
            self.locations[Age2ScenarioLocationData.ATT1_DEFEAT_FIRST_PLAYER],
            (
                defeats(Age2PlayerData.ATT1_EASTERN_ROMAN_EMPIRE) |
                defeats(Age2PlayerData.ATT1_PERSIANS) |
                defeats(Age2PlayerData.ATT1_SCYTHIANS)
            ),
        )
        self.world.set_rule(
            self.locations[Age2ScenarioLocationData.ATT1_CAPTURE_HORSES_CAMP],
            Has(Age2ItemData.AP_ATTILA_1_BLEDAS_CAMP.item_name)
        )

        self.world.set_rule(self.world.get_location("Complete " + Age2ScenarioLocationData.ATT1_VICTORY.scenario.scenario_name), can_win_scenario)
