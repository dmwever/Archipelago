"""Local Start option.

Phase 2 covers campaign/scenario selection only — which scenario Local Start
will work against. Placement is not exercised here.
"""

import random
import unittest
from types import SimpleNamespace

from ..generation.LocalStart import choose_start_scenario
from ..locations.Campaigns import Age2CampaignData
from ..locations.Scenarios import Age2ScenarioData
from .bases import Age2TestBase

ATTILA = Age2CampaignData.ATTILA.campaign_name
JOAN = Age2CampaignData.JOAN.campaign_name


class TestSelectionAttilaOnly(Age2TestBase):
    options = {
        "enabled_campaigns": {ATTILA},
        "starting_campaigns": {ATTILA},
    }

    def test_picks_attila_chapter_one(self) -> None:
        self.assertEqual(Age2ScenarioData.AP_ATTILA_1, choose_start_scenario(self.world))


class TestSelectionJoanOnly(Age2TestBase):
    options = {
        "enabled_campaigns": {JOAN},
        "starting_campaigns": {JOAN},
    }

    def test_picks_joan_chapter_one(self) -> None:
        self.assertEqual(Age2ScenarioData.AP_JOAN_1, choose_start_scenario(self.world))


class TestSelectionBothCampaigns(Age2TestBase):
    options = {
        "enabled_campaigns": {ATTILA, JOAN},
        "starting_campaigns": {ATTILA, JOAN},
    }

    def test_draws_one_starting_scenario(self) -> None:
        self.assertIn(
            choose_start_scenario(self.world),
            (Age2ScenarioData.AP_ATTILA_1, Age2ScenarioData.AP_JOAN_1),
        )


class TestSelectionStartNotEnabled(Age2TestBase):
    """A starting campaign is supposed to imply an included campaign.

    That it currently does not is a separate bug. Selection follows
    starting_campaigns regardless, rather than silently doing nothing.
    """
    options = {
        "enabled_campaigns": {ATTILA},
        "starting_campaigns": {JOAN},
    }
    run_default_tests = False

    def test_follows_starting_campaigns(self) -> None:
        self.assertEqual(Age2ScenarioData.AP_JOAN_1, choose_start_scenario(self.world))


class TestSelectionNoStartingCampaign(Age2TestBase):
    options = {
        "enabled_campaigns": {ATTILA},
        "starting_campaigns": set(),
    }
    run_default_tests = False

    def test_no_starting_campaign_means_nothing_to_do(self) -> None:
        self.assertIsNone(choose_start_scenario(self.world))


class _StubWorld:
    """Minimal stand-in for Age2World: choose_start_scenario only needs these two."""

    def __init__(self, names: set[str], seed: int) -> None:
        self.random = random.Random(seed)
        self.options = SimpleNamespace(starting_campaigns=SimpleNamespace(value=names))


class TestSelectionDeterminism(unittest.TestCase):
    NAMES = {ATTILA, JOAN}

    def test_same_seed_picks_the_same_scenario(self) -> None:
        # The option value is an unordered set, so the draw is only reproducible
        # because choose_start_scenario sorts before choosing.
        for seed in range(8):
            first = choose_start_scenario(_StubWorld(set(self.NAMES), seed))
            second = choose_start_scenario(_StubWorld(set(self.NAMES), seed))
            self.assertEqual(first, second, f"seed {seed} drew two different scenarios")

    def test_both_campaigns_are_reachable_across_seeds(self) -> None:
        drawn = {choose_start_scenario(_StubWorld(set(self.NAMES), seed)) for seed in range(32)}
        self.assertEqual(
            {Age2ScenarioData.AP_ATTILA_1, Age2ScenarioData.AP_JOAN_1},
            drawn,
        )
