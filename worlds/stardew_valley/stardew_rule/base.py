from __future__ import annotations

from abc import ABC, abstractmethod
from collections import deque
from copy import copy
from itertools import chain
from typing import Tuple, Set, Optional, Dict, Hashable, Union, Iterable, List, Sized

from BaseClasses import CollectionState
from .explanation import RuleExplanation
from .fork import fork_per_player
from .literal import LiteralStardewRule, false_, true_
from .protocol import StardewRule

MISSING_ITEM = "THIS ITEM IS MISSING"


class BaseStardewRule(StardewRule, ABC):

    def __or__(self, other) -> StardewRule:
        if other is true_ or other is false_ or type(other) is Or:
            return other | self

        return Or(self, other)

    def __and__(self, other) -> StardewRule:
        if other is true_ or other is false_ or type(other) is And:
            return other & self

        return And(self, other)


class CombinableStardewRule(BaseStardewRule, ABC):

    @property
    @abstractmethod
    def combination_key(self) -> Hashable:
        ...

    @property
    @abstractmethod
    def value(self):
        ...

    def is_same_rule(self, other: CombinableStardewRule):
        return self.combination_key == other.combination_key

    def max(self, other: CombinableStardewRule) -> CombinableStardewRule:
        return max(self, other, key=lambda x: x.value)

    def __and__(self, other):
        if isinstance(other, CombinableStardewRule) and self.is_same_rule(other):
            return self.max(other)

        return super().__and__(other)

    def min(self, other: CombinableStardewRule) -> CombinableStardewRule:
        return min(self, other, key=lambda x: x.value)

    def __or__(self, other):
        if isinstance(other, CombinableStardewRule) and self.is_same_rule(other):
            return self.min(other)

        return super().__or__(other)


class Has(BaseStardewRule):
    item: str
    # For sure there is a better way than just passing all the rules everytime
    other_rules: Dict[str, StardewRule]

    def __init__(self, item: str, other_rules: Dict[str, StardewRule]):
        self.item = item
        self.other_rules = other_rules

    def __call__(self, state: CollectionState, *args) -> bool:
        return self.evaluate_while_simplifying(state, *args)[1]

    def evaluate_while_simplifying(self, state: CollectionState, *args) -> Tuple[StardewRule, bool]:
        return self.other_rules[self.item].evaluate_while_simplifying(state, *args)

    def explain(self, state: CollectionState, *args, expected=True) -> RuleExplanation:
        return RuleExplanation(self, state, *args, expected=expected, sub_rules=[self.other_rules[self.item]])

    def get_difficulty(self, *args):
        return self.other_rules[self.item].get_difficulty(*args) + 1

    def __str__(self):
        if self.item not in self.other_rules:
            return f"Has {self.item} -> {MISSING_ITEM}"
        return f"Has {self.item}"

    def __repr__(self):
        if self.item not in self.other_rules:
            return f"Has {self.item} -> {MISSING_ITEM}"
        return f"Has {self.item} -> {repr(self.other_rules[self.item])}"

    def __hash__(self):
        return hash(self.item)


class _SimplificationState:
    original_simplifiable_rules: Tuple[StardewRule, ...]

    rules_to_simplify: deque[StardewRule]
    simplified_rules: Set[StardewRule]
    locked: bool

    def __init__(self, simplifiable_rules: Tuple[StardewRule, ...], rules_to_simplify: Optional[deque[StardewRule]] = None,
                 simplified_rules: Optional[Set[StardewRule]] = None):
        if simplified_rules is None:
            simplified_rules = set()

        self.original_simplifiable_rules = simplifiable_rules
        self.rules_to_simplify = rules_to_simplify
        self.simplified_rules = simplified_rules
        self.locked = False

    @property
    def is_simplified(self):
        return self.rules_to_simplify is not None and not self.rules_to_simplify

    def short_circuit(self, complement: LiteralStardewRule):
        self.rules_to_simplify = deque()
        self.simplified_rules = {complement}

    def try_popleft(self):
        try:
            self.rules_to_simplify.popleft()
        except IndexError:
            pass

    def acquire_copy(self):
        state = copy(self)
        state.acquire()
        return state

    def merge(self, other: _SimplificationState):
        return _SimplificationState(self.original_simplifiable_rules + other.original_simplifiable_rules)

    def add(self, rule: StardewRule):
        return _SimplificationState(self.original_simplifiable_rules + (rule,))

    def acquire(self):
        """
        This just set a boolean to True and is absolutely not thread safe. It just works because AP is single-threaded.
        """
        if self.locked is True:
            return False

        self.locked = True
        return True

    def release(self):
        assert self.locked
        self.locked = False

    def __copy__(self):
        return _SimplificationState(self.original_simplifiable_rules, copy(self.rules_to_simplify), copy(self.simplified_rules))


