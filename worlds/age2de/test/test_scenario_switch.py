"""Following the scenario the engine is actually writing.

A scenario the player has left keeps its leading active byte until something deactivates it, so
during a save/load switch two files claim to be live at once and `find_active_campaign` can latch
onto the one that was abandoned. `find_live_scenario` ignores the claim and watches the ping
instead: only the file the engine is still writing has one that moves.

Seeing movement needs two scans, so every test here scans twice. That is the mechanism, not an
accident of the fixtures -- the first scan has nothing to compare against.
"""

import os
import tempfile
import unittest

from ..campaign import XsdatFile
from ..generation import Identity
from ..client.handlers.CampaignHandler import CampaignHandler
from ..items.Items import Age2ItemData
from ..locations.Campaigns import Age2CampaignData
from ..locations.Scenarios import Age2ScenarioData

JOAN_CAMPAIGN = Age2ItemData.JOAN_OF_ARC
ATTILA_CAMPAIGN = Age2ItemData.ATTILA_THE_HUN

TAG = Identity.seed_tag("56761350679959987564", 3)
PLAYER = "Dave"


class TestFindLiveScenario(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.folder = self._tmp.name + os.sep
        self.handler = CampaignHandler([campaign for campaign in Age2CampaignData])
        self.handler.set_user_folder(self.folder)
        self.handler.set_tag(TAG)
        self.handler.set_player_name(PLAYER)
        self.handler.sync_unlocked([JOAN_CAMPAIGN, ATTILA_CAMPAIGN])

    def packet_name(self, campaign: Age2CampaignData) -> str:
        return Identity.campaign_xsdat_name(campaign.file_stem, TAG, PLAYER)

    def write_packet(self, campaign: Age2CampaignData, scenario_id: int, ping: int,
                     active: bool = True) -> None:
        """The leading 19 ints of AP_Write, which is all the ping scan reads."""
        with open(self.folder + self.packet_name(campaign), "wb") as fp:
            XsdatFile.write_bool(fp, active)
            XsdatFile.write_int(fp, ping)
            for _ in range(16):
                XsdatFile.write_int(fp, 0)
            XsdatFile.write_int(fp, scenario_id)

    def active_scenario(self) -> Age2ScenarioData:
        return self.handler.active_file.current_scenario.data

    def test_the_first_scan_records_and_follows_nothing(self) -> None:
        self.write_packet(Age2CampaignData.JOAN, Age2ScenarioData.AP_JOAN_1.id, ping=5)

        self.assertFalse(self.handler.find_live_scenario(),
                         "with nothing to compare against, a ping cannot have moved yet")
        self.assertIsNone(self.handler.active_file)

    def test_a_moving_ping_is_followed(self) -> None:
        self.write_packet(Age2CampaignData.JOAN, Age2ScenarioData.AP_JOAN_1.id, ping=5)
        self.handler.find_live_scenario()

        self.write_packet(Age2CampaignData.JOAN, Age2ScenarioData.AP_JOAN_1.id, ping=6)

        self.assertTrue(self.handler.find_live_scenario())
        self.assertEqual(Age2ScenarioData.AP_JOAN_1, self.active_scenario())

    def test_an_active_file_with_a_static_ping_is_left_alone(self) -> None:
        """The abandoned scenario in a save/load switch. Still flagged active, no longer written."""
        self.write_packet(Age2CampaignData.JOAN, Age2ScenarioData.AP_JOAN_1.id, ping=5)
        self.handler.find_live_scenario()

        self.assertFalse(self.handler.find_live_scenario())
        self.assertIsNone(self.handler.active_file)

    def test_a_ping_that_moved_backwards_still_counts_as_movement(self) -> None:
        """The ping is game time, which restarts per scenario, so a reloaded save reports less."""
        self.write_packet(Age2CampaignData.JOAN, Age2ScenarioData.AP_JOAN_1.id, ping=900)
        self.handler.find_live_scenario()

        self.write_packet(Age2CampaignData.JOAN, Age2ScenarioData.AP_JOAN_1.id, ping=12)

        self.assertTrue(self.handler.find_live_scenario())

    def test_an_inactive_file_is_ignored_however_its_ping_moves(self) -> None:
        self.write_packet(Age2CampaignData.JOAN, Age2ScenarioData.AP_JOAN_1.id, ping=5,
                          active=False)
        self.handler.find_live_scenario()

        self.write_packet(Age2CampaignData.JOAN, Age2ScenarioData.AP_JOAN_1.id, ping=6,
                          active=False)

        self.assertFalse(self.handler.find_live_scenario())

    def test_a_deactivated_four_byte_file_is_ignored(self) -> None:
        """deactivate_scenario truncates to a single bool, so the scan short-reads it."""
        self.write_packet(Age2CampaignData.JOAN, Age2ScenarioData.AP_JOAN_1.id, ping=5)
        self.handler.find_live_scenario()

        with open(self.folder + self.packet_name(Age2CampaignData.JOAN), "wb") as fp:
            XsdatFile.write_bool(fp, False)

        self.assertFalse(self.handler.find_live_scenario())

    def test_the_file_already_being_followed_is_not_refollowed(self) -> None:
        """A live current scenario is not a switch, so the caller gets no reason to flush."""
        joan = Age2CampaignData.JOAN
        self.write_packet(joan, Age2ScenarioData.AP_JOAN_1.id, ping=5)
        self.handler.find_live_scenario()
        self.write_packet(joan, Age2ScenarioData.AP_JOAN_1.id, ping=6)
        self.handler.find_live_scenario()

        self.write_packet(joan, Age2ScenarioData.AP_JOAN_1.id, ping=7)

        self.assertFalse(self.handler.find_live_scenario())
        self.assertEqual(Age2ScenarioData.AP_JOAN_1, self.active_scenario())

    def test_a_switch_follows_the_live_file_and_deactivates_the_one_left_behind(self) -> None:
        joan = Age2CampaignData.JOAN
        attila = Age2CampaignData.ATTILA
        self.write_packet(joan, Age2ScenarioData.AP_JOAN_1.id, ping=5)
        self.write_packet(attila, Age2ScenarioData.AP_ATTILA_1.id, ping=100)
        self.handler.find_live_scenario()
        self.write_packet(joan, Age2ScenarioData.AP_JOAN_1.id, ping=6)
        self.handler.find_live_scenario()
        self.assertEqual(Age2ScenarioData.AP_JOAN_1, self.active_scenario())

        # Joan goes quiet, Attila starts being written: the save/load switch.
        self.write_packet(attila, Age2ScenarioData.AP_ATTILA_1.id, ping=101)
        self.handler.find_live_scenario()
        self.write_packet(attila, Age2ScenarioData.AP_ATTILA_1.id, ping=102)

        self.assertTrue(self.handler.find_live_scenario())
        self.assertEqual(Age2ScenarioData.AP_ATTILA_1, self.active_scenario())
        self.assertEqual(4, os.path.getsize(self.folder + self.packet_name(joan)),
                         "the abandoned file should have been deactivated, not left claiming to "
                         "be live for find_active_campaign to pick up later")

    def test_growth_while_we_were_not_scanning_is_not_read_as_movement(self) -> None:
        """The scan only runs while the packet repeats, so recorded pings go stale between bouts.

        Attila grows from 100 to 900 while we are following Joan and not scanning at all. When Joan
        goes quiet, the first scan of the new bout must not read that gap as Attila running now.
        """
        joan = Age2CampaignData.JOAN
        attila = Age2CampaignData.ATTILA
        self.write_packet(joan, Age2ScenarioData.AP_JOAN_1.id, ping=5)
        self.write_packet(attila, Age2ScenarioData.AP_ATTILA_1.id, ping=100)
        self.handler.find_live_scenario()
        self.write_packet(joan, Age2ScenarioData.AP_JOAN_1.id, ping=6)
        self.handler.find_live_scenario()
        self.assertEqual(Age2ScenarioData.AP_JOAN_1, self.active_scenario())

        self.write_packet(attila, Age2ScenarioData.AP_ATTILA_1.id, ping=900)

        self.assertFalse(self.handler.find_live_scenario(),
                         "a ping recorded before we stopped scanning is not evidence of movement")
        self.assertEqual(Age2ScenarioData.AP_JOAN_1, self.active_scenario())

    def test_a_locked_scenario_is_not_followed(self) -> None:
        """Joan 2 is not unlocked yet, so its packet is noted and ignored, not followed."""
        joan = Age2CampaignData.JOAN
        self.write_packet(joan, Age2ScenarioData.AP_JOAN_2.id, ping=5)
        self.handler.find_live_scenario()

        self.write_packet(joan, Age2ScenarioData.AP_JOAN_2.id, ping=6)

        self.assertFalse(self.handler.find_live_scenario())
        self.assertIsNone(self.handler.active_file)


if __name__ == "__main__":
    unittest.main()
