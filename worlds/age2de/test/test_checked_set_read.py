"""The game learns the checked set when a scenario starts, not only after a new check.

AP.xs reads locations.xsdat only when the ping's Free Locations flag is set, and the client set
that flag only while the game had just sent location ids. A scenario entered with nothing new to
report therefore never read the file, so a location checked hours ago in an earlier scenario
looked untouched until the next check landed.

One armed ping is not enough to fix that. MarkServerLocations ends in xsDisableSelf and every
scenario starts a fresh XS context, so the read has to be asked for once per scenario rather than
once per connect. ConnectAP does not enable ReadAP until it has approved the first ping, so the
flag in that ping goes into a file nothing is reading yet. The game therefore reports the size of
its last read back in the packet, and the client keeps asking while that disagrees with the set it
is writing.
"""

import asyncio
import os
import struct
import tempfile
import unittest
from unittest import mock

from ..client.GameClient import AGE2_USER_PROFILE, Age2GameContext, DefaultClientInterface
from ..client.handlers.CampaignHandler import ActiveFile
from ..locations.Campaigns import Age2CampaignData
from ..locations.Scenarios import CAMPAIGN_TO_SCENARIOS

FREE_LOCATIONS_FIELD = 8


def read_ints(path: str) -> list[int]:
    if not os.path.exists(path):
        return []
    with open(path, "rb") as fp:
        data = fp.read()
    return [struct.unpack("<i", data[i:i + 4])[0] for i in range(0, len(data), 4)]


class FakeGame:
    """MarkServerLocations and the ConnectAP gate in front of it, as AP.xs runs them."""

    def __init__(self) -> None:
        self.checked_locations_count = 0
        self.reads = 0
        self.reading_pings = True

    def read_ping(self, folder: str, asked: bool) -> None:
        if not self.reading_pings or not asked:
            return
        self.reads += 1
        self.checked_locations_count = len(read_ints(folder + "locations.xsdat"))


class CheckedSetReadTestBase(unittest.TestCase):
    EARLIER_CHECK = 10101

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        os.makedirs(self._tmp.name + AGE2_USER_PROFILE, exist_ok=True)
        self.ctx = Age2GameContext(DefaultClientInterface())
        self.game = FakeGame()

    def connect(self, checked: set[int] | None = None) -> None:
        with mock.patch.object(Age2GameContext, "try_startup_game_connection",
                               lambda _self: False):
            self.ctx.connect({self.EARLIER_CHECK} if checked is None else checked, {},
                             self._tmp.name, 1, "deadbeef", "Player")
        self.enter_scenario()

    def enter_scenario(self) -> None:
        handler = self.ctx.campaign_handler
        first = CAMPAIGN_TO_SCENARIOS[Age2CampaignData.ATTILA][0]
        handler.active_file = ActiveFile(scn=handler.scenarios[first],
                                         read_file_name="whatever.xsdat")

    def game_sent(self, *location_ids: int) -> None:
        self.ctx.current_packet.location_ids = list(location_ids)

    def sync_checked_locations(self) -> None:
        self.ctx.location_handler.try_sync_checked_locations(
            self.ctx.client_status.checked_locations)

    def ping_asks(self) -> bool:
        self.ctx.ping_game()
        with open(self.ctx.profile_folder() + "AP.xsdat", "rb") as fp:
            data = fp.read()
        offset = FREE_LOCATIONS_FIELD * 4
        return struct.unpack("<?xxx", data[offset:offset + 4])[0]

    def tick(self) -> bool:
        """The checked-set phase of status_tick, in the order status_tick runs it."""
        self.sync_checked_locations()
        self.ctx.location_handler.confirm_checked_locations(self.game.checked_locations_count)
        asked = self.ping_asks()
        self.game.read_ping(self.ctx.profile_folder(), asked)
        return asked

    def settle(self, limit: int = 10) -> int:
        for ticks in range(1, limit + 1):
            if not self.tick():
                return ticks
        self.fail("the client never stopped asking for the checked set")


