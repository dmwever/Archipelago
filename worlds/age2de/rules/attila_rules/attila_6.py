from rule_builder.rules import Rule

from ...locations.Locations import Age2ScenarioLocationData
from ...locations.Scenarios import Age2ScenarioData
from ...locations.Players import Age2PlayerData
from ..ScenarioRules import ScenarioRules


class Attila6Rules(ScenarioRules):
    def __init__(self, rules):
        super().__init__(rules, Age2ScenarioData.AP_ATTILA_6)

    def set_rules(self):
        super().set_rules()
        defeats = self.scenario_logic.defeats

        can_win_scenario: Rule = (
            defeats(Age2PlayerData.ATT6_VERONA) &
            defeats(Age2PlayerData.ATT6_MEDIOLANUM) &
            defeats(Age2PlayerData.ATT6_PATAVIUM) &
            defeats(Age2PlayerData.ATT6_AQUILEIA)
        )

        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT6_DEFEAT_AQUILEIA], defeats(Age2PlayerData.ATT6_AQUILEIA))
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT6_DESTROY_RED_WONDER], defeats(Age2PlayerData.ATT6_AQUILEIA))
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT6_DEFEAT_MEDIOLANUM], defeats(Age2PlayerData.ATT6_MEDIOLANUM))
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT6_DESTROY_GREEN_WONDER], defeats(Age2PlayerData.ATT6_MEDIOLANUM))
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT6_DEFEAT_PATAVIUM], defeats(Age2PlayerData.ATT6_PATAVIUM) & defeats(Age2PlayerData.ATT6_VERONA))
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT6_DESTROY_PURPLE_WONDER], defeats(Age2PlayerData.ATT6_PATAVIUM))
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT6_DESTROY_PURPLE_WONDER_2], defeats(Age2PlayerData.ATT6_PATAVIUM))
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT6_DEFEAT_VERONA], defeats(Age2PlayerData.ATT6_VERONA))
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT6_DESTROY_ORANGE_WONDER], defeats(Age2PlayerData.ATT6_VERONA))
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT6_DEFEAT_THE_ITALIANS], can_win_scenario)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT6_VICTORY], can_win_scenario)
        self.world.set_rule(self.world.get_location("Complete " + Age2ScenarioLocationData.ATT6_VICTORY.scenario.scenario_name), can_win_scenario)
