from BaseClasses import Location
from rule_builder.rules import Has, Rule, True_
from worlds.age2de.logic.attila.Attila3StartingState import Attila3StartingState

from ...items.Items import Age2ItemData
from ...locations.Ages import Age2AgeData
from ...locations.Locations import SCENARIO_TO_LOCATIONS, Age2ScenarioLocationData
from ...logic.attila.Attila1StartingState import Attila1StartingState
from ...logic.Logic import ScenarioLogic
from ...locations.Scenarios import Age2ScenarioData
from ..ScenarioRules import ScenarioRules


class Attila3Rules(ScenarioRules):
    def __init__(self, rules):
        super().__init__(rules, Age2ScenarioData.AP_ATTILA_3)
        self.scenario_logic = ScenarioLogic(self.logic, Attila3StartingState(self.logic))
    
    def set_rules(self):
        super().set_rules()
        can_beat_red: Rule = True_()
        can_beat_green: Rule = True_()
        has_green_gold: Rule = can_beat_green & Has(Age2ItemData.AP_ATTILA_3_GREEN_GOLD)
        has_red_gold: Rule = can_beat_red & Has(Age2ItemData.AP_ATTILA_3_RED_GOLD)
        has_some_gold: Rule = self.logic.buildings.can_mine() | has_green_gold | has_red_gold
        has_much_gold: Rule = self.logic.buildings.can_mine() & has_green_gold & has_red_gold
        can_win_water: Rule = self.logic.military.has_navy() & has_some_gold
        can_beat_blue: Rule = self.logic.military.has_siege() & has_much_gold
        
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT3_BLUE_COGS], can_win_water)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT3_BLUE_DOCK_NORTH], can_win_water)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT3_BLUE_DOCKS_SOUTH], can_win_water)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT3_THREATEN_WONDER], can_beat_blue)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT3_DESTROY_WONDER], can_beat_blue)
        self.world.set_rule(self.locations[Age2ScenarioLocationData.ATT3_VICTORY], (has_much_gold & can_win_water) | can_beat_blue)