"""Local Start option.

Phase 2 covers campaign/scenario selection only — which scenario Local Start
will work against. Placement is not exercised here.
"""

import random
import unittest
from types import SimpleNamespace

from Options import OptionError
from test.general import setup_solo_multiworld
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
    win_items,
)
from ..items.Items import Age2ItemData
from ..locations.Locations import VICTORY_SCENARIO_LOCATIONS, Age2ScenarioLocationData
from ..locations.Campaigns import NAME_TO_CAMPAIGN, Age2CampaignData
from ..locations.Scenarios import Age2ScenarioData
from .bases import Age2TestBase
from .. import Age2World

ATTILA = Age2CampaignData.ATTILA.campaign_name
JOAN = Age2CampaignData.JOAN.campaign_name


def victory_location(world, scenario):
    return world.get_location(VICTORY_SCENARIO_LOCATIONS[scenario.scenario_name].global_name())


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


class TestSelectionOptionErrors(unittest.TestCase):
    def assert_rejects(self, enabled: set[str], starting: set[str]) -> None:
        world = setup_solo_multiworld(Age2World, ()).worlds[1]
        world.options.enabled_campaigns.value = enabled
        world.options.starting_campaigns.value = starting
        with self.assertRaises(OptionError):
            world.generate_early()

    def test_starting_must_include_an_enabled_campaign(self) -> None:
        self.assert_rejects({ATTILA}, {JOAN})

    def test_enabled_needs_at_least_one(self) -> None:
        self.assert_rejects(set(), {ATTILA})

    def test_starting_needs_at_least_one(self) -> None:
        self.assert_rejects({ATTILA}, set())


class _StubWorld:
    """Minimal stand-in for Age2World: choose_start_scenario only needs these two."""

    def __init__(self, names: set[str], seed: int) -> None:
        self.random = random.Random(seed)
        self.starting_campaigns = {NAME_TO_CAMPAIGN[name] for name in names}


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
        victory = victory_location(self.world, Age2ScenarioData.AP_JOAN_1)
        self.assertTrue(victory.can_reach(state_with(self.world, self.multiworld.state, got)))


class TestWinItemsAttila(Age2TestBase):
    options = {
        "enabled_campaigns": {ATTILA},
        "starting_campaigns": {ATTILA},
    }

    def test_attila_1_is_beatable_from_turn_one(self) -> None:
        got = win_items(self.world, Age2ScenarioData.AP_ATTILA_1)
        self.assertIsNotNone(got, "Attila 1 could not be made beatable from the pool")
        victory = victory_location(self.world, Age2ScenarioData.AP_ATTILA_1)
        self.assertTrue(victory.can_reach(state_with(self.world, self.multiworld.state, got)))


class TestBaseItemsJoan(Age2TestBase):
    options = {
        "enabled_campaigns": {JOAN},
        "starting_campaigns": {JOAN},
    }

    def test_joan_1_has_no_base_of_its_own(self) -> None:
        # has_base = False_(), so it must contribute nothing rather than poison the target.
        rule = scenario_base_rule(self.world, Age2ScenarioData.AP_JOAN_1)
        self.assertTrue(resolve(self.world, rule).always_true)

    def test_town_centre_items_survive_the_missing_villagers(self) -> None:
        got = base_items(self.world, Age2ScenarioData.AP_JOAN_1)
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


class PlacementTestBase(Age2TestBase):
    """Shared assertions for a world generated with Local Start switched on."""

    def locally_placed(self) -> list[str]:
        """Names of the real items Local Start locked into this player's own locations.

        Event items are locked too but carry no code, so they are filtered out.
        """
        return [
            location.item.name
            for location in self.multiworld.get_locations(self.player)
            if location.locked and location.item is not None and location.item.code is not None
            and location.item.player == self.player
        ]

    def assert_placements_are_local(self) -> None:
        for location in self.multiworld.get_locations(self.player):
            if location.locked and location.item is not None and location.item.code is not None:
                self.assertEqual(self.player, location.item.player,
                                 f"{location.item.name} was locked into a foreign slot")

    def assert_pool_still_balances(self) -> None:
        # create_items sizes the pool to the location count; taking items out to place
        # them by hand must not break that.
        unfilled = self.multiworld.get_unfilled_locations(self.player)
        self.assertEqual(len(unfilled), len(self.multiworld.itempool))

    def assert_victory_reachable_from_placements(self, scenario) -> None:
        victory = victory_location(self.world, scenario)
        state = state_with(self.world, self.multiworld.state, self.locally_placed())
        self.assertTrue(victory.can_reach(state),
                        f"{scenario.scenario_name} victory not reachable from the placed set")


class TestPlaceWinJoan(PlacementTestBase):
    options = {
        "enabled_campaigns": {JOAN},
        "starting_campaigns": {JOAN},
        "local_start": "guarantee_win_first_scenario",
    }

    def test_joan_1_is_winnable_from_the_placements(self) -> None:
        placed = self.locally_placed()
        self.assertTrue(placed)
        self.assert_placements_are_local()
        self.assert_pool_still_balances()
        self.assert_victory_reachable_from_placements(Age2ScenarioData.AP_JOAN_1)


