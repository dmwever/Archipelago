import logging
from typing import TYPE_CHECKING

from BaseClasses import Entrance, Location
from ..locations.Scenarios import Age2ScenarioData
from ..locations.Locations import SCENARIO_TO_SCENARIO_LOCATIONS, Age2ScenarioLocationData
from ..scenarios.ScenarioLogic import ScenarioLogic






if TYPE_CHECKING:
    from .. import Age2World
    from .Rules import Rules

logger = logging.getLogger("Age2")


class ScenarioRules:
    entrance: Entrance
    scenario_logic: ScenarioLogic
    locations: dict[Age2ScenarioLocationData, Location]

    def __init__(self, rules: 'Rules', scenario: Age2ScenarioData):
        # Per instance, not per class: as a class attribute every scenario's rule
        # object shared one location dict, across slots as well as scenarios.
        self.locations = {}
        self.rules = rules
        self.logic = rules.logic
        self.world = rules.world
        self.scenario = scenario
        self.entrance = self.world.get_entrance(scenario.scenario_name)
        for location in SCENARIO_TO_SCENARIO_LOCATIONS[scenario]:
            if not self.world.branching_option(location):
                continue
            try:
                self.locations[location] = self.world.get_location(location.global_name())
            except KeyError:
                logger.debug("%s is not in this playthrough.", location.global_name())
    
    def set_rules(self):
        self.world.set_rule(self.entrance, self.scenario_logic.is_unlocked())