from rule_builder.rules import Rule

from ...locations.Locations import Age2ScenarioLocationData
from ...locations.Scenarios import Age2ScenarioData
from ...logic.genghis.genghis_4 import Genghis4Player
from ..ScenarioRules import ScenarioRules


class Genghis4Rules(ScenarioRules):
    """Only the Kipchaks are hostile when the map opens - the Russians and Khwarazm both
    start allied, and both have to be put down anyway. Neither of their scripts advances an
    age, so each is countered where the scenario placed it: the Russians in Castle, Khwarazm
    already in Imperial with a wonder to raise.
    """

    def __init__(self, rules):
        super().__init__(rules, Age2ScenarioData.AP_GENGHIS_4)

    def set_rules(self):
        super().set_rules()
        defeats = self.scenario_logic.defeats

        self.world.set_rule(
            self.locations[Age2ScenarioLocationData.GEN4_DEFEAT_RUSSIANS],
            defeats(Genghis4Player.RUSSIANS),
        )
        self.world.set_rule(
            self.locations[Age2ScenarioLocationData.GEN4_DEFEAT_KHWARAZM],
            defeats(Genghis4Player.KHWARAZM),
        )

        can_win_scenario: Rule = (
            defeats(Genghis4Player.RUSSIANS) &
            defeats(Genghis4Player.KHWARAZM)
        )
        self.world.set_rule(self.locations[Age2ScenarioLocationData.GEN4_VICTORY], can_win_scenario)
        self.world.set_rule(self.world.get_location("Complete " + Age2ScenarioLocationData.GEN4_VICTORY.scenario.scenario_name), can_win_scenario)
