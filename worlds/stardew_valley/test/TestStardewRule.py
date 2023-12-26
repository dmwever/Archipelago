import unittest
from unittest.mock import MagicMock, Mock

from ..stardew_rule import Received, And, Or, HasProgressionPercent, false_, true_

any_collection_state = MagicMock()
any_context = MagicMock()


class TestSimplification(unittest.TestCase):
    """
    Those feature of simplifying the rules when they are built have proven to improve the fill speed considerably.
    """

    def test_simplify_and_and_and(self):
        rule = And(Received('Summer', 0), Received('Fall', 0)) & And(Received('Winter', 0), Received('Spring', 0))

        self.assertEqual(And(Received('Summer', 0), Received('Fall', 0), Received('Winter', 0), Received('Spring', 0)), rule)

    def test_simplify_and_in_and(self):
        rule = And(And(Received('Summer', 0), Received('Fall', 0)), And(Received('Winter', 0), Received('Spring', 0)))
        self.assertEqual(And(Received('Summer', 0), Received('Fall', 0), Received('Winter', 0), Received('Spring', 0)), rule)

    def test_simplify_duplicated_and(self):
        # This only works because "Received"s are combinable.
        rule = And(And(Received('Summer', 0), Received('Fall', 0)), And(Received('Summer', 0), Received('Fall', 0)))
        self.assertEqual(And(Received('Summer', 0), Received('Fall', 0)), rule)

    def test_simplify_or_or_or(self):
        rule = Or(Received('Summer', 0), Received('Fall', 0)) | Or(Received('Winter', 0), Received('Spring', 0))
        self.assertEqual(Or(Received('Summer', 0), Received('Fall', 0), Received('Winter', 0), Received('Spring', 0)), rule)

    def test_simplify_or_in_or(self):
        rule = Or(Or(Received('Summer', 0), Received('Fall', 0)), Or(Received('Winter', 0), Received('Spring', 0)))
        self.assertEqual(Or(Received('Summer', 0), Received('Fall', 0), Received('Winter', 0), Received('Spring', 0)), rule)

    def test_simplify_duplicated_or(self):
        rule = Or(Or(Received('Summer', 0), Received('Fall', 0)), Or(Received('Summer', 0), Received('Fall', 0)))
        self.assertEqual(Or(Received('Summer', 0), Received('Fall', 0)), rule)


class TestHasProgressionPercentSimplification(unittest.TestCase):
    def test_has_progression_percent_and_uses_max(self):
        rule = HasProgressionPercent(20) & HasProgressionPercent(10)
        self.assertEqual(rule, HasProgressionPercent(20))

    def test_has_progression_percent_or_uses_min(self):
        rule = HasProgressionPercent(20) | HasProgressionPercent(10)
        self.assertEqual(rule, HasProgressionPercent(10))

    def test_and_between_progression_percent_and_other_progression_percent_uses_max(self):
        cases = [
            And(HasProgressionPercent(10)) & HasProgressionPercent(20),
            HasProgressionPercent(10) & And(HasProgressionPercent(20)),
            And(HasProgressionPercent(20)) & And(HasProgressionPercent(10)),
        ]
        for i, case in enumerate(cases):
            with self.subTest(f"{i} {repr(case)}"):
                self.assertEqual(case, And(HasProgressionPercent(20)))

    def test_or_between_progression_percent_and_other_progression_percent_uses_max(self):
        cases = [
            Or(HasProgressionPercent(10)) | HasProgressionPercent(20),
            HasProgressionPercent(10) | Or(HasProgressionPercent(20)),
            Or(HasProgressionPercent(20)) | Or(HasProgressionPercent(10))
        ]
        for i, case in enumerate(cases):
            with self.subTest(f"{i} {repr(case)}"):
                self.assertEqual(case, Or(HasProgressionPercent(10)))