class AggregatingStardewRule(BaseStardewRule, ABC):
    """
    Logic for both "And" and "Or" rules.
    """
    identity: LiteralStardewRule
    complement: LiteralStardewRule
    symbol: str

    combinable_rules: Dict[Hashable, CombinableStardewRule]
    simplification_state: _SimplificationState
    _last_short_circuiting_rule: Optional[StardewRule] = None

    def __init__(self, *rules: StardewRule, _combinable_rules=None, _simplification_state=None):
        if _combinable_rules is None:
            assert rules, f"Can't create an aggregating condition without rules"
            rules, _combinable_rules = self.split_rules(rules)
            _simplification_state = _SimplificationState(rules)

        self.combinable_rules = _combinable_rules
        self.simplification_state = _simplification_state

    @property
    def original_rules(self):
        return RepeatableChain(self.combinable_rules.values(), self.simplification_state.original_simplifiable_rules)

    @property
    def current_rules(self):
        if self.simplification_state.rules_to_simplify is None:
            return self.original_rules

        return RepeatableChain(self.combinable_rules.values(), self.simplification_state.simplified_rules, self.simplification_state.rules_to_simplify)

    @classmethod
    def split_rules(cls, rules: Union[Iterable[StardewRule]]) -> Tuple[Tuple[StardewRule, ...], Dict[Hashable, CombinableStardewRule]]:
        other_rules = []
        reduced_rules = {}
        for rule in rules:
            if isinstance(rule, CombinableStardewRule):
                key = rule.combination_key
                if key not in reduced_rules:
                    reduced_rules[key] = rule
                    continue

                reduced_rules[key] = cls.combine(reduced_rules[key], rule)
                continue

            if type(rule) is cls:
                other_rules.extend(rule.simplification_state.original_simplifiable_rules)  # noqa
                reduced_rules = cls.merge(reduced_rules, rule.combinable_rules)  # noqa
                continue

            other_rules.append(rule)

        return tuple(other_rules), reduced_rules

    @classmethod
    def merge(cls, left: Dict[Hashable, CombinableStardewRule], right: Dict[Hashable, CombinableStardewRule]) -> Dict[Hashable, CombinableStardewRule]:
        reduced_rules = dict(left)
        for key, rule in right.items():
            if key not in reduced_rules:
                reduced_rules[key] = rule
                continue

            reduced_rules[key] = cls.combine(reduced_rules[key], rule)

        return reduced_rules

    @classmethod
    def add_into(cls, rule: CombinableStardewRule, rules: Dict[Hashable, CombinableStardewRule]) -> Dict[Hashable, CombinableStardewRule]:
        rules = dict(rules)

        if rule.combination_key in rules:
            rules[rule.combination_key] = cls.combine(rule, rules[rule.combination_key])
        else:
            rules[rule.combination_key] = rule

        return rules

    @staticmethod
    @abstractmethod
    def combine(left: CombinableStardewRule, right: CombinableStardewRule) -> CombinableStardewRule:
        raise NotImplementedError

    def short_circuit_simplification(self):
        self.simplification_state.short_circuit(self.complement)
        self.combinable_rules = {}
        return self.complement, self.complement.value

    def short_circuit_evaluation(self, rule):
        self._last_short_circuiting_rule = rule
        return self, self.complement.value

    @fork_per_player
    def evaluate_while_simplifying(self, state: CollectionState, *args) -> Tuple[StardewRule, bool]:
        """
        The global idea here is the same as short-circuiting operators, applied to evaluation and rule simplification.
        """

        # Directly checking last rule that short-circuited, in case state has not changed.
        if self._last_short_circuiting_rule:
            if self._last_short_circuiting_rule(state, *args) is self.complement.value:
                return self.short_circuit_evaluation(self._last_short_circuiting_rule)
            self._last_short_circuiting_rule = None

        # Combinable rules are considered already simplified, so we evaluate them right away to go faster.
        for rule in self.combinable_rules.values():
            if rule(state, *args) is self.complement.value:
                return self.short_circuit_evaluation(rule)

        if self.simplification_state.is_simplified:
            # The rule is fully simplified, so now we can only evaluate.
            for rule in self.simplification_state.simplified_rules:
                if rule(state, *args) is self.complement.value:
                    return self.short_circuit_evaluation(rule)
            return self, self.identity.value

        return self.evaluate_while_simplifying_stateful(state, *args)

    def evaluate_while_simplifying_stateful(self, state: CollectionState, *args):
        local_state = self.simplification_state
        try:
            # Creating a new copy, so we don't modify the rules while we're already evaluating it. This can happen if a rule is used for an entrance and a
            # location. When evaluating a given rule what requires access to a region, the region cache can get an update. If it does, we could enter this rule
            # again. Since the simplification is stateful, the set of simplified rules can be modified while it's being iterated on, and cause a crash.
            #
            # After investigation, for millions of call to this method, copy were acquired 425 times.
            # Merging simplification state in parent call was deemed useless.
            if not local_state.acquire():
                local_state = local_state.acquire_copy()
                self.simplification_state = local_state

            # Evaluating what has already been simplified. First it will be faster than simplifying "new" rules, but we also assume that if we reach this point
            # and there are already are simplified rule, one of these rules has short-circuited, and might again, so we can leave early.
            for rule in local_state.simplified_rules:
                if rule(state, *args) is self.complement.value:
                    return self.short_circuit_evaluation(rule)

            # If the queue is None, it means we have not start simplifying. Otherwise, we will continue simplification where we left.
            if local_state.rules_to_simplify is None:
                rules_to_simplify = frozenset(local_state.original_simplifiable_rules)
                if self.complement in rules_to_simplify:
                    return self.short_circuit_simplification()
                local_state.rules_to_simplify = deque(rules_to_simplify)

            # Start simplification where we left.
            while local_state.rules_to_simplify:
                result = self.evaluate_rule_while_simplifying_stateful(local_state, state, *args)
                local_state.try_popleft()
                if result is not None:
                    return result

            # The whole rule has been simplified and evaluated without short-circuit.
            return self, self.identity.value
        finally:
            local_state.release()

    def evaluate_rule_while_simplifying_stateful(self, local_state: _SimplificationState, state: CollectionState, *args):
        simplified, value = local_state.rules_to_simplify[0].evaluate_while_simplifying(state, *args)

        # Identity is removed from the resulting simplification since it does not affect the result.
        if simplified is self.identity:
            return

        # If we find a complement here, we know the rule will always short-circuit, what ever the state.
        if simplified is self.complement:
            return self.short_circuit_simplification()
        # Keep the simplified rule to be reevaluated later.
        local_state.simplified_rules.add(simplified)

        # Now we use the value to short-circuit if it is the complement.
        if value is self.complement.value:
            return self.short_circuit_evaluation(simplified)

    def __str__(self):
        return f"({self.symbol.join(str(rule) for rule in self.original_rules)})"

    def __repr__(self):
        return f"({self.symbol.join(repr(rule) for rule in self.original_rules)})"

    def __eq__(self, other):
        return (isinstance(other, type(self)) and self.combinable_rules == other.combinable_rules and
                self.simplification_state.original_simplifiable_rules == self.simplification_state.original_simplifiable_rules)

    def __hash__(self):
        return hash((id(self.combinable_rules), self.simplification_state.original_simplifiable_rules))

    def __copy__(self):
        return type(self)(_combinable_rules=self.combinable_rules, _simplification_state=copy(self.simplification_state))

    def explain(self, state: CollectionState, *args, expected=True) -> RuleExplanation:
        return RuleExplanation(self, state, *args, expected=expected, sub_rules=self.original_rules)


