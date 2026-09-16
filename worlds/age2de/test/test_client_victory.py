"""check_victory used to fall through its loop and return True when nothing was required.

status_loop calls it every tick and latches client_status.finished_game on the first True, then
sends CLIENT_GOAL. So a slot whose data never reached setup_victory_requirements - an older or
newer apworld, where the version check only warns - finished itself on the first pass.
"""
import unittest

from ..client.handlers.CampaignHandler import CampaignHandler
from ..locations.Campaigns import Age2CampaignData
from ..locations.Scenarios import CAMPAIGN_TO_SCENARIOS

ATTILA_KEY = Age2CampaignData.ATTILA.campaign_name + "_unlocked"
JOAN_KEY = Age2CampaignData.JOAN.campaign_name + "_unlocked"


class TestVictoryRequirements(unittest.TestCase):
    def handler(self) -> CampaignHandler:
        return CampaignHandler(list(Age2CampaignData))

    def complete(self, handler: CampaignHandler, campaign: Age2CampaignData) -> None:
        for scenario in CAMPAIGN_TO_SCENARIOS[campaign]:
            handler.scenarios[scenario].completed = True

    def test_no_slot_data_is_not_a_victory(self):
        self.assertFalse(self.handler().check_victory(),
                         "victory was declared before any campaign was required")

    def test_another_game_s_keys_are_not_a_victory(self):
        handler = self.handler()
        handler.setup_victory_requirements({"someothergame_unlocked": True})
        self.assertFalse(handler.check_victory(),
                         "keys that match no campaign left the requirement set empty")

    def test_a_required_campaign_must_be_finished(self):
        handler = self.handler()
        handler.setup_victory_requirements({ATTILA_KEY: True})
        self.assertFalse(handler.check_victory())

        scenarios = CAMPAIGN_TO_SCENARIOS[Age2CampaignData.ATTILA]
        for scenario in scenarios[:-1]:
            handler.scenarios[scenario].completed = True
        self.assertFalse(handler.check_victory(), "one scenario short still counted as a win")

        handler.scenarios[scenarios[-1]].completed = True
        self.assertTrue(handler.check_victory())

    def test_an_excluded_campaign_does_not_block_victory(self):
        handler = self.handler()
        handler.setup_victory_requirements({ATTILA_KEY: True})
        self.complete(handler, Age2CampaignData.ATTILA)
        self.assertTrue(handler.check_victory(),
                        "a campaign the slot never enabled was still required")

    def test_every_required_campaign_counts(self):
        handler = self.handler()
        handler.setup_victory_requirements({ATTILA_KEY: True, JOAN_KEY: True})
        self.complete(handler, Age2CampaignData.ATTILA)
        self.assertFalse(handler.check_victory())

        self.complete(handler, Age2CampaignData.JOAN)
        self.assertTrue(handler.check_victory())


if __name__ == "__main__":
    unittest.main()
