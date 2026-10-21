import logging
import os

from .FolderHandler import FolderHandler

from ...campaign import XsdatFile
from ...items import Items
from ...items.Items import Age2ItemData

logger = logging.getLogger("Client")


class ItemHandler(FolderHandler):
    def __init__(self, client_interface):
        self._client_interface = client_interface
        self._current_item: int = 0
        self._spent: set[int] = set()
        self._in_flight: list[int] = []
        self._sent_base: int = -1
        super().__init__()

    def current_item_index(self) -> int:
        return self._current_item

    def in_flight(self) -> bool:
        return len(self._in_flight) != 0

    def set_current_item_index(self, unlocked_items: list[Age2ItemData]) -> None:
        self._current_item = min(self._current_item, len(unlocked_items))

    def sync_items(self, unlocked_items: list[Age2ItemData], applied: int,
                   spent: set[int]) -> None:
        self._spent = spent
        self._sync_applied_items(applied, unlocked_items)
        self._report_delivered(unlocked_items)
        if self._current_item < len(unlocked_items):
            self._try_write_to_file(unlocked_items)

    def try_flush_from_folder(self) -> None:
        try:
            if os.path.exists(self._user_folder + "items.xsdat"):
                os.remove(self._user_folder + "items.xsdat")
        except Exception:
            logger.exception("Could not remove items.xsdat.")

    # -- internals -------------------------------------------------------

    def _sync_applied_items(self, applied: int, unlocked_items: list[Age2ItemData]) -> None:
        self._current_item = min(applied, len(unlocked_items))
        if self._current_item != self._sent_base:
            self._in_flight = []

    def _report_delivered(self, unlocked_items: list[Age2ItemData]) -> None:
        delivered = {index for index in range(self._current_item)
                     if index not in self._spent
                     and unlocked_items[index] in Items.ONE_SHOT_ITEMS}
        if not delivered:
            return
        self._spent = self._spent | delivered
        self._client_interface.on_item_spent(delivered)

    def _id_for_game(self, index: int, item: Age2ItemData) -> int:
        if index in self._spent:
            return Items.SKIP_ITEM_ID
        return item.id

    def _try_write_to_file(self, unlocked_items: list[Age2ItemData]) -> None:
        start = self._current_item
        count = min(len(unlocked_items) - start, Items.ITEM_WINDOW)
        window = unlocked_items[start:start + count]
        item_ids = [self._id_for_game(start + offset, item)
                    for offset, item in enumerate(window)]
        if start == self._sent_base and item_ids == self._in_flight:
            return
        try:
            with open(self._user_folder + "items.xsdat", "wb") as fp:
                XsdatFile.write_int(fp, start)
                for item_id in item_ids:
                    XsdatFile.write_int(fp, item_id)
            self._in_flight = item_ids
            self._sent_base = start
        except Exception:
            logger.exception("Could not write items.xsdat.")
