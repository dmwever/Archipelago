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
    """One received item, at the position it arrived at.

    Items repeat -- five copies of +100 Wood are five entries -- so what is managed here is the
    position, not the item. That is the one place this cannot follow MercenaryHandler, where an
    item appears at most once and can key a dict.
    """

    index: int
    data: Age2ItemData
    delivered: bool = False
    spent: bool = False

    @property
    def one_shot(self) -> bool:
        """Adds rather than sets, so sending it again would pay it out twice."""
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

    def current_item_index(self) -> int:
        return self._current_item

    def in_flight(self) -> bool:
        return len(self._in_flight) != 0

    def items(self) -> list[ManagedItem]:
        return list(self._items)

    def is_delivered(self, managed: ManagedItem) -> bool:
        return managed.delivered

    def is_spent(self, managed: ManagedItem) -> bool:
        return managed.spent

    def is_sent(self, managed: ManagedItem) -> bool:
        """In the file the game is being asked to read, but not applied yet."""
        return (self._sent_base != NOTHING_SENT
                and self._sent_base <= managed.index < self._sent_base + len(self._in_flight))

    def status(self, managed: ManagedItem) -> str:
        if self.is_spent(managed):
            return "Spent"
        if self.is_delivered(managed):
            return "Delivered"
        if self.is_sent(managed):
            return "Sent"
        return "Pending"

    def set_current_item_index(self, unlocked_items: list[Age2ItemData]) -> None:
        self._current_item = min(self._current_item, len(unlocked_items))

    def reset_delivery(self) -> None:
        """Pairs with MercenaryHandler.reset_used: the record is gone, so nothing is paid for."""
        for managed in self._items:
            managed.spent = False
        self._forget_sent()

    def sync_items(self, unlocked_items: list[Age2ItemData], applied: int,
                   spent: set[int]) -> set[int]:
        """One delivery pass.

        Returns the positions it paid out, for the caller to record. This never writes the
        record or tells the server itself, the way MercenaryHandler does not either.
        """
        self._sync_applied_items(applied, unlocked_items)
        self._sync_managed_items(unlocked_items, spent)
        delivered = self._report_delivered()
        if self._current_item < len(self._items):
            self._try_write_to_file()
        return delivered

    def try_flush_from_folder(self) -> None:
        """What was sent is gone from disk, so stop claiming it was sent.

        Without that, a scenario switch that leaves the item index where it was makes the next
        write look like one already made, and items.xsdat is deleted and never written again.
        """
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

    def _sync_managed_items(self, unlocked_items: list[Age2ItemData], spent: set[int]) -> None:
        """The received items, with the two facts the client knows about each one hung off it:
        whether the game has taken it, and whether the record has paid for it."""
        del self._items[len(unlocked_items):]
        for index, data in enumerate(unlocked_items):
            if index < len(self._items):
                managed = self._items[index]
                managed.data = data
            else:
                managed = ManagedItem(index, data)
                self._items.append(managed)
            managed.delivered = index < self._current_item
            managed.spent = index in spent

    def _report_delivered(self) -> set[int]:
        """One-shots the game has taken that the record has not paid for yet.

        Marked here as well as returned, so what is written below already skips them rather
        than sending them once more.
        """
        delivered = {managed.index for managed in self._items
                     if managed.delivered and managed.one_shot and not managed.spent}
        for index in delivered:
            self._items[index].spent = True
        return delivered

    def _id_for_game(self, managed: ManagedItem) -> int:
        return Items.SKIP_ITEM_ID if managed.spent else managed.data.id

    def _try_write_to_file(self) -> None:
        start = self._current_item
        window = self._items[start:start + Items.ITEM_WINDOW]
        item_ids = [self._id_for_game(managed) for managed in window]
        if start == self._sent_base and item_ids == self._in_flight:
            return
        try:
            with open(self._user_folder + "items.xsdat", "wb") as fp:
                XsdatFile.write_int(fp, start)
                for item_id in item_ids:
                    XsdatFile.write_int(fp, item_id)
        except Exception:
            # What is on disk is not what was meant to be there, so claim nothing.
            logger.exception("Could not write items.xsdat.")
            self._forget_sent()
            return
        self._in_flight = item_ids
        self._sent_base = start
