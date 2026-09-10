"""Scenario item delivery over <SCENARIO>.xsdat.

Covers the unlock state CampaignHandler.sync_unlocked derives from the received item
list, and the per-scenario files that state decides to write.
"""

import os
import struct
import tempfile
import unittest

from ..campaign import XsdatFile
from ..client.handlers.CampaignHandler import CampaignHandler
from ..items.Items import Age2ItemData
from ..locations.Campaigns import Age2CampaignData
from ..locations.Scenarios import Age2ScenarioData

JOAN_CAMPAIGN = Age2ItemData.JOAN_OF_ARC
JOAN_PROGRESSIVE = Age2ItemData.PROGRESSIVE_JOAN_SCENARIO
ATTILA_CAMPAIGN = Age2ItemData.ATTILA_THE_HUN
FRENCH_CAMP = Age2ItemData.AP_JOAN_4_FRENCH_CAMP


def read_ints(path: str) -> list[int]:
    if not os.path.exists(path):
        return []
    with open(path, "rb") as fp:
        data = fp.read()
    return [struct.unpack("<i", data[i:i + 4])[0] for i in range(0, len(data), 4)]


class TestScenarioItems(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.folder = self._tmp.name + os.sep

    def handler(self, *items: Age2ItemData) -> CampaignHandler:
        handler = CampaignHandler([campaign for campaign in Age2CampaignData])
        handler.set_user_folder(self.folder)
        handler.sync_unlocked(list(items))
        return handler

    def unlocked(self, handler: CampaignHandler) -> list[str]:
        return [scn.data.name for scn in handler.scenarios.values() if scn.unlocked]

    def write_campaign_packet(self, campaign: Age2CampaignData, scenario_id: int) -> None:
        with open(self.folder + campaign.xsdat_read_name, "wb") as fp:
            XsdatFile.write_bool(fp, True)
            for _ in range(17):
                XsdatFile.write_int(fp, 0)
            XsdatFile.write_int(fp, scenario_id)

    def test_unlock_is_independent_of_item_order(self) -> None:
        expected = ["AP_JOAN_1", "AP_JOAN_2", "AP_JOAN_3", "AP_JOAN_4"]
        campaign_first = self.handler(JOAN_CAMPAIGN, JOAN_PROGRESSIVE, JOAN_PROGRESSIVE, JOAN_PROGRESSIVE)
        campaign_last = self.handler(JOAN_PROGRESSIVE, JOAN_PROGRESSIVE, JOAN_PROGRESSIVE, JOAN_CAMPAIGN)

        self.assertEqual(self.unlocked(campaign_first), expected)
        self.assertEqual(
            self.unlocked(campaign_last),
            expected,
            "progressives received before the campaign item were dropped",
        )

    def test_campaign_item_alone_unlocks_only_the_first_scenario(self) -> None:
        self.assertEqual(self.unlocked(self.handler(JOAN_CAMPAIGN)), ["AP_JOAN_1"])

    def test_progressives_without_the_campaign_item_unlock_nothing(self) -> None:
        self.assertEqual(self.unlocked(self.handler(JOAN_PROGRESSIVE, JOAN_PROGRESSIVE)), [])

    def test_one_campaign_does_not_unlock_another(self) -> None:
        unlocked = self.unlocked(self.handler(ATTILA_CAMPAIGN, JOAN_PROGRESSIVE))
        self.assertEqual(unlocked, ["AP_ATTILA_1"])

    def test_unlock_clamps_to_campaign_length(self) -> None:
        unlocked = self.unlocked(self.handler(JOAN_CAMPAIGN, *([JOAN_PROGRESSIVE] * 9)))
        self.assertEqual(len(unlocked), 6)

    def test_resync_does_not_unlock_past_entitlement(self) -> None:
        items = [JOAN_CAMPAIGN, JOAN_PROGRESSIVE, JOAN_PROGRESSIVE]
        handler = self.handler(*items)
        self.assertEqual(len(self.unlocked(handler)), 3)

        handler.sync_unlocked(list(items))
        self.assertEqual(
            len(self.unlocked(handler)),
            3,
            "replaying the item list unlocked scenarios the player had not earned",
        )

    def test_unlocked_scenario_file_carries_its_items(self) -> None:
        self.handler(JOAN_CAMPAIGN, JOAN_PROGRESSIVE, JOAN_PROGRESSIVE, JOAN_PROGRESSIVE, FRENCH_CAMP)

        written = read_ints(self.folder + Age2ScenarioData.AP_JOAN_4.xsdat_write_name)
        self.assertEqual(written[0], 0)
        self.assertIn(
            FRENCH_CAMP.id,
            written[1:],
            "the French Camp item never reached JOAN4.xsdat",
        )

    def test_locked_scenario_gets_no_file(self) -> None:
        self.handler(JOAN_CAMPAIGN, FRENCH_CAMP)

        self.assertFalse(os.path.exists(self.folder + Age2ScenarioData.AP_JOAN_4.xsdat_write_name))

    def test_one_unwritable_file_does_not_suppress_the_others(self) -> None:
        os.mkdir(self.folder + Age2ScenarioData.AP_JOAN_1.xsdat_write_name)

        self.handler(JOAN_CAMPAIGN, *([JOAN_PROGRESSIVE] * 5), FRENCH_CAMP)

        for scenario in (Age2ScenarioData.AP_JOAN_2, Age2ScenarioData.AP_JOAN_4, Age2ScenarioData.AP_JOAN_6):
            self.assertTrue(
                os.path.isfile(self.folder + scenario.xsdat_write_name),
                f"{scenario.name} was suppressed by an unrelated failure",
            )

    def test_find_active_campaign_refuses_a_locked_scenario(self) -> None:
        handler = self.handler(JOAN_CAMPAIGN)
        self.write_campaign_packet(Age2CampaignData.JOAN, Age2ScenarioData.AP_JOAN_4.id)

        self.assertFalse(handler.find_active_campaign())
        self.assertIsNone(handler.active_file)

    def test_find_active_campaign_accepts_an_unlocked_scenario(self) -> None:
        handler = self.handler(JOAN_CAMPAIGN, JOAN_PROGRESSIVE, JOAN_PROGRESSIVE, JOAN_PROGRESSIVE)
        self.write_campaign_packet(Age2CampaignData.JOAN, Age2ScenarioData.AP_JOAN_4.id)

        self.assertTrue(handler.find_active_campaign())
        self.assertEqual(handler.active_file.current_scenario.data, Age2ScenarioData.AP_JOAN_4)


if __name__ == "__main__":
    unittest.main()
