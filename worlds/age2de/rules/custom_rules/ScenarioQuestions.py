from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, override

from BaseClasses import CollectionState
from NetUtils import JSONMessagePart

from rule_builder.rules import Rule

from ...locations.Ages import Age2AgeData
from ...locations.Buildings import Age2BuildingData
from ...locations.Scenarios import Age2ScenarioData

if TYPE_CHECKING:
    from ... import Age2World
    from ...logic.ScenarioLogic import ScenarioLogic

GAME = "Age Of Empires II: Definitive Edition"


@dataclass
class ScenarioQuestion(Rule["Age2World"], game=GAME):
    """A question about one scenario, answered once per seed and shared by everything that asks.

    These carry **identifiers only**, so composing one costs nothing; the tree behind it is built
    when it first resolves. rule_builder interns resolved rules by structural hash, so duplicates
    collapse - but only after the walk that discovers they are duplicates, and the age chain asks
    the same questions from very many places: one seed did 1,067,060 resolve() calls to arrive at
    2,458 distinct rules, twenty seconds a world.

    Answering is not memoised for its own sake. It is memoised because the answer cannot differ:
    resolution depends on the world's options and on the scenario, and both are fixed by the time
    rules are built.
    """

    scenario: Age2ScenarioData

    def key(self) -> tuple:
        """Unresolved rules are unhashable - rule_builder's dataclasses set eq and so drop
        __hash__ - so the cache is keyed on the fields rather than on the rule."""
        return (type(self).__name__, self.scenario)

    def answer(self, scenario: 'ScenarioLogic') -> Rule:
        """The real rule, built from that scenario's own logic."""
        raise NotImplementedError

    def describe(self, scenario: Age2ScenarioData) -> str:
        """One line for the logic explanation, instead of the whole subtree behind it."""
        raise NotImplementedError

    def answered(self, world: 'Age2World') -> Rule.Resolved:
        """The cache lives on Logic, which is the per-seed rule-building context.

        Not on the world: a rule writing its own bookkeeping onto the World is this world's
        machinery leaking into the game's. Reading it back through `world.rules.logic` is the
        same shape as the documented example reading `world.some_precalculated_bool`.
        """
        logic = world.rules.logic
        key = self.key()
        answer = logic.scenario_answers.get(key)
        if answer is None:
            if key in logic.scenario_answers_open:
                raise RecursionError(f"{key} asks itself; the rule would never terminate")
            logic.scenario_answers_open.add(key)
            try:
                answer = self.answer(logic.for_scenario(self.scenario)).resolve(world)
            finally:
                logic.scenario_answers_open.discard(key)
            logic.scenario_answers[key] = answer
        return answer

    @override
    def _instantiate(self, world: 'Age2World') -> Rule.Resolved:
        return self.Resolved(
            self.answered(world),
            self.describe(self.scenario),
            player=world.player,
            caching_enabled=getattr(world, "rule_caching_enabled", False),
        )

    class Resolved(Rule.Resolved):
        answer: Rule.Resolved
        description: str

        # always_* are ClassVars on Rule.Resolved, and And/Or read them off each child to
        # short-circuit and to dedupe. A property shadows the inherited ClassVar for instance
        # access, which is what keeps a False_ answer collapsing its parent rather than surviving
        # as an opaque wrapper. Without these two the tree grows by 44%; with them, by 23%.
        @property
        def always_true(self) -> bool:
            return self.answer.always_true

        @property
        def always_false(self) -> bool:
            return self.answer.always_false

        @override
        def _evaluate(self, state: CollectionState) -> bool:
            return self.answer(state)

        def mine(self, dependencies: dict[str, set[int]]) -> dict[str, set[int]]:
            """The child's dependencies, and this wrapper's own id alongside them.

            Forwarding alone is not enough and fails loudly: results are cached under `id(self)`,
            and CachedRuleBuilderWorld.collect invalidates by the ids a rule registers. Hand back
            only the child's id and the wrapper's own cached False is never cleared - once false,
            false forever, and every location behind it becomes unreachable. That is a FillError
            in 170 tests, which is the lucky version of this mistake.
            """
            return {name: ids | {id(self)} for name, ids in dependencies.items()}

        @override
        def item_dependencies(self) -> dict[str, set[int]]:
            return self.mine(self.answer.item_dependencies())

        @override
        def region_dependencies(self) -> dict[str, set[int]]:
            return self.mine(self.answer.region_dependencies())

        @override
        def location_dependencies(self) -> dict[str, set[int]]:
            return self.mine(self.answer.location_dependencies())

        @override
        def entrance_dependencies(self) -> dict[str, set[int]]:
            return self.mine(self.answer.entrance_dependencies())

        @override
        def explain_json(self, state: CollectionState | None = None) -> list[JSONMessagePart]:
            """The reason this wrapper exists: one line rather than the subtree behind it."""
            return [{
                "type": "color",
                "color": "green" if state and self(state) else "salmon",
                "text": self.description,
            }]

        @override
        def explain_str(self, state: CollectionState | None = None) -> str:
            return self.description


@dataclass
class ScenarioCanBuild(ScenarioQuestion, game=GAME):
    """Whether this scenario can put this building up.

    The deepest of the questions: behind it are the villagers, the civilisation, the prerequisite
    building and the age - and the age asks for two buildings of the age below, which asks again.
    """

    building: Age2BuildingData

    @override
    def key(self) -> tuple:
        return (type(self).__name__, self.scenario, self.building)

    @override
    def answer(self, scenario: 'ScenarioLogic') -> Rule:
        return scenario.buildings.build_rule(self.building)

    @override
    def describe(self, scenario: Age2ScenarioData) -> str:
        building = self.building.location_name.removeprefix("Build ")
        return f"{scenario.scenario_name} can build a {building}"


@dataclass
class ScenarioHasReached(ScenarioQuestion, game=GAME):
    """Whether this scenario is at or past this age."""

    age: Age2AgeData

    @override
    def key(self) -> tuple:
        return (type(self).__name__, self.scenario, self.age)

    @override
    def answer(self, scenario: 'ScenarioLogic') -> Rule:
        return scenario.ages.reached_rule(self.age)

    @override
    def describe(self, scenario: Age2ScenarioData) -> str:
        age = self.age.location_name.removeprefix("Reach ")
        return f"{scenario.scenario_name} has reached the {age}"
