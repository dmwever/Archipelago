import asyncio
import os
import struct
import tempfile
import unittest
from unittest import mock

from BaseClasses import ItemClassification
from NetUtils import NetworkItem

from ..client.GameClient import AGE2_USER_PROFILE, Age2GameContext, DefaultClientInterface
from ..client.handlers.LocationHandler import CLASSIFICATION_FILE, PROGRESSION

A_TRAPPED_SPREAD = [10101, 10102, 10103, 10104, 10105, 10201, 10202, 10203, 10204, 10205,
                    10301, 10302, 10303, 10304, 10305, 10401, 10402, 10403, 10404, 10405]


def read_ints(path: str) -> list[int]:
    if not os.path.exists(path):
        return []
    with open(path, "rb") as fp:
        data = fp.read()
    return [struct.unpack("<i", data[i:i + 4])[0] for i in range(0, len(data), 4)]


def reply(flags_by_location: dict[int, ItemClassification]) -> dict[int, NetworkItem]:
    return {location: NetworkItem(4242, location, 1, int(flags))
            for location, flags in flags_by_location.items()}


class ScoutingInterface(DefaultClientInterface):
    def __init__(self) -> None:
        self.scouts = 0

    def scout_locations(self) -> None:
        self.scouts += 1


class ClassificationChannelTestBase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.profile = self._tmp.name + AGE2_USER_PROFILE
        os.makedirs(self.profile, exist_ok=True)
        self.interface = ScoutingInterface()
        self.ctx = Age2GameContext(self.interface)

    def connect(self, tag: str = "deadbeef") -> None:
        with mock.patch.object(Age2GameContext, "try_startup_game_connection",
                               lambda _self: False):
            self.ctx.connect(set(), {}, self._tmp.name, 1, tag, "Player")

    def scout(self, flags_by_location: dict[int, ItemClassification]) -> None:
        self.ctx.location_handler.try_sync_classification(reply(flags_by_location))

    def classification_file(self) -> list[int]:
        return read_ints(self.profile + CLASSIFICATION_FILE)


class TestConnectingAsksForTheScout(ClassificationChannelTestBase):
    def test_connecting_requests_one(self) -> None:
        self.connect()
        self.assertEqual(1, self.interface.scouts,
                         "the colours never arrive, because nothing ever asked the server")

    def test_a_client_that_has_not_connected_asks_for_nothing(self) -> None:
        self.ctx.update_game_user_folder(self._tmp.name)
        self.assertEqual(0, self.interface.scouts)

    def test_reconnecting_asks_again(self) -> None:
        self.connect()
        asyncio.run(self.ctx.disconnect())
        self.connect()
        self.assertEqual(2, self.interface.scouts)


class TestTheReplyLandsBesideTheOtherStartupFiles(ClassificationChannelTestBase):
    def test_the_profile_folder_gets_the_file(self) -> None:
        self.connect()
        self.scout({10101: ItemClassification.progression})
        self.assertEqual([10101, PROGRESSION], self.classification_file())

    def test_the_seed_reaches_the_disguise(self) -> None:
        self.connect()
        self.scout({location: ItemClassification.trap for location in A_TRAPPED_SPREAD})
        first = self.classification_file()

        asyncio.run(self.ctx.disconnect())
        self.connect("0ddba11d")
        self.scout({location: ItemClassification.trap for location in A_TRAPPED_SPREAD})

        self.assertNotEqual(first, self.classification_file(),
                            "the handler was never told this seed, so every seed traps alike")


class TestTheFileOutlivesAScenario(ClassificationChannelTestBase):
    def test_a_scenario_switch_leaves_the_colours_in_place(self) -> None:
        self.connect()
        self.scout({10101: ItemClassification.progression})

        self.ctx.flush_files()

        self.assertEqual([10101, PROGRESSION], self.classification_file(),
                         "a mid-session flush stripped the colour off every unchecked line")

    def test_a_disconnect_takes_them_with_it(self) -> None:
        self.connect()
        self.scout({10101: ItemClassification.progression})

        asyncio.run(self.ctx.disconnect())

        self.assertEqual([], self.classification_file(),
                         "the last seed's colours were left for the next one to read")


if __name__ == "__main__":
    unittest.main()