class TestPlaceWinAttila(PlacementTestBase):
    options = {
        "enabled_campaigns": {ATTILA},
        "starting_campaigns": {ATTILA},
        "local_start": "guarantee_win_first_scenario",
    }

    def test_attila_1_is_winnable_from_the_placements(self) -> None:
        placed = self.locally_placed()
        self.assertTrue(placed)
        self.assert_placements_are_local()
        self.assert_pool_still_balances()
        self.assert_victory_reachable_from_placements(Age2ScenarioData.AP_ATTILA_1)


class TestPlaceBaseJoan(PlacementTestBase):
    options = {
        "enabled_campaigns": {JOAN},
        "starting_campaigns": {JOAN},
        "local_start": "base",
    }

    def test_town_centre_items_are_local(self) -> None:
        placed = self.locally_placed()
        self.assert_placements_are_local()
        self.assert_pool_still_balances()
        self.assertIn(Age2ItemData.TOWN_CENTER_WOOD.item_name, placed)
        self.assertIn(Age2ItemData.TOWN_CENTER_STONE.item_name, placed)


class TestPlaceBothAttila(PlacementTestBase):
    options = {
        "enabled_campaigns": {ATTILA},
        "starting_campaigns": {ATTILA},
        "local_start": "both",
    }

    def test_win_and_base_are_placed_once_each(self) -> None:
        placed = self.locally_placed()
        self.assert_placements_are_local()
        self.assert_pool_still_balances()
        self.assert_victory_reachable_from_placements(Age2ScenarioData.AP_ATTILA_1)
        self.assertIn(Age2ItemData.TOWN_CENTER_WOOD.item_name, placed)
        # Deduped across the two passes: nothing is placed twice.
        self.assertEqual(len(placed), len(set(placed)))
        # The base pass solves on top of the win set, so a requirement the win items
        # already cover is not bought a second time. Villagers come from exactly one camp.
        camps = {
            Age2ItemData.AP_ATTILA_1_BLEDAS_CAMP.item_name,
            Age2ItemData.AP_ATTILA_1_ATTILAS_CAMP.item_name,
            Age2ItemData.AP_ATTILA_1_ROMAN_VILLAGERS.item_name,
        }
        self.assertEqual(1, len(camps & set(placed)), f"expected one villager source, got {sorted(camps & set(placed))}")


class TestPlaceDisabled(PlacementTestBase):
    options = {
        "enabled_campaigns": {ATTILA},
        "starting_campaigns": {ATTILA},
        "local_start": "no",
    }

    def test_nothing_is_locked(self) -> None:
        self.assertEqual([], self.locally_placed())
        self.assert_pool_still_balances()


class TestTwoSlots(unittest.TestCase):
    """Two age2de slots in one multiworld must not share state.

    included_campaigns, Logic.scenarios and ScenarioRules.locations used to be class
    attributes, so one slot's campaigns leaked into the next and every scenario shared
    one location dict. Local Start reads all three, so it would have solved against a
    merged view of both players.
    """

    def multiworld(self):
        from test.general import setup_multiworld
        from .. import Age2World
        return setup_multiworld(
            [Age2World, Age2World],
            options=[
                {"enabled_campaigns": {ATTILA}, "starting_campaigns": {ATTILA},
                 "local_start": "guarantee_win_first_scenario"},
                {"enabled_campaigns": {JOAN}, "starting_campaigns": {JOAN},
                 "local_start": "guarantee_win_first_scenario"},
            ],
        )

    def test_campaign_sets_do_not_merge(self) -> None:
        multiworld = self.multiworld()
        first, second = multiworld.worlds[1], multiworld.worlds[2]
        self.assertEqual({Age2CampaignData.ATTILA}, first.included_campaigns)
        self.assertEqual({Age2CampaignData.JOAN}, second.included_campaigns)
        self.assertIsNot(first.included_campaigns, second.included_campaigns)

    def test_each_slot_places_its_own_items(self) -> None:
        multiworld = self.multiworld()
        for player, scenario in ((1, Age2ScenarioData.AP_ATTILA_1), (2, Age2ScenarioData.AP_JOAN_1)):
            placed = [
                location.item for location in multiworld.get_locations(player)
                if location.locked and location.item is not None and location.item.code is not None
            ]
            self.assertTrue(placed, f"player {player} placed nothing")
            for item in placed:
                self.assertEqual(player, item.player, f"{item.name} landed in the wrong slot")
            world = multiworld.worlds[player]
            victory = victory_location(world, scenario)
            state = state_with(world, multiworld.state, [item.name for item in placed])
            self.assertTrue(victory.can_reach(state),
                            f"player {player} cannot beat {scenario.scenario_name} from its placements")
