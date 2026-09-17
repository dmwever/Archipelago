from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING

from BaseClasses import CollectionRule, Entrance, Location, Region
from ..locations.Campaigns import Age2CampaignData
from ..locations.Scenarios import CAMPAIGN_TO_SCENARIOS, Age2ScenarioData
from ..logic.Logic import Logic
from ..locations.Buildings import Age2BuildingData
from ..locations.Ages import Age2AgeData
from .ScenarioRules import ScenarioRules
from .AgeRules import AgeRules
from .BuildingRules import BuildingRules
from rule_builder.rules import CanReachRegion, False_, Has, Rule, True_

from ..items.Items import Age2ItemData
from ..locations.Locations import VICTORY_SCENARIO_LOCATIONS, Age2ScenarioLocationData, Age2LocationType
from ..locations.connections import ScenarioDataRules

if TYPE_CHECKING:
    from .. import Age2World


class Rules:
    building_rules: BuildingRules
    age_rules: AgeRules
    scenario_rules: list[ScenarioRules]
    logic: Logic
    
    def __init__(self, world: Age2World):
        self.world = world
        self.logic = Logic(world)
        self.building_rules = BuildingRules(self)
        self.age_rules =  AgeRules(self, world)
        self.scenario_rules = []

    def get_entrance(self, entrance_name: str):
        return self.world.get_entrance(entrance_name)

    def set_rule(self, spot: Location | Entrance, rule: CollectionRule | Rule[Age2World]):
        self.world.set_rule(spot, rule)

    def set_rules(self) -> None:
        # The event locations themselves are created in create_regions; only their rules belong here.
        self.world.multiworld.completion_condition[self.world.player] = lambda state: state.has("Victory", self.world.player)
        self.set_rule(self.world.get_location("Victory"), self.logic.has_goal())

        for campaign in self.world.included_campaigns:
            for scenario in CAMPAIGN_TO_SCENARIOS[campaign]:
                self.scenario_rules.append(scenario.rules(self))

        for scenario in self.scenario_rules:
            scenario.set_rules()
                
        self.age_rules.set_rules()
        self.building_rules.set_rules()