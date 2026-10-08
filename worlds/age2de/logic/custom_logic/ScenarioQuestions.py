from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, override

from BaseClasses import CollectionState
from NetUtils import JSONMessagePart

from rule_builder.rules import Rule

from .SufficientRawResources import SufficientRawResources

from ...items.Items import Resource
from ...locations.Ages import Age2AgeData
from ...locations.Buildings import Age2BuildingData
from ...locations.Scenarios import Age2ScenarioData

if TYPE_CHECKING:
    from ... import Age2World
    from ...logic.ScenarioLogic import ScenarioLogic


@dataclass
class ScenarioQuestion(Rule["Age2World"], game="Age Of Empires II: Definitive Edition"):
    """A question about one scenario, answered once per seed and shared by everything that asks."""

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
        """The cache lives on Logic, which is the per-seed rule-building context."""
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
            """The child's dependencies, and this wrapper's own id alongside them."""
            return {name: ids | {id(self)} for name, ids in dependencies.items()}

        def _walked(self, kind: str, walk) -> dict[str, set[int]]:
            cache = getattr(self, "_walked_cache", None)
            if cache is None:
                cache = {}
                object.__setattr__(self, "_walked_cache", cache)
            found = cache.get(kind)
            if found is None:
                found = cache[kind] = self.mine(walk())
            return found

        @override
        def item_dependencies(self) -> dict[str, set[int]]:
            return self._walked("item", self.answer.item_dependencies)

        @override
        def region_dependencies(self) -> dict[str, set[int]]:
            return self._walked("region", self.answer.region_dependencies)

        @override
        def location_dependencies(self) -> dict[str, set[int]]:
            return self._walked("location", self.answer.location_dependencies)

        @override
        def entrance_dependencies(self) -> dict[str, set[int]]:
            return self._walked("entrance", self.answer.entrance_dependencies)

        @override
        def explain_json(self, state: CollectionState | None = None) -> list[JSONMessagePart]:
            return [{
                "type": "color",
                "color": "green" if state and self(state) else "salmon",
                "text": self.description,
            }]

        @override
        def explain_str(self, state: CollectionState | None = None) -> str:
            return self.description


@dataclass
class ScenarioCanBuild(ScenarioQuestion, game="Age Of Empires II: Definitive Edition"):
    """Whether this scenario can put this building up."""

    building: Age2BuildingData

    _WATER_BUILDINGS = frozenset({
        Age2BuildingData.DOCK,
        Age2BuildingData.HARBOR,
        Age2BuildingData.FISH_TRAP,
    })

    @override
    def key(self) -> tuple:
        return (type(self).__name__, self.scenario, self.building)

    @override
    def answer(self, scenario: 'ScenarioLogic') -> Rule:
        buildings = scenario.logic.buildings
        rule = (buildings.has_building_item(self.building)
                & scenario.has_vils()
                & scenario.ages.has_reached(self.building.age))
        prerequisite = buildings.prerequisite(self.building)
        if prerequisite is not None:
            rule = rule & scenario.has_building(prerequisite)
        if self.building in self._WATER_BUILDINGS:
            rule = rule & scenario.has_water_access()
        return rule

    @override
    def describe(self, scenario: Age2ScenarioData) -> str:
        building = self.building.location_name.removeprefix("Build ")
        article = "an" if building[0] in "AEIOU" else "a"
        return f"{scenario.scenario_name} can build {article} {building}"


@dataclass
class ScenarioHasReached(ScenarioQuestion, game="Age Of Empires II: Definitive Edition"):
    """Whether this scenario is at or past this age."""

    age: Age2AgeData

    @override
    def key(self) -> tuple:
        return (type(self).__name__, self.scenario, self.age)

    @override
    def answer(self, scenario: 'ScenarioLogic') -> Rule:
        return scenario.ages.can_reach(self.age) | scenario.ages.start_past(self.age)

    @override
    def describe(self, scenario: Age2ScenarioData) -> str:
        age = self.age.location_name.removeprefix("Reach ")
        return f"{scenario.scenario_name} has reached the {age}"


@dataclass
class ScenarioHasEasyResource(ScenarioQuestion, game="Age Of Empires II: Definitive Edition"):
    """Whether this scenario can bring a resource in freely: enough of it to keep paying."""

    resource: Resource

    @override
    def key(self) -> tuple:
        return (type(self).__name__, self.scenario, self.resource)

    @override
    def answer(self, scenario: 'ScenarioLogic') -> Rule:
        return (self._GATHERED_EASILY[self.resource](self, scenario)
                | scenario.starting_state.easy_resource_sources[self.resource]
                | scenario.economy.market_trades())

    def _food_easily(self, scenario: 'ScenarioLogic') -> Rule:
        economy = scenario.economy
        land = economy.tier_gates()
        raw_food = (
            *economy.tiered(economy.can_hunt(), "hunt_count", land),
            *economy.tiered(economy.can_herd(), "herd_count", land),
            *economy.tiered(economy.can_forage(), "bush_count", land),
            *economy.tiered(economy.can_fish_some(), "shore_fish_count",
                            economy.tier_gates("shoreline")),
            *economy.tiered(economy.can_fish_by_boat(), "deep_fish_count",
                            economy.tier_gates("afloat")),
        )

        return economy.endless_food() | SufficientRawResources(
            sources=raw_food, needed=scenario.scenario.demand.food)

    def _gold_easily(self, scenario: 'ScenarioLogic') -> Rule:
        economy = scenario.economy
        land, afloat = economy.tier_gates(), economy.tier_gates("afloat")
        raw_gold = (
            *economy.tiered(economy.can_mine_some(), "gold_count", land),
            *economy.tiered(economy.can_gather_oysters(), "oyster_count",
                            economy.tier_gates("shoreline")),
            *economy.tiered(economy.can_hunt_whales(), "whale_count", afloat),
        )

        return economy.ally_trade_gold() | (
            SufficientRawResources(sources=raw_gold, needed=scenario.scenario.demand.gold)
            & scenario.has_base() & self._at_scale(scenario, Age2BuildingData.MINING_CAMP))

    def _stone_easily(self, scenario: 'ScenarioLogic') -> Rule:
        economy = scenario.economy
        raw_stone = economy.tiered(economy.can_quarry_some(), "stone_count",
                                   economy.tier_gates())

        return (SufficientRawResources(sources=raw_stone,
                                       needed=scenario.scenario.demand.stone)
                & scenario.has_base() & self._at_scale(scenario, Age2BuildingData.MINING_CAMP))

    def _wood_easily(self, scenario: 'ScenarioLogic') -> Rule:
        return scenario.economy._can_get_wood_easily()

    def _at_scale(self, scenario: 'ScenarioLogic', camp: Age2BuildingData) -> Rule:
        return (scenario.buildings.can_build_building(camp)
                | scenario.buildings.can_build_multiple_tc())

    _GATHERED_EASILY = {
        Resource.WOOD: _wood_easily,
        Resource.FOOD: _food_easily,
        Resource.GOLD: _gold_easily,
        Resource.STONE: _stone_easily,
    }

    @override
    def describe(self, scenario: Age2ScenarioData) -> str:
        return f"{scenario.scenario_name} can easily gather {self.resource.name.lower()}"


def _question_identity(self: ScenarioQuestion.Resolved) -> int:
    """Hash a question by what it asks, not by the answer behind it."""
    return hash((type(self).__module__, self.rule_name, self.player, self.description,
                 id(self.answer)))


ScenarioQuestion.Resolved.__hash__ = _question_identity
