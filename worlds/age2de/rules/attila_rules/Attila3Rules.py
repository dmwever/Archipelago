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
        has_some_gold: Rule = self.scenario_logic.economy.has_source(Resource.GOLD)
        has_much_gold: Rule = self.scenario_logic.economy.has_easy_source(Resource.GOLD)
        can_win_water: Rule = self.scenario_logic.military.has_navy() & has_some_gold
        can_beat_blue: Rule = self.scenario_logic.military.has_siege() & has_much_gold
        
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT3_BUILD_CASTLE], self.scenario_logic.buildings.can_build_building(Age2BuildingData.CASTLE))
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT3_BLUE_COGS], can_win_water)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT3_BLUE_DOCK_NORTH], can_win_water)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT3_BLUE_DOCKS_SOUTH], can_win_water)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT3_THREATEN_WONDER], can_beat_blue)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT3_DESTROY_WONDER], can_beat_blue)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT3_VICTORY], (has_much_gold & can_win_water) | can_beat_blue)
        self.world.set_rule(self.world.get_location("Complete " + Age2ScenarioLocationData.ATT3_VICTORY.scenario.scenario_name), (has_much_gold & can_win_water) | can_beat_blue)