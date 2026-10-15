from rule_builder.rules import Has, Rule, True_
from ...locations.Buildings import Age2BuildingData

from ...items.Items import Age2ItemData, Resource
from ...locations.Locations import Age2ScenarioLocationData
from ...locations.Scenarios import Age2ScenarioData
from ..ScenarioRules import ScenarioRules


class Attila3Rules(ScenarioRules):
    def __init__(self, rules):
        super().__init__(rules, Age2ScenarioData.AP_ATTILA_3)
    
    def set_rules(self):
        super().set_rules()
        can_beat_blue: Rule = self.has_military & self.scenario_logic.military.has_siege()
        can_beat_blue = self.scenario_logic.named("can beat Blue", can_beat_blue)
        can_beat_red_or_green: Rule = self.has_military & self.scenario_logic.military.counters_building()
        can_beat_red_or_green = self.scenario_logic.named("can beat Red or Green", can_beat_red_or_green)

        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT3_GREEN_DOCK_NORTH], self.has_military | self.has_navy)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT3_GREEN_DOCK_SOUTH], self.has_military | self.has_navy)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT3_RED_DOCK], self.has_navy)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT3_GREEN_TC], can_beat_red_or_green)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT3_RED_TC], can_beat_red_or_green)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT3_RED_MARKET], self.has_military)

        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT3_BUILD_CASTLE], self.scenario_logic.buildings.can_build_building(Age2BuildingData.CASTLE))
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT3_BLUE_COGS], self.has_navy)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT3_BLUE_DOCK_NORTH], self.has_navy)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT3_BLUE_DOCKS_SOUTH], self.has_navy)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT3_THREATEN_WONDER], can_beat_blue)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT3_DESTROY_WONDER], can_beat_blue)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT3_VICTORY], (can_beat_red_or_green & self.has_navy) | can_beat_blue)
        self.world.set_rule(self.world.get_location("Complete " + Age2ScenarioLocationData.ATT3_VICTORY.scenario.scenario_name), (can_beat_red_or_green & self.has_navy) | can_beat_blue)