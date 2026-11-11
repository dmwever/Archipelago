from __future__ import annotations

import dataclasses
import enum
from typing import TYPE_CHECKING, Callable, Iterable, Mapping, cast, override

from BaseClasses import CollectionState
from NetUtils import JSONMessagePart

from rule_builder.rules import False_, Or, Rule, True_

from ...items.Items import Resource

if TYPE_CHECKING:
    from ... import Age2World


class Strength(enum.IntEnum):
    SOME = 1
    AT_SCALE = 2


class RouteResource(enum.Enum):
    HOUSING = 5


Yield = Resource | RouteResource


@dataclasses.dataclass(frozen=True, eq=False)
class EconomyRoute:
    name: str
    yields: Mapping[Yield, Strength]
    leaf: Rule
    needs: Mapping[Yield, Strength] = dataclasses.field(default_factory=dict)

    def is_yielding_resource_at_strength(self, resource: Yield, strength: Strength) -> bool:
        return resource in self.yields and self.yields[resource] >= strength


@dataclasses.dataclass(frozen=True, eq=False)
class ResolvedEconomyRoute:
    name: str
    yields: Mapping[Yield, Strength]
    leaf: Rule.Resolved
    needs: Mapping[Yield, Strength]

    def is_yielding_resource_at_strength(self, resource: Yield, strength: Strength) -> bool:
        return resource in self.yields and self.yields[resource] >= strength


@dataclasses.dataclass()
class EconomyRoutes(Rule["Age2World"], game="Age Of Empires II: Definitive Edition"):
    routes: tuple[EconomyRoute, ...] = ()
    label: str = ""

    @override
    def _instantiate(self, world: "Age2World") -> Rule.Resolved:
        routes = tuple(
            ResolvedEconomyRoute(
                name=route.name,
                yields=dict(route.yields),
                leaf=route.leaf.resolve(world),
                needs=dict(route.needs),
            )
            for route in self.routes
        )
        return self.Resolved(
            routes,
            self.label,
            player=world.player,
            caching_enabled=getattr(world, "rule_caching_enabled", False),
        )

    @override
    def __str__(self) -> str:
        return f"EconomyRoutes({', '.join(route.name for route in self.routes)})"

    class Resolved(Rule.Resolved):
        routes: tuple[ResolvedEconomyRoute, ...]
        label: str
        possible: frozenset[int] = dataclasses.field(init=False, repr=False, compare=False)
        certain: frozenset[int] = dataclasses.field(init=False, repr=False, compare=False)
        yielding: dict[tuple, Rule.Resolved] = dataclasses.field(
            init=False,
            repr=False,
            compare=False,
        )
        running_rules: dict[int, Rule.Resolved] = dataclasses.field(
            init=False,
            repr=False,
            compare=False,
        )
        walked: dict[str, dict[str, set[int]]] = dataclasses.field(
            init=False,
            repr=False,
            compare=False,
        )

        def __post_init__(self) -> None:
            super().__post_init__()
            possible = self._least_fixpoint(
                range(len(self.routes)),
                lambda route: not route.leaf.always_false,
            )
            certain = self._least_fixpoint(
                range(len(self.routes)),
                lambda route: route.leaf.always_true,
            )
            object.__setattr__(self, "possible", possible)
            object.__setattr__(self, "certain", certain)
            object.__setattr__(self, "yielding", {})
            object.__setattr__(self, "running_rules", {})
            object.__setattr__(self, "walked", {})

        def _least_fixpoint(
            self,
            candidates: Iterable[int],
            holds: Callable[[ResolvedEconomyRoute], bool],
        ) -> frozenset[int]:
            running: set[int] = set()
            supplied: dict[Yield, Strength] = {}
            changed = True
            while changed:
                changed = False
                for index in candidates:
                    if index in running:
                        continue
                    route = self.routes[index]
                    if self.are_needs_met(route, supplied) and holds(route):
                        running.add(index)
                        supplied = self.supplied_by(running)
                        changed = True
            return frozenset(running)

        def supplied_by(self, running: Iterable[int]) -> dict[Yield, Strength]:
            supplied: dict[Yield, Strength] = {}
            for index in running:
                for resource, strength in self.routes[index].yields.items():
                    if resource not in supplied or supplied[resource] < strength:
                        supplied[resource] = strength
            return supplied

        def are_needs_met(
            self,
            route: ResolvedEconomyRoute,
            supplied: Mapping[Yield, Strength],
        ) -> bool:
            return all(
                resource in supplied and supplied[resource] >= strength
                for resource, strength in route.needs.items()
            )

        def running(self, state: CollectionState) -> frozenset[int]:
            return self._least_fixpoint(
                sorted(self.possible),
                lambda route: route.leaf(state),
            )

        def remember(self, state: CollectionState, running: frozenset[int]) -> None:
            if not self.caching_enabled:
                return
            player_results = cast(dict[int, bool], state.rule_builder_cache[self.player])
            for index, rule in self.running_rules.items():
                player_results[id(rule)] = index in running

        def route_running(self, index: int) -> Rule.Resolved:
            if index not in self.running_rules:
                self.running_rules[index] = EconomyRouteRunning.Resolved(
                    self,
                    index,
                    player=self.player,
                    caching_enabled=self.caching_enabled,
                )
            return self.running_rules[index]

        def yields(
            self,
            resource: Yield,
            strength: Strength,
            among: frozenset[str] | None = None,
        ) -> Rule.Resolved:
            key = (resource, strength, among)
            if key in self.yielding:
                return self.yielding[key]
            producers = [
                index for index in sorted(self.possible)
                if self.routes[index].is_yielding_resource_at_strength(resource, strength)
                and (among is None or self.routes[index].name in among)
            ]
            if any(index in self.certain for index in producers):
                answer = True_.Resolved(player=self.player, caching_enabled=self.caching_enabled)
            elif not producers:
                answer = False_.Resolved(player=self.player, caching_enabled=self.caching_enabled)
            elif len(producers) == 1:
                answer = self.route_running(producers[0])
            else:
                answer = Or.Resolved(
                    tuple(self.route_running(index) for index in producers),
                    player=self.player,
                    caching_enabled=self.caching_enabled,
                )
            self.yielding[key] = answer
            return answer

        @override
        def _evaluate(self, state: CollectionState) -> bool:
            running = self.running(state)
            self.remember(state, running)
            return bool(running)

        def dependencies(self, kind: str) -> dict[str, set[int]]:
            if kind in self.walked:
                return self.walked[kind]
            for index in self.possible:
                self.route_running(index)
            siblings = {id(self), *(id(rule) for rule in self.running_rules.values())}
            combined: dict[str, set[int]] = {}
            for index in self.possible:
                leaf = self.routes[index].leaf
                for name, ids in getattr(leaf, f"{kind}_dependencies")().items():
                    combined.setdefault(name, set()).update(ids, siblings)
            self.walked[kind] = combined
            return combined

        @override
        def item_dependencies(self) -> dict[str, set[int]]:
            return self.dependencies("item")

        @override
        def region_dependencies(self) -> dict[str, set[int]]:
            return self.dependencies("region")

        @override
        def location_dependencies(self) -> dict[str, set[int]]:
            return self.dependencies("location")

        @override
        def entrance_dependencies(self) -> dict[str, set[int]]:
            return self.dependencies("entrance")

        @override
        def explain_str(self, state: CollectionState | None = None) -> str:
            return self.label

        @override
        def __str__(self) -> str:
            return self.label


