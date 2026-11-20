"""/mercenaries and /scenarios each report one status per row, and the interesting part is the
precedence between them: a mercenary in a seat is In-Pavilion rather than Unlocked, and the scenario
you are playing reads Active even when you have finished it before.

The commands themselves only format, so these drive the handlers the way test_client_victory does
rather than standing up a whole context.
"""

import asyncio
import os
import tempfile
import types
import unittest
from unittest import mock

from ..client import GameClient
from ..client.ApClient import Age2CommandProcessor, Age2Context
from ..client.GameClient import AGE2_USER_PROFILE, Age2GameContext, DefaultClientInterface

from ..client.DataStorage import DataStorage
from ..client.handlers.CampaignHandler import ActiveFile, CampaignHandler
from ..client.handlers.MercenaryHandler import MercenaryHandler, NO_SEAT, SEAT_COUNT
from ..items.Items import (Age2ItemData, CATEGORY_TO_ITEMS, Campaign, Mercenary,
                           ProgressiveScenario)
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
            self.assertEqual("Missing", self.handler.status(mercenary))

    def test_a_seated_mercenary_reads_in_pavilion_not_unlocked(self) -> None:
        self.handler.try_sync_mercenaries(self.roster)
        for mercenary in self.handler.seated():
            self.assertEqual("In-Pavilion", self.handler.status(mercenary),
                             f"{mercenary.item_name} holds a seat, so Unlocked would understate it")

    def test_the_overflow_reads_unlocked(self) -> None:
        self.handler.try_sync_mercenaries(self.roster)
        for mercenary in self.handler.queued():
            self.assertEqual("Unlocked", self.handler.status(mercenary))

    def test_spending_one_moves_it_to_used(self) -> None:
        self.handler.try_sync_mercenaries(self.roster)
        spent = self.handler.seated()[0]
        self.handler.use_mercenary(spent)
        self.assertEqual("Used", self.handler.status(spent))

    def test_every_mercenary_reports_exactly_one_status(self) -> None:
        self.handler.try_sync_mercenaries(self.roster)
        spent = self.handler.seated()[0]
        self.handler.use_mercenary(spent)
        self.handler.try_sync_mercenaries(self.roster, spent=[spent])
        counted = [self.handler.status(mercenary) for mercenary in self.roster]
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

    def test_with_no_items_only_the_first_chapter_is_campaign_locked(self) -> None:
        """Chapter one needs no progressive, so the campaign item is the only thing it lacks. Every
        later chapter is missing its progressive as well, which is plain Missing."""
        self.handler.sync_unlocked([])
        for campaign in EVERY_CAMPAIGN:
            chapters = CAMPAIGN_TO_SCENARIOS[campaign]
            self.assertEqual("Campaign Locked", self.handler.status(chapters[0]))
            for scenario in chapters[1:]:
                self.assertEqual("Missing", self.handler.status(scenario))

    def test_progressives_without_the_campaign_read_campaign_locked(self) -> None:
        attila = Age2CampaignData.ATTILA
        chapters = CAMPAIGN_TO_SCENARIOS[attila]
        progressive = self.progressive_item(attila)
        self.handler.sync_unlocked([progressive, progressive])

        for scenario in chapters[:3]:
            self.assertEqual("Campaign Locked", self.handler.status(scenario),
                             "the progressives reach this chapter; only the campaign is missing")
        self.assertEqual("Missing", self.handler.status(chapters[3]),
                         "the progressives do not reach this far, so it is missing outright")

    def progressive_item(self, campaign: Age2CampaignData) -> Age2ItemData:
        for item in CATEGORY_TO_ITEMS[ProgressiveScenario]:
            if item.type.vanilla_campaign == campaign:
                return item
        raise AssertionError(f"no progressive scenario item for {campaign}")

    def test_the_campaign_item_grants_the_first_chapter_only(self) -> None:
        attila = Age2CampaignData.ATTILA
        self.handler.sync_unlocked([self.campaign_item(attila)])
        chapters = CAMPAIGN_TO_SCENARIOS[attila]
        self.assertEqual("Available", self.handler.status(chapters[0]))
        for scenario in chapters[1:]:
            self.assertEqual("Missing", self.handler.status(scenario),
                             "Archipelago has not granted this chapter yet")

    def test_a_granted_chapter_waits_on_the_one_before_it(self) -> None:
        """Unlocked is the gap the world opened but the game has not: Archipelago handed over the
        chapter, and the campaign still wants the previous mission beaten first."""
        attila = Age2CampaignData.ATTILA
        chapters = CAMPAIGN_TO_SCENARIOS[attila]
        self.handler.sync_unlocked([self.campaign_item(attila), self.progressive_item(attila)])

        self.assertEqual("Unlocked", self.handler.status(chapters[1]),
                         "chapter 1 is unbeaten, so the game will not offer chapter 2")

        self.handler.scenarios[chapters[0]].completed = True
        self.assertEqual("Available", self.handler.status(chapters[1]),
                         "chapter 1 is beaten, so chapter 2 should now be selectable")

    def test_holding_one_campaign_does_nothing_for_another(self) -> None:
        self.handler.sync_unlocked([self.campaign_item(Age2CampaignData.ATTILA)])
        chapters = CAMPAIGN_TO_SCENARIOS[Age2CampaignData.JOAN]
        self.assertEqual("Campaign Locked", self.handler.status(chapters[0]),
                         "Joan's first chapter still only wants Joan's campaign item")
        for scenario in chapters[1:]:
            self.assertEqual("Missing", self.handler.status(scenario))

    def test_the_scenario_being_played_reads_active_even_once_completed(self) -> None:
        attila = Age2CampaignData.ATTILA
        self.handler.sync_unlocked([self.campaign_item(attila)])
        first = CAMPAIGN_TO_SCENARIOS[attila][0]
        managed = self.handler.scenarios[first]
        managed.completed = True

        self.assertEqual("Completed", self.handler.status(first))
        self.handler.active_file = ActiveFile(scn=managed, read_file_name="whatever.xsdat")
        self.assertEqual("Active", self.handler.status(first),
                         "replaying a finished scenario should surface that you are in it")


