"""/mercenaries and /scenarios each report one status per row, and the interesting part is the
precedence between them: a mercenary in a seat is In-Pavilion rather than Unlocked, and the scenario
you are playing reads Active even when you have finished it before.

The commands themselves only format, so these drive the handlers the way test_client_victory does
rather than standing up a whole context.
"""

import tempfile
import unittest

from ..client.DataStorage import DataStorage
from ..client.handlers.CampaignHandler import ActiveFile, CampaignHandler
from ..client.handlers.MercenaryHandler import MercenaryHandler, NO_SEAT, SEAT_COUNT
from ..items.Items import Age2ItemData, CATEGORY_TO_ITEMS, Campaign, Mercenary
from ..locations.Campaigns import Age2CampaignData
from ..locations.Scenarios import CAMPAIGN_TO_SCENARIOS

EVERY_CAMPAIGN = list(Age2CampaignData)


class TestMercenaryStatuses(unittest.TestCase):
    def setUp(self) -> None:
        self._folder = tempfile.TemporaryDirectory()
        self.addCleanup(self._folder.cleanup)
        self.handler = MercenaryHandler(CATEGORY_TO_ITEMS[Mercenary])
        self.handler.set_user_folder(self._folder.name + "/")
        self.roster = DataStorage(EVERY_CAMPAIGN).mercenaries

    def test_nothing_found_is_all_missing(self) -> None:
        for mercenary in self.roster:
            self.assertEqual("Missing", self.handler.status_of(mercenary))

    def test_a_seated_mercenary_reads_in_pavilion_not_unlocked(self) -> None:
        self.handler.try_sync_mercenaries(self.roster)
        for mercenary in self.handler.seated():
            self.assertEqual("In-Pavilion", self.handler.status_of(mercenary),
                             f"{mercenary.item_name} holds a seat, so Unlocked would understate it")

    def test_the_overflow_reads_unlocked(self) -> None:
        self.handler.try_sync_mercenaries(self.roster)
        for mercenary in self.handler.queued():
            self.assertEqual("Unlocked", self.handler.status_of(mercenary))

    def test_spending_one_moves_it_to_used(self) -> None:
        self.handler.try_sync_mercenaries(self.roster)
        spent = self.handler.seated()[0]
        self.handler.use_mercenary(spent)
        self.assertEqual("Used", self.handler.status_of(spent))

    def test_every_mercenary_reports_exactly_one_status(self) -> None:
        self.handler.try_sync_mercenaries(self.roster)
        self.handler.use_mercenary(self.handler.seated()[0])
        self.handler.try_sync_mercenaries(self.roster)
        counted = [self.handler.status_of(mercenary) for mercenary in self.roster]
        self.assertEqual(len(self.roster), len(counted))
        self.assertEqual(SEAT_COUNT, counted.count("In-Pavilion"),
                         "every seat should be filled while the queue still has mercenaries in it")
        self.assertEqual(1, counted.count("Used"))


class TestScenarioStatuses(unittest.TestCase):
    def setUp(self) -> None:
        # sync_unlocked writes every unlocked scenario's .xsdat, and an unset folder means the
        # working directory, so this needs somewhere disposable to point at.
        self._folder = tempfile.TemporaryDirectory()
        self.addCleanup(self._folder.cleanup)
        self.handler = CampaignHandler(EVERY_CAMPAIGN)
        self.handler.set_user_folder(self._folder.name + "/")
        self.roster = DataStorage(EVERY_CAMPAIGN).scenarios

    def campaign_item(self, campaign: Age2CampaignData) -> Age2ItemData:
        for item in CATEGORY_TO_ITEMS[Campaign]:
            if item.type.vanilla_campaign == campaign:
                return item
        raise AssertionError(f"no campaign item for {campaign}")

    def test_without_the_campaign_item_everything_is_missing(self) -> None:
        self.handler.sync_unlocked([])
        for scenario in self.roster:
            self.assertEqual("Missing", self.handler.status_of(scenario))

    def test_the_campaign_item_opens_the_first_chapter_only(self) -> None:
        attila = Age2CampaignData.ATTILA
        self.handler.sync_unlocked([self.campaign_item(attila)])
        chapters = CAMPAIGN_TO_SCENARIOS[attila]
        self.assertEqual("Available", self.handler.status_of(chapters[0]))
        for scenario in chapters[1:]:
            self.assertEqual("Unlocked", self.handler.status_of(scenario),
                             "the campaign is held, so a later chapter is not Missing")

    def test_another_campaign_stays_missing(self) -> None:
        self.handler.sync_unlocked([self.campaign_item(Age2CampaignData.ATTILA)])
        for scenario in CAMPAIGN_TO_SCENARIOS[Age2CampaignData.JOAN]:
            self.assertEqual("Missing", self.handler.status_of(scenario))

    def test_the_scenario_being_played_reads_active_even_once_completed(self) -> None:
        attila = Age2CampaignData.ATTILA
        self.handler.sync_unlocked([self.campaign_item(attila)])
        first = CAMPAIGN_TO_SCENARIOS[attila][0]
        managed = self.handler.scenarios[first]
        managed.completed = True

        self.assertEqual("Completed", self.handler.status_of(first))
        self.handler.active_file = ActiveFile(scn=managed, read_file_name="whatever.xsdat")
        self.assertEqual("Active", self.handler.status_of(first),
                         "replaying a finished scenario should surface that you are in it")


if __name__ == "__main__":
    unittest.main()