@dataclasses.dataclass()
class EconomyRoutesYield(Rule["Age2World"], game="Age Of Empires II: Definitive Edition"):
    economy: Rule
    resource: Yield
    strength: Strength
    among: frozenset[str] | None = None

    @override
    def _instantiate(self, world: "Age2World") -> Rule.Resolved:
        economy = cast(EconomyRoutes.Resolved, self.economy.resolve(world))
        return economy.yields(self.resource, self.strength, self.among)

    @override
    def __str__(self) -> str:
        return f"{self.economy} yields {self.resource.name.lower()} at {self.strength.name.lower()}"


@dataclasses.dataclass()
class EconomyRouteRunning(Rule["Age2World"], game="Age Of Empires II: Definitive Edition"):

    class Resolved(Rule.Resolved):
        economy: EconomyRoutes.Resolved
        index: int

        @property
        def route(self) -> ResolvedEconomyRoute:
            return self.economy.routes[self.index]

        @property
        def description(self) -> str:
            return f"{self.economy.label} runs {self.route.name}"

        @property
        def answer(self) -> Rule.Resolved:
            return self.route.leaf

        @override
        def _evaluate(self, state: CollectionState) -> bool:
            running = self.economy.running(state)
            self.economy.remember(state, running)
            return self.index in running

        @override
        def item_dependencies(self) -> dict[str, set[int]]:
            return self.economy.dependencies("item")

        @override
        def region_dependencies(self) -> dict[str, set[int]]:
            return self.economy.dependencies("region")

        @override
        def location_dependencies(self) -> dict[str, set[int]]:
            return self.economy.dependencies("location")

        @override
        def entrance_dependencies(self) -> dict[str, set[int]]:
            return self.economy.dependencies("entrance")

        @override
        def explain_json(self, state: CollectionState | None = None) -> list[JSONMessagePart]:
            return [
                {
                    "type": "color",
                    "color": "green" if state and self(state) else "salmon",
                    "text": self.description,
                },
            ]

        @override
        def explain_str(self, state: CollectionState | None = None) -> str:
            return self.description

        @override
        def __str__(self) -> str:
            return self.description


def _economy_identity(self: EconomyRoutes.Resolved) -> int:
    return id(self)


def _route_running_identity(self: EconomyRouteRunning.Resolved) -> int:
    return hash((type(self).__module__, self.rule_name, self.player, id(self.economy), self.index))


EconomyRoutes.Resolved.__hash__ = _economy_identity
EconomyRouteRunning.Resolved.__hash__ = _route_running_identity
