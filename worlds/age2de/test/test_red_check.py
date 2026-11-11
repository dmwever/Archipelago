import unittest

from ..tools.red_check import verdict

TEST = "worlds/age2de/test/test_seed_items.py::TestStartingWoodSumsToAThousand"
CASE = f"{TEST}::test_every_combination_of_market_and_partner_trade"

class TestVerdictReadsSubtestFailures(unittest.TestCase):

    def test_a_subtest_with_spaces_in_its_parameters_is_red(self):
        output = f"SUBFAILED(market_trade=1, partner_trade=1) {CASE} - AssertionError\n"
        self.assertEqual("red", verdict(TEST, output))

    def test_a_subtest_with_nested_brackets_in_its_parameters_is_red(self):
        output = f"SUBFAILED(other={{'switches': ('Starting Market Wood',)}}) {CASE}\n"
        self.assertEqual("red", verdict(TEST, output))

    def test_a_square_bracketed_subtest_is_red(self):
        self.assertEqual("red", verdict(TEST, f"SUBFAILED[case 1] {CASE}\n"))

    def test_a_failed_test_is_red(self):
        self.assertEqual("red", verdict(TEST, f"FAILED {CASE} - AssertionError\n"))

    def test_another_tests_subtest_failure_is_not_this_ones(self):
        output = "SUBFAILED(x=1, y=2) worlds/age2de/test/test_other.py::TestOther::test_it\n"
        self.assertEqual("GREEN", verdict(TEST, output))

    def test_a_pass_is_green(self):
        self.assertEqual("GREEN", verdict(TEST, f"PASSED {CASE}\n"))

if __name__ == "__main__":
    unittest.main()
