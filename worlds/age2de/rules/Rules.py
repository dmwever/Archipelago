from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING

from BaseClasses import Item, ItemClassification, Location
from ..locations.Buildings import Age2BuildingData
from ..locations.Ages import Age2AgeData
from .attila_rules.Attila1StartingState import Attila1StartingState
from .ScenarioRules import ScenarioRules
from .AgeRules import AgeRules
from .BuildingRules import BuildingRules
from rule_builder.rules import CanReachRegion, False_, Has, HasAll, Rule

from ..locations.Scenarios import Age2ScenarioData

from ..items.Items import Age2ItemData
from ..locations.Locations import VICTORY_LOCATIONS, Age2ScenarioLocationData, Age2LocationType

if TYPE_CHECKING:
    from .. import Age2World


class Rules:
    building_rules: BuildingRules
    age_rules: AgeRules
    scenario_rules: list[ScenarioRules]
    
    def __init__(self, world: Age2World):
        self.building_rules = BuildingRules(self, world)
        self.age_rules =  AgeRules(self, world)
        self.scenario_rules = []
        self.world = world

    def set_rules(self) -> None:
        for key, value in VICTORY_LOCATIONS.items():
            region = self.world.get_region(value.scenario.scenario_name)
            victory_loc = Location(self.world.player, "Complete " + value.scenario.scenario_name, None, region)
            victory_loc.place_locked_item(Item(value.scenario.scenario_name + ": Unlock Next Scenario", ItemClassification.progression, None, self.world.player))
            region.add_event("Complete " + value.scenario.scenario_name, value.scenario.scenario_name + ": Unlock Next Scenario", show_in_spoiler=False)

        # Attila 1
        attila1Rules = ScenarioRules(self, data=Attila1StartingState(self))
        self.scenario_rules.append(attila1Rules)
        att1 = self.world.get_entrance(Age2ScenarioData.AP_ATTILA_1.scenario_name)
        self.world.set_rule(att1, attila1Rules.is_unlocked())
        self.world.set_rule(self.world.get_location(Age2ScenarioLocationData.ATT1_VICTORY.global_name()),
                attila1Rules.can_reach_age(Age2AgeData.CASTLE))
        self.world.set_rule(self.world.get_location("Complete " + Age2ScenarioLocationData.ATT1_VICTORY.scenario.scenario_name),
                attila1Rules.can_reach_age(Age2AgeData.CASTLE))
        self.world.set_rule(self.world.get_location(Age2ScenarioLocationData.ATT1_DEFEAT_FIRST_PLAYER.global_name()),
                attila1Rules.can_reach_age(Age2AgeData.FEUDAL))
        self.world.set_rule(self.world.get_location(Age2ScenarioLocationData.ATT1_CAPTURE_HORSES_CAMP.global_name()), Has(Age2ItemData.AP_ATTILA_1_BLEDAS_CAMP.item_name))
        
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
        
        self.building_rules.set_rules()

        self.world.set_rule(self.world.get_location(Age2ScenarioLocationData.ATT2_VICTORY.global_name()), attila_2_vils & self.age_rules.can_reach_feudal())
        self.world.set_rule(self.world.get_location("Complete " + Age2ScenarioLocationData.ATT2_VICTORY.scenario.scenario_name), attila_2_vils & self.age_rules.can_reach_feudal())
        self.world.set_rule(self.world.get_location(Age2ScenarioLocationData.ATT2_BUILD_TC.global_name()), attila_2_vils & self.age_rules.can_reach_feudal())
        self.world.set_rule(self.world.get_location(Age2ScenarioLocationData.ATT2_BEAT_THE_ROMANS.global_name()), attila_2_vils & self.age_rules.can_reach_feudal())
        self.world.set_rule(self.world.get_location(Age2ScenarioLocationData.ATT3_BLUE_DOCK_NORTH.global_name()), attila_3_gold)
        self.world.set_rule(self.world.get_location(Age2ScenarioLocationData.ATT3_BLUE_DOCKS_SOUTH.global_name()), attila_3_gold)
        self.world.set_rule(self.world.get_location(Age2ScenarioLocationData.ATT3_DESTROY_WONDER.global_name()), attila_3_gold)
        self.world.set_rule(self.world.get_location(Age2ScenarioLocationData.ATT3_THREATEN_WONDER.global_name()), attila_3_gold)
        self.world.set_rule(self.world.get_entrance(Age2ScenarioData.AP_ATTILA_4.scenario_name), self.age_rules.can_build_tc())
        
    def can_build(self, building: Age2BuildingData) -> Rule:
        can_build: Rule = False_()
        for rule in self.scenario_rules:
            if rule.is_unlocked():
                can_build = can_build | (rule.is_unlocked() & rule.can_build_building(building))
        return can_build