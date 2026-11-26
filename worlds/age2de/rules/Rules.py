from __future__ import annotations

from typing import TYPE_CHECKING

from BaseClasses import CollectionRule, Entrance, Location
from ..logic.Logic import Logic
from ..logic.custom_logic.ScenarioCompleted import ScenarioCompleted
from ..locations.Locations import VICTORY_SCENARIO_LOCATIONS
from ..locations.Scenarios import Age2ScenarioData
from .ScenarioRules import ScenarioRules
from .AgeRules import AgeRules
from .BuildingRules import BuildingRules
from .TechRules import TechRules
from .UnitRules import UnitRules
from rule_builder.rules import Rule
# Imported for its side effect: binds Age2ScenarioData.<member>.rules, used in set_rules below.
from ..locations.connections import ScenarioDataRules  # noqa: F401

if TYPE_CHECKING:
    from .. import Age2World


class Rules:
    building_rules: BuildingRules
    age_rules: AgeRules
    tech_rules: TechRules
    unit_rules: UnitRules
    scenario_rules: list[ScenarioRules]
    logic: Logic
    
    def __init__(self, world: Age2World):
        self.world = world
        self.logic = Logic(world)
        self.building_rules = BuildingRules(self)
        self.age_rules =  AgeRules(self, world)
        self.tech_rules = TechRules(self)
        self.unit_rules = UnitRules(self)
        self.scenario_rules = []

    def set_rule(self, spot: Location | Entrance, rule: CollectionRule | Rule[Age2World]):
        self.world.set_rule(spot, rule)

    def set_rules(self) -> None:
        # The event locations themselves are created in create_regions; only their rules belong here.
        self.world.multiworld.completion_condition[self.world.player] = lambda state: state.has("Victory", self.world.player)
        self.set_rule(self.world.get_location("Victory"), self.logic.has_goal())

        for campaign in self.world.pool.campaigns.enabled:
            for scenario in self.world.pool.scenarios.in_campaign(campaign):
                self.scenario_rules.append(scenario.rules(self))

        for scenario in self.scenario_rules:
            scenario.set_rules()
            scenario.set_defeat_event_rules()
            scenario.set_guard_event_rules()
        if self.world.tracks_completion:
            self.set_completed_doors()
                
        self.age_rules.set_rules()
        self.building_rules.set_rules()
        self.tech_rules.set_rules()
        # After the scenario rules, which is where the per-scenario logic it reads is built.
        self.unit_rules.set_rules()

    def doors(self) -> dict[Age2ScenarioData, str]:
        return {scenario: f"{scenario.scenario_name}: Unlock Next Scenario"
                for scenario in self.world.pool.scenarios.included
                if scenario.scenario_name in VICTORY_SCENARIO_LOCATIONS}

    def set_completed_doors(self) -> None:
        for scenario in self.doors():
            self.set_rule(self.world.get_location(f"Complete {scenario.scenario_name}"),
                          ScenarioCompleted(scenario))