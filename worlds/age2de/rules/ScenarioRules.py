from typing import TYPE_CHECKING

from BaseClasses import Entrance, Location
from ..locations.Scenarios import Age2ScenarioData
from ..locations.Locations import SCENARIO_TO_LOCATIONS, Age2ScenarioLocationData
from ..logic.ScenarioLogic import ScenarioLogic






if TYPE_CHECKING:
    from .. import Age2World
    from .Rules import Rules


class ScenarioRules:
    entrance: Entrance
    scenario_logic: ScenarioLogic
    locations: dict[Age2ScenarioLocationData, Location] = {}
    
    def __init__(self, rules: 'Rules', scenario: Age2ScenarioData):
        self.rules = rules
        self.logic = rules.logic
        self.world = rules.world
        self.entrance = self.world.get_entrance(scenario.scenario_name)
        for location in SCENARIO_TO_LOCATIONS[scenario]:
            try:
                self.locations[location] = self.world.get_location(location.global_name())
            except:
                print(location.global_name() + " not in current playthrough.")
                continue
    
    def set_rules(self):
        self.world.set_rule(self.entrance, self.scenario_logic.is_unlocked())