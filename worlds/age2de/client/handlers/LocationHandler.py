import hashlib
import os

from BaseClasses import ItemClassification
from NetUtils import NetworkItem

from .FolderHandler import FolderHandler
from ...campaign import XsdatFile
from ...locations.connections.LocationMapping import location_id_to_name

CHECKED_FILE = "locations.xsdat"
CLASSIFICATION_FILE = "classification.xsdat"

PROGRESSION = 1
USEFUL = 2
FILLER = 3

DISGUISES = (PROGRESSION, USEFUL, FILLER)
DISGUISE_BYTES = 8


class LocationHandler(FolderHandler):
    _sending_locations: bool
    _written_location_count: int
    _tag: str

    def __init__(self):
        self._sending_locations = False
        self._written_location_count = 0
        self._tag = ''
        super().__init__()

    def set_tag(self, tag: str) -> None:
        self._tag = tag

    def send_locations(self) -> None:
        self._sending_locations = True

    def try_sync_checked_locations(self, checked_locations: set[int] | None) -> None:
        try:
            written = 0
            with open(self._user_folder + CHECKED_FILE, "wb") as fp:
                for location_id in checked_locations or ():
                    XsdatFile.write_int(fp, location_id)
                    written += 1
            self._written_location_count = written
        except Exception as ex:
            print(ex)

    def confirm_checked_locations(self, read_count: int) -> None:
        if read_count != self._written_location_count:
            self._sending_locations = True

    def are_locations_sending(self, sent_location_ids: list[int]) -> bool:
        return self._sending_locations or len(sent_location_ids) != 0

    def mark_locations_sent(self) -> None:
        self._sending_locations = False

    def try_flush_from_folder(self) -> None:
        self._written_location_count = 0
        try:
            if os.path.exists(self._user_folder + CHECKED_FILE):
                os.remove(self._user_folder + CHECKED_FILE)
        except Exception as ex:
            print(ex)

    def try_sync_classification(self, scouted: dict[int, NetworkItem]) -> None:
        try:
            with open(self._user_folder + CLASSIFICATION_FILE, "wb") as fp:
                for location_id in sorted(scouted):
                    if location_id not in location_id_to_name:
                        continue
                    XsdatFile.write_int(fp, location_id)
                    XsdatFile.write_int(
                        fp, self._class_of(location_id, scouted[location_id].flags))
        except Exception as ex:
            print(ex)

    def try_clear_classification(self) -> None:
        try:
            if os.path.exists(self._user_folder + CLASSIFICATION_FILE):
                os.remove(self._user_folder + CLASSIFICATION_FILE)
        except Exception as ex:
            print(ex)

    def _class_of(self, location_id: int, flags: int) -> int:
        if flags & ItemClassification.trap:
            return self._disguise(location_id)
        if flags & ItemClassification.progression:
            return PROGRESSION
        if flags & ItemClassification.useful:
            return USEFUL
        return FILLER

    def _disguise(self, location_id: int) -> int:
        digest = hashlib.sha256(f"{self._tag}:{location_id}".encode()).digest()
        return DISGUISES[int.from_bytes(digest[:DISGUISE_BYTES], "big") % len(DISGUISES)]
