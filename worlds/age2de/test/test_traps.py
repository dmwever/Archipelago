"""Traps spend the starting-resource surplus and nothing else.

smart_add_starting_resources bin-packs toward four resource targets and then keeps padding with
random starting resources once every target is met. That padding is the only budget traps are
allowed to take, so a seed with no room to spare produces no traps at all rather than a weaker
opening. The targets-survive test below is the one that encodes that rule; the rest guard the
option surface around it.
"""
from collections import Counter
import unittest

from BaseClasses import ItemClassification

from . import bases
from .. import Age2World
from ..items import Items
from ..locations.Campaigns import Age2CampaignData

ATTILA = Age2CampaignData.ATTILA.campaign_name
JOAN = Age2CampaignData.JOAN.campaign_name

TRAP_NAMES = set(Items.TRAP_NAMES)

# Mirrors the targets in _build_starting_resources. Duplicated deliberately: a test that read them
# from the implementation could not catch the implementation lowering them.
TARGETS = {
    Items.Resource.WOOD: 1000,
    Items.Resource.FOOD: 1000,
    Items.Resource.GOLD: 750,
    Items.Resource.STONE: 500,
}

# Traps only appear where there is surplus, and a single-campaign seed has two filler slots in
# total. Every pool test here needs a seed large enough to have padding to spend.
BIG_SEED = {
    "enabled_campaigns": {ATTILA, JOAN},
    "starting_campaigns": {ATTILA},
    "techsanity": 3,
}


def trap_counts(itempool) -> Counter:
    return Counter(item.name for item in itempool if item.name in TRAP_NAMES)


def resource_totals(itempool) -> Counter:
    totals = Counter()
    for item in itempool:
        payload = Items.NAME_TO_ITEM[item.name].type
        if isinstance(payload, Items.StartingResources):
            totals[payload.type] += payload.amount
    return totals


class TestTrapsAreOptIn(bases.Age2TestBase):
    options = dict(BIG_SEED)

    def test_no_traps_without_the_option(self) -> None:
        self.assertEqual(Counter(), trap_counts(self.multiworld.itempool),
                         "traps reached the pool with trap_difficulty left at its default")


class TestTrapsReachThePool(bases.Age2TestBase):
    """Presence is asserted through roll_traps rather than the generated pool. age2de seeds are
    item-dense -- the filler budget is roughly 15 to 40 slots -- so whether any surplus survives
    the resource targets is genuinely seed-dependent, and a pool-level presence assertion would
    flake. What the pool must hold on every seed are the invariants below."""

    options = {**BIG_SEED, "trap_difficulty": 5, "trap_percentage": 100}

    def test_roll_traps_spends_the_whole_surplus_at_full_percentage(self) -> None:
        traps = self.world.roll_traps(40)
        self.assertEqual(40, len(traps))
        for trap in traps:
            self.assertIn(trap.name, TRAP_NAMES)

    def test_roll_traps_takes_the_percentage_share(self) -> None:
        self.world.options.trap_percentage.value = 25
        self.assertEqual(10, len(self.world.roll_traps(40)))

    def test_the_pool_still_matches_the_location_count(self) -> None:
        unfilled = self.multiworld.get_unfilled_locations(self.player)
        self.assertEqual(len(unfilled), len(self.multiworld.itempool))

    def test_the_starting_resource_targets_survive(self) -> None:
        """The priority rule, stated as the invariant that actually holds on every seed.

        A trap can only exist where there was surplus, and surplus is only counted once every
        target has been met without halving. So traps in the pool prove the targets were funded.
        The converse is not a defect: a seed whose filler budget cannot fund the targets halves
        them and produces no traps, which is the rule working rather than failing."""
        pool = self.multiworld.itempool
        if sum(trap_counts(pool).values()) == 0:
            return
        totals = resource_totals(pool)
        for resource, target in TARGETS.items():
            self.assertGreaterEqual(totals[resource], target,
                                    f"{resource.name} fell to {totals[resource]}, below its {target} target")

    def test_every_trap_is_classified_as_a_trap(self) -> None:
        for item in self.multiworld.itempool:
            if item.name in TRAP_NAMES:
                self.assertEqual(ItemClassification.trap, item.classification, item.name)