class TestEvaluateWhileSimplifying(unittest.TestCase):
    def test_propagate_evaluate_while_simplifying(self):
        expected_result = True
        other_rule = MagicMock()
        other_rule.evaluate_while_simplifying = Mock(return_value=(other_rule, expected_result))
        rule = And(Or(other_rule))

        _, actual_result = rule.evaluate_while_simplifying(any_collection_state, any_context)

        other_rule.evaluate_while_simplifying.assert_called_with(any_collection_state, any_context)
        self.assertEqual(expected_result, actual_result)

    def test_return_complement_when_its_found(self):
        expected_simplified = false_
        expected_result = False
        rule = And(expected_simplified)

        actual_simplified, actual_result = rule.evaluate_while_simplifying(any_collection_state, any_context)

        self.assertEqual(expected_result, actual_result)
        self.assertEqual(expected_simplified, actual_simplified)

    def test_short_circuit_when_complement_found(self):
        other_rule = MagicMock()
        rule = Or(true_, )

        rule.evaluate_while_simplifying(any_collection_state, any_context)

        other_rule.evaluate_while_simplifying.assert_not_called()

    def test_short_circuit_when_combinable_rules_is_false(self):
        other_rule = MagicMock()
        rule = And(HasProgressionPercent(10), other_rule)

        rule.evaluate_while_simplifying(any_collection_state, any_context)

        other_rule.evaluate_while_simplifying.assert_not_called()

    def test_identity_is_removed_from_other_rules(self):
        rule = Or(false_, HasProgressionPercent(10))

        simplified, _ = rule.evaluate_while_simplifying(any_collection_state, any_context)

        self.assertEqual(1, len(simplified.current_rules))
        self.assertIn(HasProgressionPercent(10), simplified.current_rules)

    def test_complement_replaces_combinable_rules(self):
        rule = Or(HasProgressionPercent(10), true_)

        rule.evaluate_while_simplifying(any_collection_state, any_context)

        self.assertTrue(rule.current_rules)

    def test_simplifying_to_complement_propagates_complement(self):
        expected_simplified = true_
        expected_result = True
        rule = Or(Or(expected_simplified), HasProgressionPercent(10))

        actual_simplified, actual_result = rule.evaluate_while_simplifying(any_collection_state, any_context)

        self.assertEqual(expected_result, actual_result)
        self.assertEqual(expected_simplified, actual_simplified)
        self.assertTrue(rule.current_rules)

    def test_already_simplified_rules_are_not_simplified_again(self):
        other_rule = MagicMock()
        other_rule.evaluate_while_simplifying = Mock(return_value=(other_rule, False))
        rule = Or(other_rule, HasProgressionPercent(10))

        rule.evaluate_while_simplifying(any_collection_state, any_context)
        other_rule.assert_not_called()
        other_rule.evaluate_while_simplifying.reset_mock()

        rule.evaluate_while_simplifying(any_collection_state, any_context)
        other_rule.assert_called_with(any_collection_state, any_context)
        other_rule.evaluate_while_simplifying.assert_not_called()

    def test_continue_simplification_after_short_circuited(self):
        a_rule = MagicMock()
        a_rule.evaluate_while_simplifying = Mock(return_value=(a_rule, False))
        another_rule = MagicMock()
        another_rule.evaluate_while_simplifying = Mock(return_value=(another_rule, False))
        rule = And(a_rule, another_rule)

        rule.evaluate_while_simplifying(any_collection_state, any_context)
        # This test is completely messed up because sets are used internally and order of the rules cannot be ensured.
        not_yet_simplified, already_simplified = (another_rule, a_rule) if a_rule.evaluate_while_simplifying.called else (a_rule, another_rule)
        not_yet_simplified.evaluate_while_simplifying.assert_not_called()
        already_simplified.return_value = True

        rule.evaluate_while_simplifying(any_collection_state, any_context)
        not_yet_simplified.evaluate_while_simplifying.assert_called_with(any_collection_state, any_context)


class TestEvaluateWhileSimplifyingDoubleCalls(unittest.TestCase):
    """
    So, there is a situation where a rule kind of calls itself while it's being evaluated, because its evaluation triggers a region cache refresh.

    The region cache check every entrance, so if a rule is also used in an entrances, it can be reevaluated.

    For instance, but not limited to
    Has Melon -> (Farm & Summer) | Greenhouse -> Greenhouse triggers an update of the region cache
        -> Every entrance are evaluated, for instance "can start farming" -> Look that any crop can be grown (calls Has Melon).
    """

    def test_nested_call_in_the_internal_rule_being_evaluated_does_check_the_internal_rule(self):
        internal_rule = MagicMock()
        rule = Or(internal_rule)

        called_once = False
        internal_call_result = None

        def first_call_to_internal_rule(state, context):
            nonlocal internal_call_result
            nonlocal called_once
            if called_once:
                return internal_rule, True
            called_once = True

            _, internal_call_result = rule.evaluate_while_simplifying(state, context)
            internal_rule.evaluate_while_simplifying = Mock(return_value=(internal_rule, True))
            return internal_rule, True

        internal_rule.evaluate_while_simplifying = first_call_to_internal_rule

        rule.evaluate_while_simplifying(any_collection_state, any_context)

        self.assertTrue(called_once)
        self.assertTrue(internal_call_result)

    def test_nested_call_to_already_simplified_rule_does_not_steal_rule_to_simplify_from_parent_call(self):
        an_internal_rule = MagicMock()
        an_internal_rule.evaluate_while_simplifying = Mock(return_value=(an_internal_rule, True))
        another_internal_rule = MagicMock()
        another_internal_rule.evaluate_while_simplifying = Mock(return_value=(another_internal_rule, True))
        rule = Or(an_internal_rule, another_internal_rule)

        rule.evaluate_while_simplifying(any_collection_state, any_context)
        # This test is completely messed up because sets are used internally and order of the rules cannot be ensured.
        if an_internal_rule.evaluate_while_simplifying.called:
            not_yet_simplified, already_simplified = another_internal_rule, an_internal_rule
        else:
            not_yet_simplified, already_simplified = an_internal_rule, another_internal_rule

        called_once = False
        internal_call_result = None

        def call_to_already_simplified(state, context):
            nonlocal internal_call_result
            nonlocal called_once
            if called_once:
                return False
            called_once = True

            _, internal_call_result = rule.evaluate_while_simplifying(state, context)
            return False

        already_simplified.side_effect = call_to_already_simplified
        not_yet_simplified.return_value = True

        _, actual_result = rule.evaluate_while_simplifying(any_collection_state, any_context)

        self.assertTrue(called_once)
        self.assertTrue(internal_call_result)
        self.assertTrue(actual_result)
