import logging
from typing import TYPE_CHECKING

from BaseClasses import Entrance, Location
from rule_builder.rules import Rule
from ..locations.Scenarios import Age2ScenarioData
from ..locations.Locations import SCENARIO_TO_SCENARIO_LOCATIONS, Age2ScenarioLocationData
from ..locations.Players import TRADE_BUILDINGS
from ..logic.ScenarioLogic import ScenarioLogic

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
        self.scenario_logic = rules.logic.for_scenario(scenario)
        self.entrance = self.world.get_entrance(scenario.scenario_name)
        for location in SCENARIO_TO_SCENARIO_LOCATIONS[scenario]:
            if not self.world.pool.scenarios.includes_location(location):
                continue
            try:
                self.locations[location] = self.world.get_location(location.global_name())
            except KeyError:
                logger.debug("%s is not in this playthrough.", location.global_name())
    
    def set_defeat_event_rules(self):
        for player in self.scenario.players:
            if not self.world.options.partner_trade.needs_defeat_event(player):
                continue
            event_name = player.defeat_event(self.scenario.scenario_name)
            event = self.world.get_location(event_name)
            self.world.set_rule(event, self.scenario_logic.player_logic.defeats(player))

    def set_guard_event_rules(self):
        for player in self.scenario.players:
            for building in TRADE_BUILDINGS:
                if not self.world.options.partner_trade.needs_guard_event(player, building):
                    continue
                event_name = player.guard_event(self.scenario.scenario_name, building)
                event = self.world.get_location(event_name)
                self.world.set_rule(
                    event, self.scenario_logic.player_logic.guards(player, building))

    def set_rules(self):
        self.world.set_rule(self.entrance, self.scenario_logic.is_unlocked())
        self.has_navy: Rule = self.scenario_logic.military.has_navy()
        self.has_military: Rule = self.scenario_logic.military.has_military()