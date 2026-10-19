"""The counter table: which unit lines counter which."""

import unittest

from ..locations.UnitLines import Age2UnitLineData
from ..locations.connections.UnitCounters import LINE_TO_COUNTERS

class TestUnitLineIds(unittest.TestCase):

    def test_no_unit_line_id_is_an_alias(self):
        # An IntEnum member that repeats an id silently becomes the earlier member.
        self.assertEqual(len(Age2UnitLineData.__members__), len(list(Age2UnitLineData)))

class TestCounterTable(unittest.TestCase):

    def test_no_line_lists_a_counter_twice(self):
        for line, counters in LINE_TO_COUNTERS.items():
            with self.subTest(line.name):
                self.assertEqual(len(set(counters)), len(counters))

    def test_the_petard_does_not_counter_siege(self):
        siege_lines = (
            Age2UnitLineData.BOMBARD_CANNON_LINE,
            Age2UnitLineData.MANGONEL_LINE,
            Age2UnitLineData.SCORPION_LINE,
            Age2UnitLineData.TREBUCHET_LINE,
        )
        for line in siege_lines:
            with self.subTest(line.name):
                self.assertNotIn(Age2UnitLineData.PETARD_LINE, LINE_TO_COUNTERS[line])

    def test_the_petard_counters_the_mounted_trebuchet(self):
        self.assertIn(
            Age2UnitLineData.PETARD_LINE,
            LINE_TO_COUNTERS[Age2UnitLineData.MOUNTED_TREBUCHET_LINE],
        )

    def test_the_ram_counters_archers_and_trebuchets(self):
        rammed_lines = (
            Age2UnitLineData.ARCHER_LINE,
            Age2UnitLineData.CAVALRY_ARCHER_LINE,
            Age2UnitLineData.LONGBOWMAN_LINE,
            Age2UnitLineData.PLUMED_ARCHER_LINE,
            Age2UnitLineData.RATTAN_ARCHER_LINE,
            Age2UnitLineData.BALLISTA_ELEPHANT_LINE,
            Age2UnitLineData.TREBUCHET_LINE,
        )
        for line in rammed_lines:
            with self.subTest(line.name):
                self.assertIn(Age2UnitLineData.BATTERING_RAM_LINE, LINE_TO_COUNTERS[line])

    def test_lines_that_do_not_counter(self):
        not_countered_by = (
            (Age2UnitLineData.KNIGHT_LINE, Age2UnitLineData.THROWING_AXEMAN_LINE),
            (Age2UnitLineData.SCOUT_CAVALRY_LINE, Age2UnitLineData.SKIRMISHER_LINE),
            (Age2UnitLineData.MISSIONARY_LINE, Age2UnitLineData.MONK_LINE),
            (Age2UnitLineData.BATTERING_RAM_LINE, Age2UnitLineData.VILLAGER_MALE_LINE),
            (Age2UnitLineData.DEMOLITION_RAFT_LINE, Age2UnitLineData.ARCHER_LINE),
        )
        for line, counter in not_countered_by:
            with self.subTest(f"{line.name} by {counter.name}"):
                self.assertNotIn(counter, LINE_TO_COUNTERS[line])

    def test_lines_that_counter(self):
        countered_by = (
            (Age2UnitLineData.CATAPHRACT_LINE, Age2UnitLineData.ARCHER_LINE),
            (Age2UnitLineData.PETARD_LINE, Age2UnitLineData.BOYAR_LINE),
            (Age2UnitLineData.LEITIS_LINE, Age2UnitLineData.MISSIONARY_LINE),
            (Age2UnitLineData.DEMOLITION_RAFT_LINE, Age2UnitLineData.LONGBOAT_LINE),
            (Age2UnitLineData.DEMOLITION_RAFT_LINE, Age2UnitLineData.TURTLE_SHIP_LINE),
            (Age2UnitLineData.TREBUCHET_LINE, Age2UnitLineData.TREBUCHET_LINE),
        )
        for line, counter in countered_by:
            with self.subTest(f"{line.name} by {counter.name}"):
                self.assertIn(counter, LINE_TO_COUNTERS[line])

if __name__ == "__main__":
    unittest.main()
