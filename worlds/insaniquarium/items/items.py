from __future__ import annotations

import enum
from typing import TYPE_CHECKING

from BaseClasses import Item, ItemClassification

from ..generation.identity import GAME_NAME

if TYPE_CHECKING:
    from .. import InsaniquariumWorld


class InsaniquariumItem(Item):
    game = GAME_NAME


class InsaniquariumItemData(enum.IntEnum):
    """Every item in the pool. Ids must match the AP_*_ITEM_ID constants in WinFish's APBridge.cpp."""

    def __new__(cls, id: int, item_name: str, classification: ItemClassification) -> InsaniquariumItemData:
        obj = int.__new__(cls, id)
        obj._value_ = id
        return obj

    def __init__(self, id: int, item_name: str, classification: ItemClassification) -> None:
        self.id = id
        self.item_name = item_name
        self.classification = classification

    MOCK_ITEM = 1, "Mock Item", ItemClassification.progression


# Event item placed on the Victory event location; never in the pool and has no id.
VICTORY_ITEM_NAME = "Victory"

NAME_TO_ITEM: dict[str, InsaniquariumItemData] = {item.item_name: item for item in InsaniquariumItemData}
item_name_to_id: dict[str, int] = {item.item_name: item.id for item in InsaniquariumItemData}


def create_item(world: InsaniquariumWorld, name: str) -> InsaniquariumItem:
    item = NAME_TO_ITEM[name]
    return InsaniquariumItem(item.item_name, item.classification, item.id, world.player)