class Or(AggregatingStardewRule):
    identity = false_
    complement = true_
    symbol = " | "

    def __call__(self, state: CollectionState, *args) -> bool:
        return self.evaluate_while_simplifying(state, *args)[1]

    def __or__(self, other):
        if other is true_ or other is false_:
            return other | self

        if isinstance(other, CombinableStardewRule):
            return Or(_combinable_rules=self.add_into(other, self.combinable_rules), _simplification_state=self.simplification_state)

        if type(other) is Or:
            return Or(_combinable_rules=self.merge(self.combinable_rules, other.combinable_rules),
                      _simplification_state=self.simplification_state.merge(other.simplification_state))

        return Or(_combinable_rules=self.combinable_rules, _simplification_state=self.simplification_state.add(other))

    @staticmethod
    def combine(left: CombinableStardewRule, right: CombinableStardewRule) -> CombinableStardewRule:
        return left.min(right)

    def get_difficulty(self, *args):
        return min(rule.get_difficulty(*args) for rule in self.original_rules)


class And(AggregatingStardewRule):
    identity = true_
    complement = false_
    symbol = " & "

    def __call__(self, state: CollectionState, *args) -> bool:
        return self.evaluate_while_simplifying(state, *args)[1]

    def __and__(self, other):
        if other is true_ or other is false_:
            return other & self

        if isinstance(other, CombinableStardewRule):
            return And(_combinable_rules=self.add_into(other, self.combinable_rules), _simplification_state=self.simplification_state)

        if type(other) is And:
            return And(_combinable_rules=self.merge(self.combinable_rules, other.combinable_rules),
                       _simplification_state=self.simplification_state.merge(other.simplification_state))

        return And(_combinable_rules=self.combinable_rules, _simplification_state=self.simplification_state.add(other))

    @staticmethod
    def combine(left: CombinableStardewRule, right: CombinableStardewRule) -> CombinableStardewRule:
        return left.max(right)

    def get_difficulty(self, *args):
        return max(rule.get_difficulty(*args) for rule in self.original_rules)


