from __future__ import annotations

from typing import TYPE_CHECKING

from BaseClasses import Region

from ..items.items import InsaniquariumItem, VICTORY_ITEM_NAME
from ..locations.locations import InsaniquariumLocation, InsaniquariumLocationData, VICTORY_LOCATION_NAME

if TYPE_CHECKING:
    from .. import InsaniquariumWorld


def create_regions(world: InsaniquariumWorld) -> None:
    menu = Region(world.origin_region_name, world.player, world.multiworld)

    mock = InsaniquariumLocationData.MOCK_LOCATION
    menu.add_locations({mock.location_name: mock.id}, InsaniquariumLocation)

    # Rules for both locations are set in rules/rules.py.
    menu.add_event(VICTORY_LOCATION_NAME, VICTORY_ITEM_NAME,
                   location_type=InsaniquariumLocation, item_type=InsaniquariumItem)

    world.multiworld.regions += [menu]
