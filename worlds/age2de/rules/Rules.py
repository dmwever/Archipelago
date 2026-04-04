from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING

from BaseClasses import CollectionRule, Entrance, Item, ItemClassification, Location
from .attila_rules.Attila1Rules import Attila1Rules
from ..logic.Logic import Logic
from ..locations.Buildings import Age2BuildingData
from ..locations.Ages import Age2AgeData
from .ScenarioRules import ScenarioRules
from .AgeRules import AgeRules
from .BuildingRules import BuildingRules
from rule_builder.rules import CanReachRegion, False_, Has, HasAll, Rule, True_

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
        self.building_rules = BuildingRules(self)
        self.age_rules =  AgeRules(self, world)
        self.scenario_rules = []
        self.world = world
        self.logic = Logic(world)

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

        for scenario in self.scenario_rules:
            scenario.set_rules()
        
        # Attila 2
        att2 = self.world.get_entrance(Age2ScenarioData.AP_ATTILA_2.scenario_name)
        self.world.set_rule(att2, Has(Age2ScenarioLocationData.ATT1_VICTORY.scenario.scenario_name + ": Unlock Next Scenario") & Has("Progressive Attila Scenario"))
        
        att3 = self.world.get_entrance(Age2ScenarioData.AP_ATTILA_3.scenario_name)
        self.world.set_rule(att3, Has(Age2ScenarioLocationData.ATT2_VICTORY.scenario.scenario_name + ": Unlock Next Scenario") & Has("Progressive Attila Scenario", 2))
        
        att4 = self.world.get_entrance(Age2ScenarioData.AP_ATTILA_4.scenario_name)
        self.world.set_rule(att4, Has(Age2ScenarioLocationData.ATT3_VICTORY.scenario.scenario_name + ": Unlock Next Scenario") & Has("Progressive Attila Scenario", 3))
        
        att5 = self.world.get_entrance(Age2ScenarioData.AP_ATTILA_5.scenario_name)
        self.world.set_rule(att5, Has(Age2ScenarioLocationData.ATT4_VICTORY.scenario.scenario_name + ": Unlock Next Scenario") & Has("Progressive Attila Scenario", 4))
        
        att6 = self.world.get_entrance(Age2ScenarioData.AP_ATTILA_6.scenario_name)
        self.world.set_rule(att6, Has(Age2ScenarioLocationData.ATT5_VICTORY.scenario.scenario_name + ": Unlock Next Scenario") & Has("Progressive Attila Scenario", 5))
        
        # starting tc rules
        
        # scenario-specific rules

        attila_2_vils = Has(Age2ItemData.AP_ATTILA_2_VILLAGERS.item_name)

        attila_3_gold = HasAll(Age2ItemData.AP_ATTILA_3_GREEN_GOLD.item_name, Age2ItemData.AP_ATTILA_3_RED_GOLD.item_name)
        
        self.age_rules.set_rules()
        self.building_rules.set_rules()
        
        self.world.set_rule(self.world.get_location(Age2ScenarioLocationData.ATT2_VICTORY.global_name()), attila_2_vils & self.logic.ages.can_reach_feudal())
        self.world.set_rule(self.world.get_location("Complete " + Age2ScenarioLocationData.ATT2_VICTORY.scenario.scenario_name), attila_2_vils & self.logic.ages.can_reach_feudal())
        self.world.set_rule(self.world.get_location(Age2ScenarioLocationData.ATT2_BUILD_TC.global_name()), attila_2_vils & self.logic.ages.can_reach_feudal())
        self.world.set_rule(self.world.get_location(Age2ScenarioLocationData.ATT2_BEAT_THE_ROMANS.global_name()), attila_2_vils & self.logic.ages.can_reach_feudal())
        self.world.set_rule(self.world.get_location(Age2ScenarioLocationData.ATT3_BLUE_DOCK_NORTH.global_name()), attila_3_gold)
        self.world.set_rule(self.world.get_location(Age2ScenarioLocationData.ATT3_BLUE_DOCKS_SOUTH.global_name()), attila_3_gold)
        self.world.set_rule(self.world.get_location(Age2ScenarioLocationData.ATT3_DESTROY_WONDER.global_name()), attila_3_gold)
        self.world.set_rule(self.world.get_location(Age2ScenarioLocationData.ATT3_THREATEN_WONDER.global_name()), attila_3_gold)
        self.world.set_rule(self.world.get_entrance(Age2ScenarioData.AP_ATTILA_4.scenario_name), self.logic.buildings.can_build_tc())