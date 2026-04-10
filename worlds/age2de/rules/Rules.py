from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING

from BaseClasses import CollectionRule, Entrance, Item, ItemClassification, Location
from .attila_rules.Attila6Rules import Attila6Rules
from .attila_rules.Attila5Rules import Attila5Rules
from .attila_rules.Attila4Rules import Attila4Rules
from .attila_rules.Attila3Rules import Attila3Rules
from .attila_rules.Attila2Rules import Attila2Rules
from .attila_rules.Attila1Rules import Attila1Rules
from ..logic.Logic import Logic
from ..locations.Buildings import Age2BuildingData
from ..locations.Ages import Age2AgeData
from .ScenarioRules import ScenarioRules
from .AgeRules import AgeRules
from .BuildingRules import BuildingRules
from rule_builder.rules import CanReachRegion, False_, Has, Rule, True_

from ..locations.Scenarios import Age2ScenarioData

from ..items.Items import Age2ItemData
from ..locations.Locations import VICTORY_LOCATIONS, Age2ScenarioLocationData, Age2LocationType

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
        self.world.get_entrance(entrance_name)

    def set_rule(self, spot: Location | Entrance, rule: CollectionRule | Rule[Age2World]):
        self.world.set_rule(spot, rule)

    def set_rules(self) -> None:
        for key, value in VICTORY_LOCATIONS.items():
            region = self.world.get_region(value.scenario.scenario_name)
            victory_loc = Location(self.world.player, "Complete " + value.scenario.scenario_name, None, region)
            victory_loc.place_locked_item(Item(value.scenario.scenario_name + ": Unlock Next Scenario", ItemClassification.progression, None, self.world.player))
            region.add_event("Complete " + value.scenario.scenario_name, value.scenario.scenario_name + ": Unlock Next Scenario", show_in_spoiler=False)

        # Attila 1
        self.scenario_rules.append(Attila1Rules(self))
        self.scenario_rules.append(Attila2Rules(self))
        self.scenario_rules.append(Attila3Rules(self))
        self.scenario_rules.append(Attila4Rules(self))
        self.scenario_rules.append(Attila5Rules(self))
        self.scenario_rules.append(Attila6Rules(self))

        for scenario in self.scenario_rules:
            scenario.set_rules()
                
        self.age_rules.set_rules()
        self.building_rules.set_rules()