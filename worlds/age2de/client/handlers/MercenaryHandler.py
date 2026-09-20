from dataclasses import dataclass
import io
import logging
import os

from .FolderHandler import FolderHandler

from ...campaign import XsdatFile
from ...items.Items import Age2ItemData

logger = logging.getLogger("Client")

SEAT_COUNT = 4
NO_SEAT = -1
EMPTY_SEAT = -1

@dataclass
class ManagedMercenary:
    data: Age2ItemData
    unlocked: bool = False
    used: bool = False
    seat: int = NO_SEAT

class MercenaryHandler(FolderHandler):
    _mercenaries: dict[Age2ItemData, ManagedMercenary]
    _seats: list[Age2ItemData]
    _queue: list[Age2ItemData]
    _queue_serial: int
    _queue_bytes: bytes

    def __init__(self, data: list[Age2ItemData]):
        self._mercenaries = {}
        for mercenary in data:
            self._mercenaries[mercenary] = ManagedMercenary(mercenary)
        self._seats = [None] * SEAT_COUNT
        self._queue = []
        self._queue_serial = 0
        self._queue_bytes = b""
        super().__init__()

    def use_mercenary(self, mercenary: Age2ItemData) -> None:
        self.set_used(mercenary, True)

    def set_used(self, mercenary: Age2ItemData, used: bool = True) -> None:
        if mercenary not in self._mercenaries:
            logger.warning("Mercenary data not found in this AP World's Mercenary Handler. "
                           "Could not use mercenary %s.", mercenary.name)
            return
        managed = self._mercenaries[mercenary]
        managed.used = used
        if not used:
            return
        if managed.seat != NO_SEAT:
            self._seats[managed.seat] = None
            managed.seat = NO_SEAT
        if mercenary in self._queue:
            self._queue.remove(mercenary)

    def is_used(self, mercenary: Age2ItemData) -> bool:
        if mercenary not in self._mercenaries:
            return False
        return self._mercenaries[mercenary].used

    def is_unlocked(self, mercenary: Age2ItemData) -> bool:
        if mercenary not in self._mercenaries:
            return False
        return self._mercenaries[mercenary].unlocked

    def in_seat(self, mercenary: Age2ItemData) -> bool:
        if mercenary not in self._mercenaries:
            return False
        return self._mercenaries[mercenary].seat != NO_SEAT

    def status(self, mercenary: Age2ItemData) -> str:
        if self.is_used(mercenary):
            return "Used"
        if self.in_seat(mercenary):
            return "In-Pavilion"
        if self.is_unlocked(mercenary):
            return "Unlocked"
        return "Missing"

    def queue_serial(self) -> int:
        return self._queue_serial

    def seated(self) -> list[Age2ItemData]:
        return list(self._seats)

    def queued(self) -> list[Age2ItemData]:
        return list(self._queue)

    def try_sync_mercenaries(self, unlocked_items: list[Age2ItemData]) -> None:
        try:
            self._enqueue_unlocked(unlocked_items)
            self._fill_seats()
            self._write_queue()
            self._write_used()
        except Exception:
            logger.exception("Could not sync mercenaries.")

    def try_flush_from_folder(self) -> None:
        for name in ("mercenary_queue.xsdat", "mercenaries.xsdat"):
            try:
                if os.path.exists(self._user_folder + name):
                    os.remove(self._user_folder + name)
            except Exception as ex:
                print(ex)

    def _enqueue_unlocked(self, unlocked_items: list[Age2ItemData]) -> None:
        for item in unlocked_items:
            if item not in self._mercenaries:
                continue
            managed = self._mercenaries[item]
            managed.unlocked = True
            if managed.used or managed.seat != NO_SEAT or item in self._queue:
                continue
            self._queue.append(item)

    def _fill_seats(self) -> None:
        for seat in range(SEAT_COUNT):
            if self._seats[seat] is not None:
                continue
            if not self._queue:
                return
            mercenary = self._queue.pop(0)
            self._seats[seat] = mercenary
            self._mercenaries[mercenary].seat = seat

    def _write_queue(self) -> None:
        body = io.BytesIO()
        for mercenary in self._seats:
            if mercenary is None:
                XsdatFile.write_int(body, EMPTY_SEAT)
                XsdatFile.write_int(body, EMPTY_SEAT)
                XsdatFile.write_int(body, EMPTY_SEAT)
                XsdatFile.write_int(body, 0)
                continue
            data = mercenary.type
            XsdatFile.write_int(body, mercenary.id)
            XsdatFile.write_int(body, data.name_string_id)
            XsdatFile.write_int(body, data.icon_id)
            XsdatFile.write_int(body, data.unit_count)
            for unit_id in data.unit_ids:
                XsdatFile.write_int(body, unit_id)

        seats = body.getvalue()
        if seats != self._queue_bytes:
            self._queue_bytes = seats
            self._queue_serial = self._queue_serial + 1

        with open(self._user_folder + "mercenary_queue.xsdat", "wb") as fp:
            XsdatFile.write_int(fp, self._queue_serial)
            fp.write(seats)

    def _write_used(self) -> None:
        with open(self._user_folder + "mercenaries.xsdat", "wb") as fp:
            for mercenary, managed in self._mercenaries.items():
                if managed.used:
                    XsdatFile.write_int(fp, mercenary.id)
