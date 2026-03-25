from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING

from BaseClasses import Item, ItemClassification, Location
from .AgeRules import AgeRules
from .BuildingRules import BuildingRules
from rule_builder.rules import CanReachRegion, Has, HasAll

from ..locations.Scenarios import Age2ScenarioData

from ..items.Items import Age2ItemData
from ..locations.Locations import VICTORY_LOCATIONS, Age2ScenarioLocationData, Age2LocationType

if TYPE_CHECKING:
    from .. import Age2World


class Rules:
    building_rules: BuildingRules
    age_rules: AgeRules
    
    def __init__(self):
        self.building_rules = BuildingRules(self)
        self.age_rules =  AgeRules(self)
    

    def set_rules(self, world: Age2World) -> None:
        for key, value in VICTORY_LOCATIONS.items():
            region = world.get_region(value.scenario.scenario_name)
            victory_loc = Location(world.player, "Complete " + value.scenario.scenario_name, None, region)
            victory_loc.place_locked_item(Item(value.scenario.scenario_name + ": Unlock Next Scenario", ItemClassification.progression, None, world.player))
            region.add_event("Complete " + value.scenario.scenario_name, value.scenario.scenario_name + ": Unlock Next Scenario", show_in_spoiler=False)

        # Attila Scenarios
        att1 = world.get_entrance(Age2ScenarioData.AP_ATTILA_1.scenario_name)
        world.set_rule(att1, (CanReachRegion("Menu") & Has("Attila the Hun Campaign")))
        
        att2 = world.get_entrance(Age2ScenarioData.AP_ATTILA_2.scenario_name)
        world.set_rule(att2, Has(Age2ScenarioLocationData.ATT1_VICTORY.scenario.scenario_name + ": Unlock Next Scenario") & Has("Progressive Attila Scenario"))
        
        att3 = world.get_entrance(Age2ScenarioData.AP_ATTILA_3.scenario_name)
        world.set_rule(att3, Has(Age2ScenarioLocationData.ATT2_VICTORY.scenario.scenario_name + ": Unlock Next Scenario") & Has("Progressive Attila Scenario", 2))
        
        att4 = world.get_entrance(Age2ScenarioData.AP_ATTILA_4.scenario_name)
        world.set_rule(att4, Has(Age2ScenarioLocationData.ATT3_VICTORY.scenario.scenario_name + ": Unlock Next Scenario") & Has("Progressive Attila Scenario", 3))
        
        att5 = world.get_entrance(Age2ScenarioData.AP_ATTILA_5.scenario_name)
        world.set_rule(att5, Has(Age2ScenarioLocationData.ATT4_VICTORY.scenario.scenario_name + ": Unlock Next Scenario") & Has("Progressive Attila Scenario", 4))
        
        att6 = world.get_entrance(Age2ScenarioData.AP_ATTILA_6.scenario_name)
        world.set_rule(att6, Has(Age2ScenarioLocationData.ATT5_VICTORY.scenario.scenario_name + ": Unlock Next Scenario") & Has("Progressive Attila Scenario", 5))
        
        # starting tc rules
        
        # scenario-specific rules

        attila_camp = Has(Age2ItemData.AP_ATTILA_1_ATTILAS_CAMP.item_name)

        bleda_camp = Has(Age2ItemData.AP_ATTILA_1_BLEDAS_CAMP.item_name)

        attila_2_vils = Has(Age2ItemData.AP_ATTILA_2_VILLAGERS.item_name)

        attila_3_gold = HasAll(Age2ItemData.AP_ATTILA_3_GREEN_GOLD.item_name, Age2ItemData.AP_ATTILA_3_RED_GOLD.item_name)
        
        self.building_rules.set_rules(world)
        
        world.set_rule(world.get_location(Age2ScenarioLocationData.ATT1_VICTORY.global_name()),
                (attila_camp | bleda_camp) & self.age_rules.can_reach_castle)
        world.set_rule(world.get_location("Complete " + Age2ScenarioLocationData.ATT1_VICTORY.scenario.scenario_name),
                (attila_camp | bleda_camp) & self.age_rules.can_reach_castle)
        world.set_rule(world.get_location(Age2ScenarioLocationData.ATT1_DEFEAT_FIRST_PLAYER.global_name()),
                (attila_camp | bleda_camp) & self.age_rules.can_reach_feudal)
        world.set_rule(world.get_location(Age2ScenarioLocationData.ATT1_CAPTURE_HORSES_CAMP.global_name()), bleda_camp)
        world.set_rule(world.get_location(Age2ScenarioLocationData.ATT2_VICTORY.global_name()), attila_2_vils & self.age_rules.can_reach_feudal)
        world.set_rule(world.get_location("Complete " + Age2ScenarioLocationData.ATT2_VICTORY.scenario.scenario_name), attila_2_vils & self.age_rules.can_reach_feudal)
        world.set_rule(world.get_location(Age2ScenarioLocationData.ATT2_BUILD_TC.global_name()), attila_2_vils & self.age_rules.can_reach_feudal)
        world.set_rule(world.get_location(Age2ScenarioLocationData.ATT2_BEAT_THE_ROMANS.global_name()), attila_2_vils & self.age_rules.can_reach_feudal)
        world.set_rule(world.get_location(Age2ScenarioLocationData.ATT3_BLUE_DOCK_NORTH.global_name()), attila_3_gold)
        world.set_rule(world.get_location(Age2ScenarioLocationData.ATT3_BLUE_DOCKS_SOUTH.global_name()), attila_3_gold)
        world.set_rule(world.get_location(Age2ScenarioLocationData.ATT3_DESTROY_WONDER.global_name()), attila_3_gold)
        world.set_rule(world.get_location(Age2ScenarioLocationData.ATT3_THREATEN_WONDER.global_name()), attila_3_gold)
        world.set_rule(world.get_entrance(Age2ScenarioData.AP_ATTILA_4.scenario_name), self.age_rules.can_build_tc)