import os
import tempfile
import unittest
from pathlib import Path

from BaseClasses import ItemClassification
from NetUtils import NetworkItem

from ..client.handlers.LocationHandler import (CHECKED_FILE, CLASSIFICATION_FILE, FILLER,
                                               LocationHandler, PROGRESSION, USEFUL)

NOTHING_SENT: list[int] = []
SEED_TAG = "deadbeef"
RECEIVING_PLAYER = 1
SOME_ITEM = 4242


def scouted(flags_by_location: dict[int, ItemClassification]) -> dict[int, NetworkItem]:
    return {location: NetworkItem(SOME_ITEM, location, RECEIVING_PLAYER, int(flags))
            for location, flags in flags_by_location.items()}


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
        self.handler.set_tag(SEED_TAG)

    def checked_file(self) -> list[int]:
        return read_ids(self.folder, CHECKED_FILE)

    def classification_file(self) -> list[int]:
        return read_ids(self.folder, CLASSIFICATION_FILE)


class TestTheScoutedClassesAreWritten(LocationHandlerTestBase):
    def test_it_writes_a_class_beside_each_scouted_location(self):
        self.handler.try_sync_classification(scouted({
            10101: ItemClassification.progression,
            10102: ItemClassification.useful,
            10305: ItemClassification.filler,
        }))
        self.assertEqual([10101, PROGRESSION, 10102, USEFUL, 10305, FILLER],
                         self.classification_file())

    def test_an_especially_useful_progression_item_reads_as_progression(self):
        self.handler.try_sync_classification(scouted({
            10101: ItemClassification.progression | ItemClassification.useful,
        }))
        self.assertEqual([10101, PROGRESSION], self.classification_file())


class TestTheReplyIsTheRecordOfWhatThisSeedHas(LocationHandlerTestBase):
    def test_a_location_the_server_did_not_report_is_absent_rather_than_defaulted(self):
        self.handler.try_sync_classification(scouted({
            10101: ItemClassification.progression,
            10305: ItemClassification.useful,
        }))
        self.assertNotIn(10102, self.classification_file()[0::2],
                         "a location this seed never made was written with a default class, so "
                         "the game will decorate something Archipelago does not own")

    def test_an_empty_reply_writes_an_empty_file(self):
        self.handler.try_sync_classification({})
        self.assertEqual([], self.classification_file())

    def test_a_location_this_apworld_does_not_know_is_left_out(self):
        self.handler.try_sync_classification(scouted({
            10101: ItemClassification.progression,
            99999999: ItemClassification.progression,
        }))
        self.assertEqual([10101, PROGRESSION], self.classification_file(),
                         "an id this client cannot name was written for the game to look up")

    def test_a_second_scout_replaces_the_first(self):
        self.handler.try_sync_classification(scouted({
            10101: ItemClassification.progression,
            10102: ItemClassification.useful,
        }))
        self.handler.try_sync_classification(scouted({10102: ItemClassification.useful}))
        self.assertEqual([10102, USEFUL], self.classification_file())


class TestATrapIsDisguised(LocationHandlerTestBase):
    SPREAD = [10101, 10102, 10103, 10104, 10105, 10201, 10202, 10203, 10204, 10205,
              10301, 10302, 10303, 10304, 10305, 10401, 10402, 10403, 10404, 10405]

    def disguises(self, *location_ids: int) -> list[int]:
        self.handler.try_sync_classification(
            scouted({location: ItemClassification.trap for location in location_ids}))
        return self.classification_file()[1::2]

    def test_a_trap_wears_an_ordinary_class(self):
        self.assertTrue(all(disguise in (PROGRESSION, USEFUL, FILLER)
                            for disguise in self.disguises(*self.SPREAD)),
                        "a trap was written as something no genuine item wears")

    def test_the_disguise_does_not_move_between_scouts(self):
        first = self.disguises(*self.SPREAD)
        self.assertEqual(first, self.disguises(*self.SPREAD))

    def test_a_fresh_handler_disguises_a_trap_the_same_way(self):
        first = self.disguises(*self.SPREAD)

        self.handler = LocationHandler()
        self.handler.set_user_folder(self.folder)
        self.handler.set_tag(SEED_TAG)

        self.assertEqual(first, self.disguises(*self.SPREAD),
                         "a reconnect repainted the traps, which identifies every one of them")

    def test_the_disguise_is_pinned_so_another_session_reads_it_the_same(self):
        self.assertEqual([USEFUL, FILLER, PROGRESSION],
                         self.disguises(10101, 10105, 10201),
                         "the disguise moved between runs; a per-process hash cannot carry it")

    def test_another_seed_disguises_the_same_location_differently(self):
        first = self.disguises(*self.SPREAD)

        self.handler.set_tag("0ddba11d")

        self.assertNotEqual(first, self.disguises(*self.SPREAD),
                            "the disguise ignores the seed, so one seed's trap map fits them all")

    def test_a_trap_is_spread_across_all_three_classes(self):
        self.assertEqual({PROGRESSION, USEFUL, FILLER}, set(self.disguises(*self.SPREAD)),
                         "the disguise collapses onto fewer than three colours")


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

    def test_a_flush_leaves_the_scouted_classes_alone(self):
        self.handler.try_sync_classification(scouted({10101: ItemClassification.progression}))

        self.handler.try_flush_from_folder()

        self.assertEqual([10101, PROGRESSION], self.classification_file(),
                         "a scout-once file was cleared by a mid-scenario flush that cannot rewrite it")

    def test_disconnecting_clears_the_scouted_classes(self):
        self.handler.try_sync_classification(scouted({10101: ItemClassification.progression}))

        self.handler.try_clear_classification()

        self.assertFalse(os.path.exists(self.folder + CLASSIFICATION_FILE),
                         "the last seed's colours were left in the profile folder")

    def test_clearing_an_empty_folder_is_quiet(self):
        self.handler.try_clear_classification()

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