class TestConnectingArmsTheRead(CheckedSetReadTestBase):
    def test_the_first_ping_after_connecting_asks_although_the_game_sent_nothing(self) -> None:
        self.connect()
        self.assertEqual([], self.ctx.current_packet.location_ids)
        self.assertTrue(self.tick(),
                        "a scenario entered cold is never told to read locations.xsdat")

    def test_a_client_that_has_not_connected_does_not_ask(self) -> None:
        self.ctx.update_game_user_folder(self._tmp.name)
        self.enter_scenario()
        self.assertFalse(self.ping_asks(),
                         "the read was armed by construction rather than by connecting")


class TestTheGameLearnsTheCheckedSet(CheckedSetReadTestBase):
    def test_one_read_takes_in_everything_checked_before_the_scenario(self) -> None:
        self.connect({10101, 10102, 10305})
        self.settle()
        self.assertEqual(1, self.game.reads)
        self.assertEqual(3, self.game.checked_locations_count,
                         "the game acked a set that is not the one the client wrote")

    def test_a_settled_session_stops_asking(self) -> None:
        self.connect()
        self.settle()
        self.assertEqual([False] * 5, [self.tick() for _ in range(5)],
                         "the feature added per-tick work for the rest of the scenario")
        self.assertEqual(1, self.game.reads)


class TestTheClientWaitsForTheGameToListen(CheckedSetReadTestBase):
    """ConnectAP approves the first ping before enabling ReadAP, so that ping is read for
    validation but never for its flags."""

    def test_the_arm_is_not_spent_on_a_ping_nothing_reads(self) -> None:
        self.connect()
        self.game.reading_pings = False
        self.assertEqual([True, True], [self.tick() for _ in range(2)])
        self.assertEqual(0, self.game.reads)

        self.game.reading_pings = True
        self.assertTrue(self.tick(), "the arm was spent on pings the game never read")
        self.assertEqual(1, self.game.reads)
        self.assertFalse(self.tick())


class TestANewScenarioAsksAgain(CheckedSetReadTestBase):
    def test_entering_the_next_scenario_reads_the_checked_set_without_a_reconnect(self) -> None:
        self.connect()
        self.settle()

        self.game = FakeGame()
        self.enter_scenario()

        self.assertTrue(self.tick(),
                        "a fresh XS context starts with MarkServerLocations disabled and unasked")
        self.assertEqual(1, self.game.reads)
        self.assertEqual(1, self.game.checked_locations_count)


class TestReconnectingArmsItAgain(CheckedSetReadTestBase):
    def test_a_reconnect_asks_on_its_own_first_ping(self) -> None:
        self.connect()
        self.settle()
        self.assertFalse(self.tick())

        asyncio.run(self.ctx.disconnect())
        self.connect()

        self.assertTrue(self.tick(),
                        "a reconnected client left the game on a stale checked set")


class TestANewCheckStillAsks(CheckedSetReadTestBase):
    def test_a_location_the_game_just_sent_is_offered_back(self) -> None:
        self.connect()
        self.settle()

        self.ctx.client_status.checked_locations.add(10102)
        self.game_sent(10102)

        self.assertTrue(self.tick())
        self.assertEqual(2, self.game.checked_locations_count)


class TestAnEarlierScenariosChecksReachTheNextOne(CheckedSetReadTestBase):
    def test_a_check_from_an_earlier_scenario_is_written_and_read(self) -> None:
        self.connect({self.EARLIER_CHECK})
        self.sync_checked_locations()

        self.assertEqual([self.EARLIER_CHECK],
                         read_ints(self.ctx.profile_folder() + "locations.xsdat"))
        self.assertEqual([], self.ctx.current_packet.location_ids)

        self.settle()
        self.assertEqual(1, self.game.checked_locations_count,
                         "the game never took in the check from the earlier scenario")


if __name__ == "__main__":
    unittest.main()
