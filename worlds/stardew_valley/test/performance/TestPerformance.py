import os
import time
from dataclasses import dataclass
from statistics import mean, median, variance, stdev
from typing import List

from Fill import distribute_items_restrictive, balance_multiworld_progression
from worlds import AutoWorld
from .. import SVTestCase, minimal_locations_maximal_items, allsanity_options_without_mods, setup_multiworld, default_options

# [get_seed() for i in range(25)]
default_seeds = [26726304721450259037] * 25
number_generations = len(default_seeds)
acceptable_deviation = 4


@dataclass
class PerformanceResults:
    case: SVTestCase

    amount_of_players: int
    results: List[float]
    acceptable_mean: float

    def __repr__(self):
        size = size_name(self.amount_of_players)

        total_time = sum(self.results)
        mean_time = mean(self.results)
        median_time = median(self.results)
        stdev_time = stdev(self.results, mean_time)
        variance_time = variance(self.results, mean_time)

        return f"""Generated {len(self.results)} {size} multiworlds in {total_time:.4f} seconds. Average {mean_time:.4f} seconds (Acceptable: {self.acceptable_mean:.2f})
Mean: {mean_time:.4f} Median: {median_time:.4f} Stdeviation: {stdev_time:.4f} Variance: {variance_time:.4f} Deviation percent: {stdev_time / mean_time:.2%}"""


class SVPerformanceTestCase(SVTestCase):
    acceptable_time_per_player: float
    results: List[PerformanceResults]

    # Set False to run tests that take long
    skip_performance_tests: bool = True
    # Set False to not call the fill in the tests"""
    skip_fill: bool = True

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        performance_tests_key = "performance"
        if performance_tests_key in os.environ:
            cls.skip_performance_tests = not bool(os.environ[performance_tests_key])

        fill_tests_key = "fill"
        if fill_tests_key in os.environ:
            cls.skip_fill = not bool(os.environ[fill_tests_key])

    @classmethod
    def tearDownClass(cls) -> None:
        case = None
        for result in cls.results:
            if type(result.case) is not case:
                case = type(result.case)
                print(case.__name__)
            print(result)
        print()
        super().tearDownClass()

    def performance_test_multiworld(self, options):
        amount_of_players = len(options)
        acceptable_average_time = self.acceptable_time_per_player * amount_of_players
        total_time = 0
        all_times = []
        for i, seed in enumerate(default_seeds):
            with self.subTest(f"Seed: {seed}"):
                time_before = time.time()

                print(f"Starting world setup")
                multiworld = setup_multiworld(options, seed)
                if not self.skip_fill:
                    distribute_items_restrictive(multiworld)
                    AutoWorld.call_all(multiworld, 'post_fill')
                    if multiworld.players > 1:
                        balance_multiworld_progression(multiworld)

                time_after = time.time()
                elapsed_time = time_after - time_before
                total_time += elapsed_time
                all_times.append(elapsed_time)
                print(f"Multiworld {i + 1}/{number_generations} [{seed}] generated in {elapsed_time:.4f} seconds")
                # tester.assertLessEqual(elapsed_time, acceptable_average_time * acceptable_deviation)

        self.results.append(PerformanceResults(self, amount_of_players, all_times, acceptable_average_time))
        self.assertLessEqual(mean(all_times), acceptable_average_time)


def size_name(number_players):
    if number_players == 1:
        return "solo"
    elif number_players == 2:
        return "duo"
    elif number_players == 3:
        return "trio"
    return f"{number_players}-player"


class TestDefaultOptions(SVPerformanceTestCase):
    acceptable_time_per_player = 0.04
    options = default_options()
    results = []

    def test_solo(self):
        if self.skip_performance_tests:
            return

        number_players = 1
        multiworld_options = [self.options] * number_players
        self.performance_test_multiworld(multiworld_options)

    def test_duo(self):
        if self.skip_performance_tests:
            return

        number_players = 2
        multiworld_options = [self.options] * number_players
        self.performance_test_multiworld(multiworld_options)

    def test_5_player(self):
        if self.skip_performance_tests:
            return

        number_players = 5
        multiworld_options = [self.options] * number_players
        self.performance_test_multiworld(multiworld_options)

    def test_10_player(self):
        if self.skip_performance_tests:
            return

        number_players = 10
        multiworld_options = [self.options] * number_players
        self.performance_test_multiworld(multiworld_options)


class TestMinLocationMaxItems(SVPerformanceTestCase):
    acceptable_time_per_player = 0.08
    options = minimal_locations_maximal_items()
    results = []

    def test_solo(self):
        if self.skip_performance_tests:
            return

        number_players = 1
        multiworld_options = [self.options] * number_players
        self.performance_test_multiworld(multiworld_options)

    def test_duo(self):
        if self.skip_performance_tests:
            return

        number_players = 2
        multiworld_options = [self.options] * number_players
        self.performance_test_multiworld(multiworld_options)

    def test_5_player(self):
        if self.skip_performance_tests:
            return

        number_players = 5
        multiworld_options = [self.options] * number_players
        self.performance_test_multiworld(multiworld_options)

    def test_10_player(self):
        if self.skip_performance_tests:
            return

        number_players = 10
        multiworld_options = [self.options] * number_players
        self.performance_test_multiworld(multiworld_options)


class TestAllsanityWithoutMods(SVPerformanceTestCase):
    acceptable_time_per_player = 0.07
    options = allsanity_options_without_mods()
    results = []

    def test_solo(self):
        if self.skip_performance_tests:
            return

        number_players = 1
        multiworld_options = [self.options] * number_players
        self.performance_test_multiworld(multiworld_options)

    def test_duo(self):
        if self.skip_performance_tests:
            return

        number_players = 2
        multiworld_options = [self.options] * number_players
        self.performance_test_multiworld(multiworld_options)

    def test_5_player(self):
        if self.skip_performance_tests:
            return

        number_players = 5
        multiworld_options = [self.options] * number_players
        self.performance_test_multiworld(multiworld_options)

    def test_10_player(self):
        if self.skip_performance_tests:
            return

        number_players = 10
        multiworld_options = [self.options] * number_players
        self.performance_test_multiworld(multiworld_options)

# class TestAllsanityWithMods(SVTestCase):
#
#     def test_allsanity_with_mods_has_at_least_locations(self):
#         allsanity_options = allsanity_options_with_mods()
#         multiworld = setup_solo_multiworld(allsanity_options)
