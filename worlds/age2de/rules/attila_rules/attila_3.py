from rule_builder.rules import Rule
from ...locations.Buildings import Age2BuildingData

from ...locations.Locations import Age2ScenarioLocationData
from ...locations.Scenarios import Age2ScenarioData
from ...locations.Players import Age2PlayerData
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
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT3_GREEN_TC], defeats(Age2PlayerData.ATT3_MARCIANOPOLIS))
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT3_RED_TC], defeats(Age2PlayerData.ATT3_PHILIPPOPOLIS))
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT3_RED_MARKET], self.has_military)

        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT3_BUILD_CASTLE], self.scenario_logic.buildings.can_build_building(Age2BuildingData.CASTLE))
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT3_BLUE_COGS], self.has_navy)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT3_BLUE_DOCK_NORTH], self.has_navy)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT3_BLUE_DOCKS_SOUTH], self.has_navy)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT3_THREATEN_WONDER], defeats(Age2PlayerData.ATT3_CONSTANTINOPLE))
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT3_DESTROY_WONDER], defeats(Age2PlayerData.ATT3_CONSTANTINOPLE))

        can_win_scenario: Rule = (
            ((defeats(Age2PlayerData.ATT3_PHILIPPOPOLIS) | defeats(Age2PlayerData.ATT3_MARCIANOPOLIS)) & self.has_navy) |
            defeats(Age2PlayerData.ATT3_CONSTANTINOPLE)
        )
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT3_VICTORY], can_win_scenario)
        self.world.set_rule(self.world.get_location("Complete " + Age2ScenarioLocationData.ATT3_VICTORY.scenario.scenario_name), can_win_scenario)
