import os
import tempfile
import unittest
from pathlib import Path

from ..client.handlers.LocationHandler import CHECKED_FILE, LocationHandler

NOTHING_SENT: list[int] = []


def read_ids(folder: str, name: str) -> list[int]:
    path = Path(folder) / name
    if not path.exists():
        return []
    raw = path.read_bytes()
    return [int.from_bytes(raw[i:i + 4], "little", signed=True) for i in range(0, len(raw), 4)]


class LocationHandlerTestBase(unittest.TestCase):
    def setUp(self) -> None:
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.folder = folder.name + "/"
        self.handler = LocationHandler()
        self.handler.set_user_folder(self.folder)

    def checked_file(self) -> list[int]:
        return read_ids(self.folder, CHECKED_FILE)


class TestTheCheckedLocationsAreWritten(LocationHandlerTestBase):
    def test_it_writes_the_checked_locations_it_was_handed(self):
        self.handler.try_sync_checked_locations({10101, 10102, 10305})
        self.assertEqual([10101, 10102, 10305], sorted(self.checked_file()))

    def test_it_writes_nothing_when_nothing_is_checked(self):
        self.handler.try_sync_checked_locations(set())
        self.assertEqual([], self.checked_file())

    def test_an_unconnected_client_has_no_checked_locations_to_write(self):
        self.handler.try_sync_checked_locations(None)
        self.assertEqual([], self.checked_file())

    def test_a_dropped_check_leaves_nothing_behind(self):
        self.handler.try_sync_checked_locations({10101, 10102})
        self.handler.try_sync_checked_locations({10101})
        self.assertEqual([10101], self.checked_file())


class TestAskingForTheRead(LocationHandlerTestBase):
    def test_a_fresh_handler_does_not_ask(self):
        self.assertFalse(self.handler.are_locations_sending(NOTHING_SENT),
                         "the read was armed by construction rather than by connecting")

    def test_sending_locations_asks_until_the_ping_is_written(self):
        self.handler.send_locations()
        self.assertTrue(self.handler.are_locations_sending(NOTHING_SENT))
        self.handler.mark_locations_sent()
        self.assertFalse(self.handler.are_locations_sending(NOTHING_SENT))

    def test_a_location_the_game_just_sent_asks_on_its_own(self):
        self.assertTrue(self.handler.are_locations_sending([10102]))


class TestTheGameAcksTheRead(LocationHandlerTestBase):
    def test_a_count_that_disagrees_arms_the_read_again(self):
        self.handler.try_sync_checked_locations({10101, 10102})
        self.handler.mark_locations_sent()
        self.handler.confirm_checked_locations(0)
        self.assertTrue(self.handler.are_locations_sending(NOTHING_SENT))

    def test_a_count_that_agrees_leaves_the_read_unasked(self):
        self.handler.try_sync_checked_locations({10101, 10102})
        self.handler.mark_locations_sent()
        self.handler.confirm_checked_locations(2)
        self.assertFalse(self.handler.are_locations_sending(NOTHING_SENT))

    def test_the_ack_is_against_the_locations_that_were_written(self):
        self.handler.try_sync_checked_locations({10101, 10102})
        self.handler.mark_locations_sent()
        self.handler.confirm_checked_locations(2)
        self.handler.try_sync_checked_locations({10101, 10102, 10305})
        self.handler.confirm_checked_locations(2)
        self.assertTrue(self.handler.are_locations_sending(NOTHING_SENT),
                        "a new check went unread because the game's old ack still agreed")


class TestFlushing(LocationHandlerTestBase):
    def test_a_flush_clears_the_checked_file(self):
        self.handler.try_sync_checked_locations({10101})
        self.handler.try_flush_from_folder()
        self.assertFalse(os.path.exists(self.folder + CHECKED_FILE))

    def test_a_flush_leaves_a_file_the_handler_does_not_write(self):
        scouted = Path(self.folder + "classification.xsdat")
        scouted.write_bytes(b"\x01\x00\x00\x00")

        self.handler.try_flush_from_folder()

        self.assertTrue(scouted.exists(),
                        "a scout-once file was cleared by a mid-scenario flush that cannot rewrite it")

    def test_a_flush_forgets_what_the_game_was_told(self):
        self.handler.try_sync_checked_locations({10101})
        self.handler.mark_locations_sent()
        self.handler.try_flush_from_folder()
        self.handler.confirm_checked_locations(1)
        self.assertTrue(self.handler.are_locations_sending(NOTHING_SENT),
                        "a flushed file was still credited to the game as read")

    def test_flushing_an_empty_folder_is_quiet(self):
        self.handler.try_flush_from_folder()


if __name__ == "__main__":
    unittest.main()
