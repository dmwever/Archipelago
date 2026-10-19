from rule_builder.rules import Rule
from ...locations.Buildings import Age2BuildingData

from ...locations.Locations import Age2ScenarioLocationData
from ...locations.Scenarios import Age2ScenarioData
from ...logic.attila.attila_3 import Attila3Player
from ..ScenarioRules import ScenarioRules


class Attila3Rules(ScenarioRules):
    def __init__(self, rules):
        super().__init__(rules, Age2ScenarioData.AP_ATTILA_3)

    def set_rules(self):
        super().set_rules()
        defeats = self.scenario_logic.defeats

        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT3_GREEN_DOCK_NORTH], self.has_military | self.has_navy)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT3_GREEN_DOCK_SOUTH], self.has_military | self.has_navy)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT3_RED_DOCK], self.has_navy)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT3_GREEN_TC], defeats(Attila3Player.MARCIANOPOLIS))
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT3_RED_TC], defeats(Attila3Player.PHILIPPOPOLIS))
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT3_RED_MARKET], self.has_military)

        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT3_BUILD_CASTLE], self.scenario_logic.buildings.can_build_building(Age2BuildingData.CASTLE))
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT3_BLUE_COGS], self.has_navy)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT3_BLUE_DOCK_NORTH], self.has_navy)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT3_BLUE_DOCKS_SOUTH], self.has_navy)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT3_THREATEN_WONDER], defeats(Attila3Player.CONSTANTINOPLE))
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT3_DESTROY_WONDER], defeats(Attila3Player.CONSTANTINOPLE))

        can_win_scenario: Rule = (
            ((defeats(Attila3Player.PHILIPPOPOLIS) | defeats(Attila3Player.MARCIANOPOLIS)) & self.has_navy) |
            defeats(Attila3Player.CONSTANTINOPLE)
        )
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT3_VICTORY], can_win_scenario)
        self.world.set_rule(self.world.get_location("Complete " + Age2ScenarioLocationData.ATT3_VICTORY.scenario.scenario_name), can_win_scenario)
