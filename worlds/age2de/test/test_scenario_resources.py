"""The per-scenario map yields.

These numbers are hand-owned data, so what is worth testing is not the arithmetic that produced
them - that scanner is gone - but the invariants that a careless edit would break, and the couple
of facts the logic layer will lean on.
"""

import unittest

from ..locations.connections import ScenarioResources  # noqa: F401  - assigns on import
from ..locations.connections.ScenarioResources import ScenarioResourceCount
from ..locations.Scenarios import Age2ScenarioData


class TestEveryScenarioHasCounts(unittest.TestCase):
    def test_every_scenario_is_bound(self):
        for scenario in Age2ScenarioData:
            with self.subTest(scenario.name):
                self.assertIsInstance(scenario.resources, ScenarioResourceCount)


class TestCountsAreCoherent(unittest.TestCase):
    def test_nothing_is_negative(self):
        for scenario in Age2ScenarioData:
            counts = scenario.resources
            for field, value in vars(counts).items():
                with self.subTest(f"{scenario.name}.{field}"):
                    self.assertGreaterEqual(value, 0)

    def test_fish_includes_shore_fish(self):
        """A fishing ship reaches everything a villager on the shore can."""
        for scenario in Age2ScenarioData:
            with self.subTest(scenario.name):
                self.assertGreaterEqual(scenario.resources.fish_count,
                                        scenario.resources.shore_fish_count)

    def test_food_counts_shore_fish_once(self):
        for scenario in Age2ScenarioData:
            counts = scenario.resources
            with self.subTest(scenario.name):
                self.assertEqual(
                    counts.food_count,
                    counts.hunt_count + counts.herd_count + counts.bush_count + counts.fish_count)

    def test_gold_and_stone_are_whole_piles(self):
        """800 a mine and 350 a quarry. A number that is not a multiple is a typo, or a
        hand correction that should carry a comment saying so."""
        for scenario in Age2ScenarioData:
            with self.subTest(scenario.name):
                self.assertEqual(scenario.resources.gold_count % 800, 0)
                self.assertEqual(scenario.resources.stone_count % 350, 0)


class TestTheFactsLogicLeansOn(unittest.TestCase):
    """Spot checks, so a silent all-zero regression cannot make every economy rule trivially
    true, and so the two scenarios the logic layer treats as special stay that way."""

    def test_joan_1_has_no_gold_and_no_stone(self):
        counts = Age2ScenarioData.AP_JOAN_1.resources
        self.assertEqual(counts.gold_count, 0)
        self.assertEqual(counts.stone_count, 0)

    def test_every_other_scenario_has_gold_and_stone(self):
        for scenario in Age2ScenarioData:
            if scenario is Age2ScenarioData.AP_JOAN_1:
                continue
            with self.subTest(scenario.name):
                self.assertGreater(scenario.resources.gold_count, 0)
                self.assertGreater(scenario.resources.stone_count, 0)

    def test_every_scenario_has_some_food(self):
        for scenario in Age2ScenarioData:
            with self.subTest(scenario.name):
                self.assertGreater(scenario.resources.food_count, 0)

    def test_attila_4_is_the_fish_drought(self):
        """Five deep fish and seven shore fish on the map. can_fish_easily has to come out
        False there, and this is the datum it rests on."""
        attila_4 = Age2ScenarioData.AP_ATTILA_4.resources
        self.assertLess(attila_4.fish_count, 3000)
        self.assertGreater(Age2ScenarioData.AP_ATTILA_1.resources.fish_count,
                           attila_4.fish_count * 5)

    def test_relics_are_where_we_think(self):
        with_relics = {scenario.name: scenario.resources.relic_count
                       for scenario in Age2ScenarioData if scenario.resources.relic_count}
        self.assertEqual(with_relics, {"AP_ATTILA_3": 2, "AP_ATTILA_4": 4})

    def test_no_map_has_an_oyster_or_a_whale_yet(self):
        """Both fields exist for scenarios not yet written. If this ever fails, a map gained
        one and the gold logic should start counting it."""
        for scenario in Age2ScenarioData:
            with self.subTest(scenario.name):
                self.assertEqual(scenario.resources.oyster_count, 0)
                self.assertEqual(scenario.resources.whale_count, 0)