class TestMercenaryStatusesOutsideAMatch(unittest.TestCase):
    def setUp(self) -> None:
        self._folder = tempfile.TemporaryDirectory()
        self.addCleanup(self._folder.cleanup)
        os.makedirs(self._folder.name + AGE2_USER_PROFILE)
        self.ctx = Age2GameContext(DefaultClientInterface())
        self.ctx.client_status.tag = "T"
        self.ctx.client_status.player_name = "P"
        self.ctx.update_game_user_folder(self._folder.name)
        self.held = CATEGORY_TO_ITEMS[Mercenary][:SEAT_COUNT + 2]
        self.ctx.client_status.unlocked_items = list(self.held)

    def run_one_tick(self) -> None:
        async def no_sleep() -> None:
            pass

        with (
            mock.patch.object(GameClient, "long_sleep", no_sleep),
            mock.patch.object(GameClient, "short_sleep", no_sleep),
        ):
            asyncio.run(GameClient.status_tick(self.ctx))
        self.assertFalse(self.ctx.campaign_handler.has_active_scenario())

    def test_held_mercenaries_are_not_missing_with_no_scenario_running(self) -> None:
        self.ctx.reconcile_spent(0)
        self.run_one_tick()
        statuses = [self.ctx.mercenary_handler.status(mercenary) for mercenary in self.held]
        self.assertEqual(SEAT_COUNT, statuses.count("In-Pavilion"))
        self.assertEqual(2, statuses.count("Unlocked"))

    def test_a_spent_mercenary_reads_used_with_no_scenario_running(self) -> None:
        self.ctx.reconcile_spent(1)
        self.run_one_tick()
        self.assertEqual("Used", self.ctx.mercenary_handler.status(self.held[0]))
        self.assertNotIn(self.held[0], self.ctx.mercenary_handler.seated())

    def test_nothing_is_seated_before_the_spent_state_arrives(self) -> None:
        self.run_one_tick()
        for mercenary in self.held:
            self.assertEqual("Missing", self.ctx.mercenary_handler.status(mercenary))


