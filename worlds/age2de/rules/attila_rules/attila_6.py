from rule_builder.rules import Rule

from ...locations.Locations import Age2ScenarioLocationData
from ...locations.Scenarios import Age2ScenarioData
from ...logic.attila.attila_6 import Attila6Player
from ..ScenarioRules import ScenarioRules


class Attila6Rules(ScenarioRules):
    def __init__(self, rules):
        super().__init__(rules, Age2ScenarioData.AP_ATTILA_6)

    def set_rules(self):
        super().set_rules()
        defeats = self.scenario_logic.defeats

        can_win_scenario: Rule = (
            defeats(Attila6Player.VERONA) &
            defeats(Attila6Player.MEDIOLANUM) &
            defeats(Attila6Player.PATAVIUM) &
            defeats(Attila6Player.AQUILEIA)
        )

        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT6_DEFEAT_AQUILEIA], defeats(Attila6Player.AQUILEIA))
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT6_DESTROY_RED_WONDER], defeats(Attila6Player.AQUILEIA))
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT6_DEFEAT_MEDIOLANUM], defeats(Attila6Player.MEDIOLANUM))
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT6_DESTROY_GREEN_WONDER], defeats(Attila6Player.MEDIOLANUM))
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT6_DEFEAT_PATAVIUM], defeats(Attila6Player.PATAVIUM) & defeats(Attila6Player.VERONA))
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT6_DESTROY_PURPLE_WONDER], defeats(Attila6Player.PATAVIUM))
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT6_DESTROY_PURPLE_WONDER_2], defeats(Attila6Player.PATAVIUM))
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT6_DEFEAT_VERONA], defeats(Attila6Player.VERONA))
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT6_DESTROY_ORANGE_WONDER], defeats(Attila6Player.VERONA))
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT6_DEFEAT_THE_ITALIANS], can_win_scenario)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT6_VICTORY], can_win_scenario)
        self.world.set_rule(self.world.get_location("Complete " + Age2ScenarioLocationData.ATT6_VICTORY.scenario.scenario_name), can_win_scenario)
