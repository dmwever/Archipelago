from typing import Any

from worlds.AutoWorld import World

from .generation import slot_data
from .generation.identity import GAME_NAME
from .items import items
from .items.items import InsaniquariumItem, MOCK_ITEM
from .locations import locations
from .options import InsaniquariumOptions
from .regions import regions
from .rules.rules import InsaniquariumRules


class InsaniquariumWorld(World):
    """Insaniquarium Deluxe: feed your fish, fight off aliens, collect the pets."""

    game = GAME_NAME
    options_dataclass = InsaniquariumOptions
    options: InsaniquariumOptions

    item_name_to_id = items.item_name_to_id
    location_name_to_id = locations.location_name_to_id
    item_name_groups = items.item_name_groups

    origin_region_name = "Menu"

    def create_regions(self) -> None:
        regions.create_regions(self)

    def create_items(self) -> None:
        self.multiworld.itempool += items.create_item_pool(self)

    def create_item(self, name: str) -> InsaniquariumItem:
        return items.create_item(self, name)

    def get_filler_item_name(self) -> str:
        # Placeholder until there's a real filler item; the pool already matches the location count.
        return MOCK_ITEM

    def set_rules(self) -> None:
        InsaniquariumRules(self).set_rules()

    def fill_slot_data(self) -> dict[str, Any]:
        return slot_data.build(self)
