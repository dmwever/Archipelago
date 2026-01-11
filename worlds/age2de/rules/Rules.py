from __future__ import annotations

from typing import TYPE_CHECKING

from BaseClasses import CollectionState, Item, ItemClassification, Location, Region
from worlds.age2de.Options import Goal

from ..locations.Scenarios import scenario_names

from ..items.Items import Age2Item
from ..items.Events import Event
from ..locations.Locations import TYPE_TO_LOCATIONS, VICTORY_LOCATIONS, Age2LocationData, Age2LocationType
from worlds.generic.Rules import set_rule

if TYPE_CHECKING:
    from .. import Age2World

def set_rules(world: Age2World) -> None:
    att1 = world.get_entrance("The Scourge of God")
    set_rule(att1, lambda state: state.can_reach_region("Menu", player= world.player)
             and state.has_all(["Attila the Hun Campaign"], world.player))
    att2 = world.get_entrance("The Great Ride")
    set_rule(att2, lambda state: state.can_reach_location("The Scourge of God: Victory", player= world.player)
             and state.has("Progressive Attila Scenario", world.player))
    
    
    victory_locations = []
    
    if world.options.goal == Goal.option_campaign_completion:
        *_, last = world.get_regions()
        location_data: Age2LocationData = VICTORY_LOCATIONS[last.name]
        location: Location = next(l for l in last.locations if l.name == location_data.global_name())
        location.place_locked_item(Item(Event.victory, ItemClassification.progression, 0, world.player))
        world.multiworld.completion_condition[world.player] = lambda state: state.has(Event.victory, world.player)