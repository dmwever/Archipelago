"""Local Start option.

Phase 2 covers campaign/scenario selection only — which scenario Local Start
will work against. Placement is not exercised here.
"""

import random
import unittest
from types import SimpleNamespace

from rule_builder.rules import False_, Has, HasAll, True_

from ..generation.LocalStart import (
    choose_start_scenario,
    resolve,
    solve,
    state_with,
    victory_location,
    win_items,
)
from ..items.Items import Age2ItemData
from ..locations.Locations import Age2ScenarioLocationData
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


class TestSolver(Age2TestBase):
    """The solver, against real resolved rules on a generated world."""

    options = {
        "enabled_campaigns": {JOAN},
        "starting_campaigns": {JOAN},
    }

    RAM = Age2ItemData.AP_JOAN_1_RAM.item_name
    SWORDSMEN = Age2ItemData.AP_JOAN_1_SWORDSMEN.item_name
    CROSSBOWMEN = Age2ItemData.AP_JOAN_1_CROSSBOWMEN.item_name
    TRANSPORT = Age2ItemData.AP_JOAN_1_TRANSPORT.item_name
    PROGRESSIVE = Age2ItemData.PROGRESSIVE_JOAN_SCENARIO.item_name

    def target_for(self, rule):
        return resolve(self.world, rule)

    def solve_for(self, rule, candidates):
        return solve(self.world, self.target_for(rule), self.multiworld.state, candidates)

    def test_and_over_or_takes_one_branch(self) -> None:
        # Has(ram) & (Has(swordsmen) | Has(crossbowmen)) needs two items, not three.
        rule = Has(self.RAM) & (Has(self.SWORDSMEN) | Has(self.CROSSBOWMEN))
        got = self.solve_for(rule, [self.RAM, self.SWORDSMEN, self.CROSSBOWMEN])
        self.assertEqual(2, len(got))
        self.assertIn(self.RAM, got)
        self.assertTrue(self.SWORDSMEN in got or self.CROSSBOWMEN in got)

    def test_conjunction_keeps_everything_it_needs(self) -> None:
        rule = HasAll(self.RAM, self.SWORDSMEN, self.TRANSPORT)
        got = self.solve_for(rule, [self.RAM, self.SWORDSMEN, self.CROSSBOWMEN, self.TRANSPORT])
        self.assertEqual({self.RAM, self.SWORDSMEN, self.TRANSPORT}, set(got))

    def test_already_satisfied_needs_nothing(self) -> None:
        self.assertEqual([], self.solve_for(True_(), [self.RAM]))

    def test_unsatisfiable_returns_none(self) -> None:
        self.assertIsNone(self.solve_for(False_(), [self.RAM]))

    def test_missing_item_returns_none(self) -> None:
        # The candidate pool cannot supply the transport, so the target is unreachable.
        rule = HasAll(self.RAM, self.TRANSPORT)
        self.assertIsNone(self.solve_for(rule, [self.RAM, self.SWORDSMEN]))

    def test_counts_take_as_many_copies_as_asked(self) -> None:
        rule = Has(self.PROGRESSIVE, 2)
        got = self.solve_for(rule, [self.PROGRESSIVE] * 4 + [self.RAM])
        self.assertEqual([self.PROGRESSIVE] * 2, got)

    def test_location_target_joan_1_victory(self) -> None:
        # The real thing: what does it take to reach Joan 1's victory from turn one?
        victory = self.world.get_location(Age2ScenarioLocationData.JOAN1_VICTORY.global_name())
        candidates = [item.name for item in self.multiworld.itempool if item.player == self.player]
        got = solve(self.world, victory, self.multiworld.state, candidates)
        self.assertIsNotNone(got)
        self.assertEqual(3, len(got))
        self.assertIn(self.RAM, got)
        self.assertIn(self.TRANSPORT, got)
        self.assertTrue(self.SWORDSMEN in got or self.CROSSBOWMEN in got)
        # And the answer actually holds.
        self.assertTrue(victory.can_reach(state_with(self.world, self.multiworld.state, got)))


class TestWinItemsJoan(Age2TestBase):
    options = {
        "enabled_campaigns": {JOAN},
        "starting_campaigns": {JOAN},
    }

    def test_joan_1_is_beatable_from_turn_one(self) -> None:
        got = win_items(self.world, Age2ScenarioData.AP_JOAN_1)
        self.assertIsNotNone(got, "Joan 1 could not be made beatable from the pool")
        print(f"\n[win_items] Joan 1 -> {len(got)} items: {sorted(got)}")
        victory = victory_location(self.world, Age2ScenarioData.AP_JOAN_1)
        self.assertTrue(victory.can_reach(state_with(self.world, self.multiworld.state, got)))

    def test_scenario_outside_the_playthrough_has_no_victory(self) -> None:
        self.assertIsNone(victory_location(self.world, Age2ScenarioData.AP_ATTILA_1))
        self.assertIsNone(win_items(self.world, Age2ScenarioData.AP_ATTILA_1))


class TestWinItemsAttila(Age2TestBase):
    options = {
        "enabled_campaigns": {ATTILA},
        "starting_campaigns": {ATTILA},
    }

    def test_attila_1_is_beatable_from_turn_one(self) -> None:
        got = win_items(self.world, Age2ScenarioData.AP_ATTILA_1)
        self.assertIsNotNone(got, "Attila 1 could not be made beatable from the pool")
        print(f"\n[win_items] Attila 1 -> {len(got)} items: {sorted(got)}")
        victory = victory_location(self.world, Age2ScenarioData.AP_ATTILA_1)
        self.assertTrue(victory.can_reach(state_with(self.world, self.multiworld.state, got)))