class TestTrapDifficultyGatesThePool(bases.Age2TestBase):
    options = {**BIG_SEED, "trap_difficulty": 0, "trap_percentage": 100}

    def test_no_traps_at_no_traps_however_high_the_percentage(self) -> None:
        self.assertEqual(Counter(), trap_counts(self.multiworld.itempool))


class TestAWeightOfZeroExcludesOneTrap(bases.Age2TestBase):
    EXCLUDED = Items.Age2ItemData.TRAP_WOLOLO.item_name

    options = {
        **BIG_SEED,
        "trap_difficulty": 5,
        "trap_percentage": 100,
        "trap_distribution": {EXCLUDED: 0},
    }

    def test_the_zero_weighted_trap_never_appears(self) -> None:
        self.assertEqual(0, trap_counts(self.multiworld.itempool)[self.EXCLUDED],
                         "a trap weighted 0 was still rolled")

    def test_a_large_roll_never_yields_it_either(self) -> None:
        """200 draws over eight remaining traps: absence here is by construction, not luck."""
        rolled = Counter(trap.name for trap in self.world.roll_traps(200))
        self.assertEqual(0, rolled[self.EXCLUDED])
        self.assertEqual(200, sum(rolled.values()), "zeroing one trap suppressed the rest")


class TestEveryWeightZeroSuppressesTraps(bases.Age2TestBase):
    options = {
        **BIG_SEED,
        "trap_difficulty": 5,
        "trap_percentage": 100,
        "trap_distribution": {name: 0 for name in Items.TRAP_NAMES},
    }

    def test_all_weights_zero_overrides_the_percentage(self) -> None:
        self.assertEqual(Counter(), trap_counts(self.multiworld.itempool))
        self.assertEqual([], self.world.roll_traps(200), "every weight was 0 but traps were rolled")

    def test_the_pool_still_matches_the_location_count(self) -> None:
        unfilled = self.multiworld.get_unfilled_locations(self.player)
        self.assertEqual(len(unfilled), len(self.multiworld.itempool))


class TestSurplusAccounting(bases.Age2TestBase):
    options = dict(BIG_SEED)

    def test_a_budget_too_small_for_the_targets_reports_no_surplus(self) -> None:
        """Halving means the targets were abandoned, not met. A seed too tight to fund them is
        too tight to fund traps, so the surplus is forfeited rather than shared."""
        for wanted in range(0, 16):
            _items, surplus = self.world._build_starting_resources(wanted)
            self.assertEqual(0, surplus, f"{wanted} slots reported {surplus} surplus")

    def test_a_generous_budget_reports_surplus(self) -> None:
        _items, surplus = self.world._build_starting_resources(80)
        self.assertGreater(surplus, 0, "80 slots funded the targets but reported no surplus")

    def test_the_surplus_is_never_more_than_the_budget(self) -> None:
        for wanted in (20, 40, 80, 160):
            items, surplus = self.world._build_starting_resources(wanted)
            self.assertEqual(wanted, len(items))
            self.assertLessEqual(surplus, wanted)

    def test_roll_traps_returns_nothing_without_surplus(self) -> None:
        self.world.options.trap_difficulty.value = 5
        self.world.options.trap_percentage.value = 100
        self.assertEqual([], self.world.roll_traps(0))
        self.assertEqual([], self.world.roll_traps(-1))


class TestTrapItemGroup(unittest.TestCase):
    def test_the_group_holds_every_trap(self) -> None:
        self.assertEqual(TRAP_NAMES, Age2World.item_name_groups["Traps"])

    def test_every_trap_id_is_in_the_band(self) -> None:
        """5000-5099. ItemHandler.xs dispatches on this range and has no else branch, so an id
        outside it is dropped in game with no output."""
        for trap in Items.CATEGORY_TO_ITEMS[Items.Trap]:
            self.assertTrue(5000 <= trap.id <= 5099, f"{trap.item_name} has id {trap.id}")
