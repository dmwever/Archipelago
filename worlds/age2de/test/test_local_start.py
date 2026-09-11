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
    satisfied,
    solve,
    state_with,
    base_candidate_names,
    base_items,
    conjuncts,
    scenario_base_rule,
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


class TestBaseItemsJoan(Age2TestBase):
    options = {
        "enabled_campaigns": {JOAN},
        "starting_campaigns": {JOAN},
    }

    def test_joan_1_has_no_base_of_its_own(self) -> None:
        # has_base = False_(), so it must contribute nothing rather than poison the target.
        self.assertIsNone(scenario_base_rule(self.world, Age2ScenarioData.AP_JOAN_1))

    def test_town_centre_items_survive_the_missing_villagers(self) -> None:
        got = base_items(self.world, Age2ScenarioData.AP_JOAN_1)
        print(f"\n[base_items] Joan 1 -> {len(got)} items: {sorted(got)}")
        self.assertIn(Age2ItemData.TOWN_CENTER_WOOD.item_name, got)
        self.assertIn(Age2ItemData.TOWN_CENTER_STONE.item_name, got)
        self.assert_satisfiable_conjuncts_met(got)
        # Nothing supplies villagers at turn one on a Joan start once campaign
        # progression is off the table, so that conjunct is skipped rather than
        # dragging the whole Joan 1 win set in behind it.
        for excluded in (Age2ItemData.PROGRESSIVE_JOAN_SCENARIO, Age2ItemData.AP_JOAN_1_TRANSPORT):
            self.assertNotIn(excluded.item_name, got)

    def assert_satisfiable_conjuncts_met(self, got: list[str]) -> None:
        """Every part of can_build_base that could be satisfied, is.

        Not the whole conjunction: base_items deliberately skips conjuncts no item can
        satisfy, which on a Joan start is the "some unlocked scenario has villagers"
        term. Asserting the whole target would demand the behaviour we chose against.
        """
        world = self.world
        base_state = self.multiworld.state
        candidates = base_candidate_names(world)
        state = state_with(world, base_state, got)
        checked = 0
        for conjunct in conjuncts(world.rules.logic.can_build_base()):
            resolved = resolve(world, conjunct)
            if solve(world, resolved, base_state, candidates) is None:
                continue
            checked += 1
            self.assertTrue(satisfied(resolved, state), f"unmet conjunct {conjunct} given {sorted(got)}")
        self.assertGreater(checked, 0, "no conjunct was satisfiable, so the test proves nothing")



class TestBaseItemsAttila(Age2TestBase):
    options = {
        "enabled_campaigns": {ATTILA},
        "starting_campaigns": {ATTILA},
    }

    VILS = {
        Age2ItemData.AP_ATTILA_1_BLEDAS_CAMP.item_name,
        Age2ItemData.AP_ATTILA_1_ATTILAS_CAMP.item_name,
        Age2ItemData.AP_ATTILA_1_ROMAN_VILLAGERS.item_name,
    }

    def test_attila_1_contributes_its_own_base_rule(self) -> None:
        self.assertIsNotNone(scenario_base_rule(self.world, Age2ScenarioData.AP_ATTILA_1))

    def test_includes_town_centre_and_a_villager_source(self) -> None:
        got = base_items(self.world, Age2ScenarioData.AP_ATTILA_1)
        print(f"\n[base_items] Attila 1 -> {len(got)} items: {sorted(got)}")
        self.assertIn(Age2ItemData.TOWN_CENTER_WOOD.item_name, got)
        self.assertIn(Age2ItemData.TOWN_CENTER_STONE.item_name, got)
        self.assertTrue(self.VILS & set(got), "no villager source was placed locally")
        self.assert_satisfiable_conjuncts_met(got)
        # One villager source is enough; solving conjuncts apart used to collect two.
        self.assertEqual(1, len(self.VILS & set(got)))

    def assert_satisfiable_conjuncts_met(self, got: list[str]) -> None:
        """Every part of can_build_base that could be satisfied, is.

        Not the whole conjunction: base_items deliberately skips conjuncts no item can
        satisfy, which on a Joan start is the "some unlocked scenario has villagers"
        term. Asserting the whole target would demand the behaviour we chose against.
        """
        world = self.world
        base_state = self.multiworld.state
        candidates = base_candidate_names(world)
        state = state_with(world, base_state, got)
        checked = 0
        for conjunct in conjuncts(world.rules.logic.can_build_base()):
            resolved = resolve(world, conjunct)
            if solve(world, resolved, base_state, candidates) is None:
                continue
            checked += 1
            self.assertTrue(satisfied(resolved, state), f"unmet conjunct {conjunct} given {sorted(got)}")
        self.assertGreater(checked, 0, "no conjunct was satisfiable, so the test proves nothing")



class TestConjuncts(unittest.TestCase):
    def test_flattens_nested_unconditional_ands(self) -> None:
        a, b, c = Has("A"), Has("B"), Has("C")
        self.assertEqual([a, b, c], conjuncts((a & b) & c))

    def test_leaves_a_single_rule_alone(self) -> None:
        a = Has("A")
        self.assertEqual([a], conjuncts(a))

    def test_does_not_split_an_or(self) -> None:
        rule = Has("A") | Has("B")
        self.assertEqual([rule], conjuncts(rule))
