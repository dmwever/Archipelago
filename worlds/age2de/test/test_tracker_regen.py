"""Universal Tracker rebuilt this world from the YAML with a seed of its own, so its budget sample
and every scenario's order differed from the server's - and with them everything the tracker said
about logic. One seed gave a different budget for the same location on every reconnect. These pin
that a rebuild handed the server's slot data draws the same world."""
import unittest

from worlds.AutoWorld import call_all
from test.general import setup_solo_multiworld

from .. import UT_SEED, Age2World

STEPS = ("generate_early", "create_regions", "create_items", "set_rules")


def build(seed: int, passthrough: dict | None = None):
    multiworld = setup_solo_multiworld(Age2World, (), seed=seed)
    if passthrough is not None:
        multiworld.re_gen_passthrough = {Age2World.game: passthrough}
    for step in STEPS:
        call_all(multiworld, step)
    return multiworld.worlds[1]


def drawn(world) -> tuple:
    """Everything the budget drew: the sample, its ranks, and each scenario's order."""
    budget = world.pool.budget
    orders = tuple(
        (scenario.scenario.name, tuple(entry.location.name for entry in scenario.budget.order.order))
        for scenario in world.rules.logic.scenarios
    )
    return tuple(sorted(location.name for location in budget.entries)), tuple(sorted(
        (location.name, rank) for location, rank in budget.rank.items())), orders


class TestTheTrackerRebuildsTheSameWorld(unittest.TestCase):
    def test_the_seed_goes_out_in_slot_data(self):
        world = build(seed=1)
        self.assertIn(UT_SEED, world.fill_slot_data())

    def test_a_rebuild_with_the_slot_data_draws_the_same_budget(self):
        server = build(seed=1)
        tracker = build(seed=2, passthrough=server.fill_slot_data())
        self.assertEqual(drawn(server), drawn(tracker))
        self.assertEqual(server.ut_seed, tracker.ut_seed)

    def test_without_it_a_rebuild_draws_its_own(self):
        """The control: the tracker's own seed really does draw something else."""
        self.assertNotEqual(drawn(build(seed=1)), drawn(build(seed=2)))

    def test_the_hook_hands_the_slot_data_back(self):
        """UT regenerates only when interpret_slot_data returns something."""
        slot_data = {UT_SEED: 7}
        self.assertEqual(slot_data, Age2World.interpret_slot_data(slot_data))
