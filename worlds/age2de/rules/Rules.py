from typing import TYPE_CHECKING

from ..items.Items import Age2Item
from ..locations.Locations import Age2LocationData
from worlds.generic.Rules import set_rule

if TYPE_CHECKING:
    from .. import Age2World

def set_rules(world: Age2World) -> None:
    att1 = world.get_entrance("The Great Ride")
    set_rule(att1, lambda state: state.has("The Scourge of God: Victory", world.player))
    
    
    att1_region = world.get_region("The Scourge of God")
    att1_region.add_event(
        "Victory", "The Scourge of God: Victory", location_type=Age2LocationData, item_type=Age2Item
    )
    
    att2_region = world.get_region("The Great Ride")
    att1_region.add_event(
        "Victory", "The Great Ride: Victory", location_type=Age2LocationData, item_type=Age2Item
    )
    world.multiworld.completion_condition[world.player] = lambda state: state.has_all(("The Scourge of God: Victory", "The Great Ride: Victory"), world.player)