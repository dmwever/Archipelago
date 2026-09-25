from __future__ import annotations

from typing import TYPE_CHECKING, NamedTuple

from BaseClasses import Item, ItemClassification as IC

from ..generation.identity import GAME_NAME

if TYPE_CHECKING:
    from .. import InsaniquariumWorld


class InsaniquariumItem(Item):
    game = GAME_NAME


class InsaniquariumItemData(NamedTuple):
    classification: IC
    quantity: int           # copies placed in the pool
    id: int                 # must match the AP_*_ITEM_ID constants in WinFish's APBridge.cpp
    category: str           # becomes the item group


MOCK_ITEM = "Mock Item"

item_table: dict[str, InsaniquariumItemData] = {
    MOCK_ITEM: InsaniquariumItemData(IC.progression, 1, 1, "Mock"),
}

# Event item placed on the Victory event location; never in the pool and has no id.
VICTORY_ITEM_NAME = "Victory"

item_name_to_id: dict[str, int] = {name: data.id for name, data in item_table.items()}

item_name_groups: dict[str, set[str]] = {}
for _name, _data in item_table.items():
    item_name_groups.setdefault(_data.category, set()).add(_name)


def create_item(world: InsaniquariumWorld, name: str) -> InsaniquariumItem:
    data = item_table[name]
    return InsaniquariumItem(name, data.classification, data.id, world.player)


def create_item_pool(world: InsaniquariumWorld) -> list[InsaniquariumItem]:
    return [create_item(world, name) for name, data in item_table.items() for _ in range(data.quantity)]
