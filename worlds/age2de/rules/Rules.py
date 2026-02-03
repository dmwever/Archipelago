from __future__ import annotations

from typing import TYPE_CHECKING

from BaseClasses import CollectionState, Item, ItemClassification, Location, Region
from worlds.age2de.Options import Goal

from ..locations.Scenarios import scenario_names

from ..items.Items import Age2Item
from ..items.Events import Event
from ..locations.Locations import TYPE_TO_LOCATIONS, VICTORY_LOCATIONS, Age2LocationData, Age2LocationType
from worlds.generic.Rules import CollectionRule, set_rule

if TYPE_CHECKING:
    from .. import Age2World

def set_rules(world: Age2World) -> None:
    
    # Attila Scenarios
    att1 = world.get_entrance("The Scourge of God")
    set_rule(att1, lambda state: state.can_reach_region("Menu", player= world.player)
             and state.has_all(["Attila the Hun Campaign"], world.player))
    world.multiworld.register_indirect_condition(world.get_region("Menu"), att1)
    att2 = world.get_entrance("The Great Ride")
    set_rule(att2, lambda state: state.can_reach_location("The Scourge of God: Victory", player= world.player)
             and state.has("Progressive Attila Scenario", world.player))
    world.multiworld.register_indirect_condition(world.get_region("The Scourge of God"), att2)
    att3 = world.get_entrance("The Walls of Constantinople")
    set_rule(att3, lambda state: state.can_reach_location("The Great Ride: Victory", player= world.player)
             and state.has("Progressive Attila Scenario", world.player, 2))
    world.multiworld.register_indirect_condition(world.get_region("The Great Ride"), att2)
    
    set_rule(world.get_location(Age2LocationData.ATT1_VICTORY.global_name()), has_attila_1_camp(world))
    set_rule(world.get_location(Age2LocationData.ATT2_VICTORY.global_name()), has_attila_2_vils(world))
    set_rule(world.get_location(Age2LocationData.ATT2_BUILD_TC.global_name()), has_attila_2_vils(world))
    set_rule(world.get_location(Age2LocationData.ATT3_BLUE_DOCK_NORTH.global_name()), has_attila_3_gold(world))
    set_rule(world.get_location(Age2LocationData.ATT3_BLUE_DOCKS_SOUTH.global_name()), has_attila_3_gold(world))
    set_rule(world.get_location(Age2LocationData.ATT3_DESTROY_WONDER.global_name()), has_attila_3_gold(world))
    set_rule(world.get_location(Age2LocationData.ATT3_THREATEN_WONDER.global_name()), has_attila_3_gold(world))
    
    victory_locations = []
    
# scenario-specific rules

def has_attila_1_camp(world: Age2World) -> CollectionRule:
    return lambda state: state.has_any(["Attila, The Scourge of God: Bleda's Camp", "Attila, The Scourge of God: Attila's Camp"], world.player)

def has_attila_2_vils(world: Age2World) -> CollectionRule:
    return lambda state: state.has("Attila, The Great Ride: Villagers", world.player)

def has_attila_3_gold(world: Age2World) -> CollectionRule:
    return lambda state: state.has_all(["Attila, The Walls of Constantinople: Red Gold", "Attila, The Walls of Constantinople: Green Gold"], world.player)