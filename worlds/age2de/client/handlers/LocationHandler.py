import os

from .FolderHandler import FolderHandler
from ...campaign import XsdatFile

CHECKED_FILE = "locations.xsdat"


class LocationHandler(FolderHandler):
    _sending_locations: bool
    _written_location_count: int

    def __init__(self):
        self._sending_locations = False
        self._written_location_count = 0
        super().__init__()

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
