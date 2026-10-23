from dataclasses import dataclass
import logging
import os

from .FolderHandler import FolderHandler

from ...campaign import XsdatFile
from ...items import Items
from ...items.Items import Age2ItemData

logger = logging.getLogger("Client")

NOTHING_SENT = -1


@dataclass
class ManagedItem:
    index: int
    data: Age2ItemData
    delivered: bool = False
    spent: bool = False

    @property
    def one_shot(self) -> bool:
        return self.data in Items.ONE_SHOT_ITEMS


class ItemHandler(FolderHandler):
    _items: list[ManagedItem]
    _current_item: int
    _in_flight: list[int]
    _sent_base: int

    def __init__(self):
        self._items = []
        self._current_item = 0
        self._in_flight = []
        self._sent_base = NOTHING_SENT
        super().__init__()

    def in_flight(self) -> bool:
        return len(self._in_flight) != 0

    def try_sync_delivered(self, unlocked_items: list[Age2ItemData], applied: int) -> set[int]:
        try:
            self._sync_applied_items(applied, unlocked_items)
            self._sync_managed_items(unlocked_items)
            return {managed.index for managed in self._items
                    if managed.delivered and managed.one_shot}
        except Exception:
            logger.exception("Could not sync items.")
            return set()

    def try_write_to_file(self, spent: set[int]) -> None:
        for managed in self._items:
            managed.spent = managed.index in spent
            
        current_item = self._current_item
        if current_item < len(self._items):
            unsent = self._items[current_item:]
            item_ids = [self._id_for_game(managed) for managed in unsent]
            if current_item == self._sent_base and item_ids == self._in_flight:
                return
            try:
                with open(self._user_folder + "items.xsdat", "wb") as fp:
                    XsdatFile.write_int(fp, current_item)
                    for item_id in item_ids:
                        XsdatFile.write_int(fp, item_id)
            except Exception:
                logger.exception("Could not write items.xsdat.")
                self._forget_sent()
                return
            self._in_flight = item_ids
            self._sent_base = current_item

    def try_flush_from_folder(self) -> None:
        self._forget_sent()
        try:
            if os.path.exists(self._user_folder + "items.xsdat"):
                os.remove(self._user_folder + "items.xsdat")
        except Exception:
            logger.exception("Could not remove items.xsdat.")

    # -- internals -------------------------------------------------------

    def _forget_sent(self) -> None:
        self._in_flight = []
        self._sent_base = NOTHING_SENT

    def _sync_applied_items(self, applied: int, unlocked_items: list[Age2ItemData]) -> None:
        self._current_item = min(applied, len(unlocked_items))
        if self._current_item != self._sent_base:
            self._forget_sent()

    def _sync_managed_items(self, unlocked_items: list[Age2ItemData]) -> None:
        del self._items[len(unlocked_items):]
        for index, data in enumerate(unlocked_items):
            if index < len(self._items):
                managed = self._items[index]
                managed.data = data
            else:
                managed = ManagedItem(index, data)
                self._items.append(managed)
            managed.delivered = index < self._current_item

    def _id_for_game(self, managed: ManagedItem) -> int:
        return Items.SKIP_ITEM_ID if managed.spent else managed.data.id