class TestMercenaryQueueTags(unittest.TestCase):
    def setUp(self) -> None:
        self._folder = tempfile.TemporaryDirectory()
        self.addCleanup(self._folder.cleanup)
        self.handler = MercenaryHandler(CATEGORY_TO_ITEMS[Mercenary])
        self.handler.set_user_folder(self._folder.name + "/")
        self.storage = DataStorage(EVERY_CAMPAIGN)
        self.unlock_order = list(reversed(self.storage.mercenaries[:SEAT_COUNT + 3]))
        ctx = Age2Context.__new__(Age2Context)
        ctx.ui = None
        ctx.data_storage = self.storage
        ctx.game_ctx = types.SimpleNamespace(mercenary_handler=self.handler)
        self.processor = Age2CommandProcessor(ctx)

    def printed_lines(self) -> list[str]:
        with self.assertLogs("Client", "INFO") as logs:
            self.processor._cmd_mercenaries()
        return [record.getMessage() for record in logs.records]

    def test_seated_mercenaries_show_their_seat_in_unlock_order(self) -> None:
        self.handler.try_sync_mercenaries(self.unlock_order)
        lines = self.printed_lines()
        for seat, mercenary in enumerate(self.unlock_order[:SEAT_COUNT], start=1):
            self.assertIn(f"{'In-Pavilion':<12}{mercenary.item_name} (seat {seat})", lines)

    def test_queued_mercenaries_show_their_place_in_unlock_order(self) -> None:
        self.handler.try_sync_mercenaries(self.unlock_order)
        lines = self.printed_lines()
        for place, mercenary in enumerate(self.unlock_order[SEAT_COUNT:], start=1):
            self.assertIn(f"{'Unlocked':<12}{mercenary.item_name} (#{place} in queue)", lines)

    def test_spending_a_seated_one_moves_the_queue_up(self) -> None:
        self.handler.try_sync_mercenaries(self.unlock_order)
        self.handler.use_mercenary(self.unlock_order[0])
        self.handler.try_sync_mercenaries(self.unlock_order, spent=[self.unlock_order[0]])
        lines = self.printed_lines()
        self.assertIn(f"{'Used':<12}{self.unlock_order[0].item_name}", lines)
        self.assertIn(
            f"{'In-Pavilion':<12}{self.unlock_order[SEAT_COUNT].item_name} (seat 1)",
            lines,
        )
        self.assertIn(
            f"{'Unlocked':<12}{self.unlock_order[SEAT_COUNT + 1].item_name} (#1 in queue)",
            lines,
        )

    def test_missing_mercenaries_carry_no_tag(self) -> None:
        lines = self.printed_lines()
        self.assertEqual(
            [f"{'Missing':<12}{mercenary.item_name}" for mercenary in self.storage.mercenaries],
            lines,
        )

    def test_the_list_runs_used_missing_queue_then_seats_each_descending(self) -> None:
        spent = self.unlock_order[0]
        self.handler.try_sync_mercenaries(self.unlock_order)
        self.handler.use_mercenary(spent)
        self.handler.try_sync_mercenaries(self.unlock_order, spent=[spent])
        seated = self.handler.seated()
        queued = self.handler.queued()
        missing = [
            mercenary for mercenary in self.storage.mercenaries
            if mercenary not in self.unlock_order
        ]
        expected = (
            [f"{'Used':<12}{spent.item_name}"]
            + [f"{'Missing':<12}{mercenary.item_name}" for mercenary in missing]
            + [
                f"{'Unlocked':<12}{queued[place - 1].item_name} (#{place} in queue)"
                for place in range(len(queued), 0, -1)
            ]
            + [
                f"{'In-Pavilion':<12}{seated[seat - 1].item_name} (seat {seat})"
                for seat in range(SEAT_COUNT, 0, -1)
            ]
        )
        self.assertEqual(2, len(queued))
        self.assertEqual(expected, self.printed_lines())


if __name__ == "__main__":
    unittest.main()