class Count(BaseStardewRule):
    count: int
    rules: List[StardewRule]
    rules_count: int
    _simplified: bool

    def __init__(self, count: int, rule: Union[StardewRule, Iterable[StardewRule]], *rules: StardewRule):
        rules_list: List[StardewRule]

        if isinstance(rule, Iterable):
            rules_list = [*rule]
        else:
            rules_list = [rule]

        if rules is not None:
            rules_list.extend(rules)

        assert rules_list, "Can't create a Count conditions without rules"
        assert len(rules_list) >= count, "Count need at least as many rules at the count"

        self.rules = rules_list
        self.count = count
        self.rules_count = len(rules_list)
        self._simplified = False

    def evaluate_while_simplifying(self, state: CollectionState, *args) -> Tuple[StardewRule, bool]:
        c = 0
        for i in range(self.rules_count):
            self.rules[i], value = self.rules[i].evaluate_while_simplifying(state, *args)
            if value:
                c += 1

            if c >= self.count:
                return self, True
            if c + self.rules_count - i < self.count:
                break

        return self, False

    def __call__(self, state: CollectionState, *args) -> bool:
        return self.evaluate_while_simplifying(state, *args)[1]

    def explain(self, state: CollectionState, *args, expected=True) -> RuleExplanation:
        return RuleExplanation(self, state, *args, expected=expected, sub_rules=self.rules)

    def get_difficulty(self, *args):
        self.rules = sorted(self.rules, key=lambda x: x.get_difficulty())
        # In an optimal situation, all the simplest rules will be true. Since the rules are sorted, we know that the most difficult rule we might have to do
        # is the one at the "self.count".
        return self.rules[self.count - 1].get_difficulty(*args)

    def __repr__(self):
        return f"Received {self.count} {repr(self.rules)}"


class RepeatableChain(Iterable, Sized):
    """
    Essentially a copy of what's in the core, with proper type hinting
    """

    def __init__(self, *iterable: Union[Iterable, Sized]):
        self.iterables = iterable

    def __iter__(self):
        return chain.from_iterable(self.iterables)

    def __bool__(self):
        return any(sub_iterable for sub_iterable in self.iterables)

    def __len__(self):
        return sum(len(iterable) for iterable in self.iterables)

    def __contains__(self, item):
        return any(item in it for it in self.iterables)
