"""A scenario the player has not unlocked says so in game, instead of waiting for a client forever.

The client refuses to bind to a scenario that is Missing or Campaign Locked, so it never wrote
AP.xsdat for it, and ConnectAP printed "Waiting for Client Connection" every second with nothing
coming. While it refuses, the client now writes the negated scenario id as AP.xsdat's first int.
ConnectAP reads that first int through CheckScenario's open, and shows "Scenario not Unlocked"
instead. A positive id keeps the packet's normal meaning.
"""

import asyncio
import os
import pathlib
import struct
import tempfile
import unittest
from unittest import mock

from ..campaign import XsdatFile
from ..client import GameClient
from ..client.GameClient import AGE2_USER_PROFILE, AP_WORLD_VERSION, Age2GameContext, \
    DefaultClientInterface
from ..generation import Identity
from ..items.Items import Age2ItemData
from ..locations.Scenarios import Age2ScenarioData

SLOT = 1
TAG = "deadbeef"
PLAYER = "Player"


class TestTheClientRefusesALockedScenario(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        os.makedirs(self._tmp.name + AGE2_USER_PROFILE, exist_ok=True)
        self.ctx = Age2GameContext(DefaultClientInterface())
        with mock.patch.object(Age2GameContext, "try_startup_game_connection",
                               lambda _self: False):
            self.ctx.connect(set(), {}, self._tmp.name, SLOT, TAG, PLAYER)
        self.ping = 0

    def unlock(self, *items: Age2ItemData) -> None:
        self.ctx.client_status.unlocked_items = list(items)

    def game_runs(self, scenario: Age2ScenarioData) -> None:
        """One AP_Write from the running scenario, field for field."""
        self.ping += 1
        name = Identity.campaign_xsdat_name(scenario.campaign.file_stem, TAG, PLAYER)
        with open(self.ctx.profile_folder() + name, "wb") as fp:
            XsdatFile.write_int(fp, 1)                       # active
            XsdatFile.write_int(fp, self.ping)               # game time
            XsdatFile.write_int(fp, AP_WORLD_VERSION.major)
            XsdatFile.write_int(fp, SLOT)
            XsdatFile.write_int(fp, -1)                      # last message id
            for _ in range(12):
                XsdatFile.write_int(fp, -1)
            XsdatFile.write_int(fp, 0)                       # completed
            XsdatFile.write_int(fp, scenario.id)
            XsdatFile.write_int(fp, AP_WORLD_VERSION.minor)
            XsdatFile.write_int(fp, -1)                      # pending mercenary
            XsdatFile.write_int(fp, -1)                      # consumed queue serial
            XsdatFile.write_int(fp, 0)                       # applied item count
            XsdatFile.write_int(fp, 0)                       # checked locations count
            XsdatFile.write_int(fp, 0)                       # location ids that follow
            for i in range(24):
                XsdatFile.write_int(fp, i)

    def tick(self) -> None:
        async def no_sleep() -> None:
            return None

        with mock.patch.object(GameClient, "long_sleep", no_sleep), \
             mock.patch.object(GameClient, "short_sleep", no_sleep):
            asyncio.run(GameClient.status_tick(self.ctx))

    def first_int_of_ap_xsdat(self) -> int | None:
        path = self.ctx.profile_folder() + "AP.xsdat"
        if not os.path.exists(path):
            return None
        with open(path, "rb") as fp:
            return struct.unpack("<i", fp.read(4))[0]

    def status(self, scenario: Age2ScenarioData) -> str:
        self.ctx.campaign_handler.sync_unlocked(self.ctx.client_status.unlocked_items)
        return self.ctx.campaign_handler.status(scenario)

    def test_a_missing_scenario_gets_its_negated_id(self) -> None:
        self.unlock(Age2ItemData.JOAN_OF_ARC)
        self.assertEqual("Missing", self.status(Age2ScenarioData.AP_JOAN_3))

        self.game_runs(Age2ScenarioData.AP_JOAN_3)
        self.tick()

        self.assertEqual(-Age2ScenarioData.AP_JOAN_3.id, self.first_int_of_ap_xsdat())
        self.assertFalse(self.ctx.campaign_handler.has_active_scenario())

    def test_a_campaign_locked_scenario_gets_its_negated_id(self) -> None:
        self.unlock(Age2ItemData.PROGRESSIVE_JOAN_SCENARIO, Age2ItemData.PROGRESSIVE_JOAN_SCENARIO)
        self.assertEqual("Campaign Locked", self.status(Age2ScenarioData.AP_JOAN_3))

        self.game_runs(Age2ScenarioData.AP_JOAN_3)
        self.tick()

        self.assertEqual(-Age2ScenarioData.AP_JOAN_3.id, self.first_int_of_ap_xsdat())
        self.assertFalse(self.ctx.campaign_handler.has_active_scenario())

    def test_an_available_scenario_gets_its_own_id(self) -> None:
        self.unlock(Age2ItemData.JOAN_OF_ARC)
        self.assertEqual("Available", self.status(Age2ScenarioData.AP_JOAN_1))

        self.game_runs(Age2ScenarioData.AP_JOAN_1)
        self.tick()

        self.assertEqual(Age2ScenarioData.AP_JOAN_1.id, self.first_int_of_ap_xsdat())

    def test_the_refusal_writes_nothing_else(self) -> None:
        self.unlock(Age2ItemData.JOAN_OF_ARC)
        self.game_runs(Age2ScenarioData.AP_JOAN_3)
        self.tick()

        self.assertEqual(4, os.path.getsize(self.ctx.profile_folder() + "AP.xsdat"))

    def test_unlocking_mid_wait_connects(self) -> None:
        self.unlock(Age2ItemData.JOAN_OF_ARC)
        self.game_runs(Age2ScenarioData.AP_JOAN_3)
        self.tick()
        self.assertEqual(-Age2ScenarioData.AP_JOAN_3.id, self.first_int_of_ap_xsdat())

        self.unlock(Age2ItemData.JOAN_OF_ARC, Age2ItemData.PROGRESSIVE_JOAN_SCENARIO,
                    Age2ItemData.PROGRESSIVE_JOAN_SCENARIO)
        self.game_runs(Age2ScenarioData.AP_JOAN_3)
        self.tick()

        self.assertEqual(Age2ScenarioData.AP_JOAN_3.id, self.first_int_of_ap_xsdat())
        self.assertTrue(self.ctx.campaign_handler.has_active_scenario())


AGEIPELAGO = os.environ.get("AGEIPELAGO_PATH")
AP_XS = pathlib.Path(AGEIPELAGO or ".", "age 2 files", "resources", "_common", "xs", "AP.xs")


@unittest.skipUnless(AGEIPELAGO, "AGEIPELAGO_PATH is not set")
class TestTheGameReadsTheRefusal(unittest.TestCase):
    """The client's -id means nothing unless ConnectAP compares against the same encoding."""

    def connect_ap(self) -> str:
        source = AP_XS.read_text(encoding="utf-8")
        start = source.index("rule ConnectAP")
        return source[start:source.index("\n}", start)]

    def test_connect_ap_matches_the_negated_id(self) -> None:
        self.assertRegex(self.connect_ap(), r"==\s*0\s*-\s*scenarioId")

    def test_connect_ap_says_scenario_not_unlocked(self) -> None:
        self.assertIn('"<RED>Scenario not Unlocked"', self.connect_ap())


if __name__ == "__main__":
    unittest.main()
