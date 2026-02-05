from __future__ import annotations

from typing import TYPE_CHECKING

from BaseClasses import CollectionState, Item, ItemClassification, Location, Region
from worlds.age2de.Options import Goal

from ..locations.Scenarios import Age2ScenarioData, scenario_names

from ..items.Items import Age2Item
from ..items.Events import Event
from ..locations.Locations import TYPE_TO_LOCATIONS, VICTORY_LOCATIONS, Age2LocationData, Age2LocationType
from worlds.generic.Rules import CollectionRule, set_rule

if TYPE_CHECKING:
    from .. import Age2World

def set_rules(world: Age2World) -> None:
    
    # Attila Scenarios
    att1 = world.get_entrance(Age2ScenarioData.AP_ATTILA_1.scenario_name)
    set_rule(att1, lambda state: state.can_reach_region("Menu", player= world.player)
             and state.has_all(["Attila the Hun Campaign"], world.player))
    
    att2 = world.get_entrance(Age2ScenarioData.AP_ATTILA_2.scenario_name)
    set_rule(att2, lambda state: state.can_reach_location(Age2LocationData.ATT1_VICTORY.global_name(), player= world.player)
             and state.has("Progressive Attila Scenario", world.player))
    world.multiworld.register_indirect_condition(world.get_region(Age2ScenarioData.AP_ATTILA_1.scenario_name), att2)
    
    att3 = world.get_entrance(Age2ScenarioData.AP_ATTILA_3.scenario_name)
    set_rule(att3, lambda state: state.can_reach_location(Age2LocationData.ATT2_VICTORY.global_name(), player= world.player)
             and state.has("Progressive Attila Scenario", world.player, 2))
    world.multiworld.register_indirect_condition(world.get_region(Age2ScenarioData.AP_ATTILA_2.scenario_name), att3)
    
    att4 = world.get_entrance(Age2ScenarioData.AP_ATTILA_4.scenario_name)
    set_rule(att4, lambda state: state.can_reach_location(Age2LocationData.ATT3_VICTORY.global_name(), player= world.player)
             and state.has("Progressive Attila Scenario", world.player, 3))
    world.multiworld.register_indirect_condition(world.get_region(Age2ScenarioData.AP_ATTILA_3.scenario_name), att4)
    
    att5 = world.get_entrance(Age2ScenarioData.AP_ATTILA_5.scenario_name)
    set_rule(att5, lambda state: state.can_reach_location(Age2LocationData.ATT4_VICTORY.global_name(), player= world.player)
             and state.has("Progressive Attila Scenario", world.player, 4))
    world.multiworld.register_indirect_condition(world.get_region(Age2ScenarioData.AP_ATTILA_4.scenario_name), att5)
    
    att6 = world.get_entrance(Age2ScenarioData.AP_ATTILA_6.scenario_name)
    set_rule(att6, lambda state: state.can_reach_location(Age2LocationData.ATT5_VICTORY.global_name(), player= world.player)
             and state.has("Progressive Attila Scenario", world.player, 5))
    world.multiworld.register_indirect_condition(world.get_region(Age2ScenarioData.AP_ATTILA_5.scenario_name), att6)
    
    set_rule(world.get_location(Age2LocationData.ATT1_VICTORY.global_name()), has_attila_1_attila_camp(world) or has_attila_1_bleda_camp(world))
    set_rule(world.get_location(Age2LocationData.ATT1_CAPTURE_HORSES_CAMP.global_name()), has_attila_1_bleda_camp(world))
    set_rule(world.get_location(Age2LocationData.ATT2_VICTORY.global_name()), has_attila_2_vils(world) and can_build_tc(world))
    set_rule(world.get_location(Age2LocationData.ATT2_BUILD_TC.global_name()), has_attila_2_vils(world) and can_build_tc(world))
    set_rule(world.get_location(Age2LocationData.ATT3_BLUE_DOCK_NORTH.global_name()), has_attila_3_gold(world))
    set_rule(world.get_location(Age2LocationData.ATT3_BLUE_DOCKS_SOUTH.global_name()), has_attila_3_gold(world))
    set_rule(world.get_location(Age2LocationData.ATT3_DESTROY_WONDER.global_name()), has_attila_3_gold(world))
    set_rule(world.get_location(Age2LocationData.ATT3_THREATEN_WONDER.global_name()), has_attila_3_gold(world))
    
    victory_locations = []

# starting tc rules

def can_build_tc(world: Age2World) -> CollectionRule:
    return lambda state: state.has_all([Age2Item.TOWN_CENTER_STONE.item_name, Age2Item.TOWN_CENTER_WOOD.item_name], world.player)
 
# scenario-specific rules

def has_attila_1_attila_camp(world: Age2World) -> CollectionRule:
    return lambda state: state.has("Attila, The Scourge of God: Attila's Camp", world.player)

def has_attila_1_bleda_camp(world: Age2World) -> CollectionRule:
    return lambda state: state.has("Attila, The Scourge of God: Bleda's Camp", world.player)

def has_attila_2_vils(world: Age2World) -> CollectionRule:
    return lambda state: state.has("Attila, The Great Ride: Villagers", world.player)

def has_attila_3_gold(world: Age2World) -> CollectionRule:
    return lambda state: state.has_all(["Attila, The Walls of Constantinople: Red Gold", "Attila, The Walls of Constantinople: Green Gold"], world.player)