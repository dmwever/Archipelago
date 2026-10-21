from rule_builder.rules import Rule

from ...locations.Locations import Age2ScenarioLocationData
from ...locations.Scenarios import Age2ScenarioData
from ...locations.Players import Age2PlayerData
from ..ScenarioRules import ScenarioRules


class Genghis2Rules(ScenarioRules):
    def __init__(self, rules):
        super().__init__(rules, Age2ScenarioData.AP_GENGHIS_2)

    def set_rules(self):
        super().set_rules()
        defeats = self.scenario_logic.player_logic.defeats

        # Kushluk hides behind both camps, so reaching him asks for both.
        can_win_scenario: Rule = (
            defeats(Age2PlayerData.GEN2_KUSHLUK) &
            defeats(Age2PlayerData.GEN2_KARA_KHITAI)
        )
        self.world.set_rule(self.locations[Age2ScenarioLocationData.GEN2_VICTORY], can_win_scenario)
        self.world.set_rule(self.world.get_location("Complete " + Age2ScenarioLocationData.GEN2_VICTORY.scenario.scenario_name), can_win_scenario)
