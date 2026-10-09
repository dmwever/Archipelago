"""The per-scenario map yields, now that they are split by who holds them.

These numbers are hand-owned data, so what is worth testing is not the arithmetic that produced
them - that scanner is gone - but the invariants that a careless edit would break, and the couple
of facts the logic layer will lean on. The counts themselves are the truth, not the assertions:
nothing here pins a value that a re-scan of a map is allowed to move.
"""

import unittest
from dataclasses import fields

from ..locations.connections import ScenarioResources  # noqa: F401  - assigns on import
from ..locations.connections.ScenarioResources import ScenarioResourceCount, Tier, total
from ..locations.Scenarios import Age2ScenarioData

FIXED_FORCE = (Age2ScenarioData.AP_JOAN_1, Age2ScenarioData.AP_JOAN_5,
               Age2ScenarioData.AP_GENGHIS_1)
"""No villagers, so the yields are deliberately all zero however much the map holds."""

COUNT_FIELDS = tuple(field.name for field in fields(ScenarioResourceCount))


class TestEveryScenarioHasCounts(unittest.TestCase):
    def test_every_scenario_is_bound_in_every_tier(self):
        for scenario in Age2ScenarioData:
            with self.subTest(scenario.name):
                self.assertEqual(set(scenario.resources), set(Tier))

    def test_every_tier_is_a_count(self):
        for scenario in Age2ScenarioData:
            for tier, counts in scenario.resources.items():
                with self.subTest(f"{scenario.name}.{tier.name}"):
                    self.assertIsInstance(counts, ScenarioResourceCount)


class TestCountsAreCoherent(unittest.TestCase):
    def test_nothing_is_negative(self):
        for scenario in Age2ScenarioData:
            for tier, counts in scenario.resources.items():
                for field in COUNT_FIELDS:
                    with self.subTest(f"{scenario.name}.{tier.name}.{field}"):
                        self.assertGreaterEqual(getattr(counts, field), 0)

    def test_food_is_everything_edible_in_the_tier(self):
        """Shore and deep fish are independent counts - a boat reaches both, a fisherman only
        the one - so food adds them separately rather than taking a total and subtracting."""
        for scenario in Age2ScenarioData:
            for tier, counts in scenario.resources.items():
                with self.subTest(f"{scenario.name}.{tier.name}"):
                    self.assertEqual(
                        counts.food_count,
                        counts.hunt_count + counts.herd_count + counts.bush_count
                        + counts.shore_fish_count + counts.deep_fish_count)

    def test_gold_and_stone_are_whole_piles(self):
        """800 a mine and 350 a quarry, in every tier. A number that is not a multiple is a typo,
        or a hand correction that should carry a comment saying so."""
        for scenario in Age2ScenarioData:
            for tier, counts in scenario.resources.items():
                with self.subTest(f"{scenario.name}.{tier.name}"):
                    self.assertEqual(counts.gold_count % 800, 0)
                    self.assertEqual(counts.stone_count % 350, 0)

    def test_fish_split_by_reach_not_by_species(self):
        """Shore and deep are about what it takes to get at a fish, not what kind it is: a
        salmon against a beach is shore, a shore fish out in open water is deep. So neither
        count divides evenly by anything, and the only thing left to assert is that a map with
        fish files them somewhere."""
        for scenario in Age2ScenarioData:
            if scenario in FIXED_FORCE:
                continue
            counts = total(scenario)
            with self.subTest(scenario.name):
                self.assertGreater(counts.shore_fish_count + counts.deep_fish_count, 0)

    def test_the_total_is_the_tiers_added_up(self):
        for scenario in Age2ScenarioData:
            summed = total(scenario)
            for field in COUNT_FIELDS:
                with self.subTest(f"{scenario.name}.{field}"):
                    self.assertEqual(
                        getattr(summed, field),
                        sum(getattr(counts, field) for counts in scenario.resources.values()))


class TestTheFactsLogicLeansOn(unittest.TestCase):
    """Spot checks, so a silent all-zero regression cannot make every economy rule trivially
    true, and so the scenarios the logic layer treats as special stay that way."""

    def test_a_fixed_force_has_nothing_to_gather(self):
        for scenario in FIXED_FORCE:
            counts = total(scenario)
            for field in COUNT_FIELDS:
                with self.subTest(f"{scenario.name}.{field}"):
                    self.assertEqual(getattr(counts, field), 0)

    def test_every_other_scenario_has_gold_and_stone(self):
        for scenario in Age2ScenarioData:
            if scenario in FIXED_FORCE:
                continue
            with self.subTest(scenario.name):
                self.assertGreater(total(scenario).gold_count, 0)
                self.assertGreater(total(scenario).stone_count, 0)

    def test_every_other_scenario_has_some_food(self):
        for scenario in Age2ScenarioData:
            if scenario in FIXED_FORCE:
                continue
            with self.subTest(scenario.name):
                self.assertGreater(total(scenario).food_count, 0)

    def test_attila_4_is_the_fish_drought(self):
        """A dozen fish on the whole map. can_fish_easily has to come out False there, and this
        is the datum it rests on."""
        attila_4 = total(Age2ScenarioData.AP_ATTILA_4)
        drought = attila_4.shore_fish_count + attila_4.deep_fish_count
        attila_1 = total(Age2ScenarioData.AP_ATTILA_1)
        plenty = attila_1.shore_fish_count + attila_1.deep_fish_count
        self.assertLess(drought, 3000)
        self.assertGreater(plenty, drought * 5)

    def test_relics_are_where_we_think(self):
        with_relics = {scenario.name: total(scenario).relic_count
                       for scenario in Age2ScenarioData if total(scenario).relic_count}
        self.assertEqual(with_relics, {"AP_ATTILA_3": 2, "AP_ATTILA_4": 4, "AP_GENGHIS_5": 1})

    def test_no_map_has_an_oyster_or_a_whale_yet(self):
        """Both fields exist for scenarios not yet written. If this ever fails, a map gained
        one and the gold logic should start counting it."""
        for scenario in Age2ScenarioData:
            for tier, counts in scenario.resources.items():
                with self.subTest(f"{scenario.name}.{tier.name}"):
                    self.assertEqual(counts.oyster_count, 0)
                    self.assertEqual(counts.whale_count, 0)

    def test_only_scenarios_with_an_ally_use_the_ally_tier(self):
        """ALLY resolves to False_() for now, so anything parked there is unreachable. Attila 1
        has the Scythians and Attila 5 its own ally; no other scenario should be using it."""
        allied = {scenario.name for scenario in Age2ScenarioData
                  if any(getattr(scenario.resources[Tier.ALLY], field)
                         for field in COUNT_FIELDS)}
        self.assertEqual(allied, {"AP_ATTILA_1", "AP_ATTILA_5"})
