"""The resource origins one scenario could bring in, and the search for a set that pays for a
running total."""
from __future__ import annotations

import dataclasses
import itertools
from typing import TYPE_CHECKING, Iterable, Sequence

from rule_builder.rules import Rule

from ...generation.pools.BudgetPool import SAMPLED_RESOURCES
from ...items.Items import Resource
from ...locations.Ages import Age2AgeData
from ...locations.Buildings import Age2BuildingData
from .BudgetOrigin import RESOURCE_ORIGINS, ResourceOrigin
from .GatherMethodPurchase import GatherMethodPurchase
from .Need import Need
from .Requirement import Requirement

if TYPE_CHECKING:
    from ... import Age2World
    from ..ScenarioLogic import ScenarioLogic

@dataclasses.dataclass(frozen=True, eq=False)
class ResolvedGatherMethod:
    """One way to work a source in one scenario: its rule, already resolved, and its need."""
    rule: Rule.Resolved
    need: Need

@dataclasses.dataclass(frozen=True, eq=False)
class ScenarioResourceOrigin:
    """A resource origin as one scenario could work it: what it brings in there, and each gather
    method it could use - the method's rule, already resolved, and its need."""
    origin: ResourceOrigin
    allowance: int
    gather_methods: tuple[ResolvedGatherMethod, ...]

    @property
    def name(self) -> str:
        return self.origin.name

    @property
    def resource(self) -> Resource:
        return self.origin.resource

@dataclasses.dataclass(frozen=True, eq=False)
class DropsiteChoice:
    """One gather method with one pick of dropsite, by index: its origin, and the method's rule
    among ScenarioResourceOrigins.rules; then its need, and the buildings picked."""
    source: int
    rule: int
    need: Need
    site: tuple[Age2BuildingData, ...]

    @staticmethod
    def sites(method_need: Need) -> list[tuple[Age2BuildingData, ...]]:
        """Each way to put the method's buildings up: one pick from each of its building
        choices."""
        groups = sorted(method_need.building_choices, key=lambda group: tuple(map(int, group)))
        return list(itertools.product(*groups))

@dataclasses.dataclass(frozen=True, eq=False)
class Bootstrap:
    """What paid for a total: the choices brought in, and what their purchases added to it."""
    choices: frozenset[int]
    purchases_added: dict[Resource, int]

@dataclasses.dataclass(frozen=True, eq=False)
class ScenarioResourceOrigins:
    """Every resource origin one scenario could bring in, each gather method it could use there,
    and each pick of dropsite for those. Frozen and tupled throughout: a resolved budget total
    keeps it, and it has to hash. It hashes by identity: there is one per scenario, shared by
    every budget total there, and hashing its contents for each would be slow. It keeps the
    scenario's start age, not its ScenarioBudgetLogic: a resolved rule outlives its world, and
    holding the budget logic would hold the world with it."""
    start_age: Age2AgeData
    origins: tuple[ScenarioResourceOrigin, ...]
    choices: tuple[DropsiteChoice, ...]
    """Each gather method once per pick of dropsite: what the search brings in, one at a time."""

    @classmethod
    def from_scenario(
        cls,
        scenario: ScenarioLogic,
        world: Age2World,
    ) -> ScenarioResourceOrigins:
        origins: list[ScenarioResourceOrigin] = []

        for origin in RESOURCE_ORIGINS:
            methods: list[ResolvedGatherMethod] = []
            for method in origin.gather_methods:
                resolved = method.rule(scenario.economy).resolve(world)
                if not resolved.always_false:
                    methods.append(
                        ResolvedGatherMethod(resolved, scenario.budget.settle(method.need))
                    )

            allowance = origin.allowance_in_scenario(scenario.scenario)
            if methods and allowance:
                origins.append(
                    ScenarioResourceOrigin(origin, allowance, tuple(methods))
                )

        choices: list[DropsiteChoice] = []
        rule_index = 0   # where the method's rule sits in rules
        for index, origin in enumerate(origins):
            for method in origin.gather_methods:
                choices += [
                    DropsiteChoice(index, rule_index, method.need, site)
                        for site in DropsiteChoice.sites(method.need)
                ]
                rule_index += 1

        return cls(scenario.budget.start_age, tuple(origins), tuple(choices))

    @property
    def rules(self) -> list[Rule.Resolved]:
        """Every gather method's rule, flat, in the order DropsiteChoice.rule counts them."""
        return [
            method.rule for origin in self.origins
                for method in origin.gather_methods
        ]

    @property
    def every_choice(self) -> list[int]:
        return list(range(len(self.choices)))

    def working(self, usable: Iterable[int]) -> set[int]:
        """The origins these choices bring in."""
        return {self.choices[choice].source for choice in usable}

    def income(self, working: Iterable[int]) -> dict[Resource, int]:
        """What the origins at these indices bring in, per resource."""
        total = dict.fromkeys(SAMPLED_RESOURCES, 0)
        for index in working:
            origin = self.origins[index]
            total[origin.resource] += origin.allowance
        return total

    def allowance(self) -> dict[Resource, int]:
        """What every origin together brings in."""
        return self.income(range(len(self.origins)))

    def gather_method_purchases(
        self,
        running_total_need: Need,
        requirement: Requirement,
        waived: frozenset[Age2BuildingData],
    ) -> tuple[tuple[GatherMethodPurchase, ...], ...]:
        """What each choice's gather method buys, against this running total."""
        return tuple(
            GatherMethodPurchase.for_running_total(
                choice.need,
                choice.site,
                running_total_need,
                requirement,
                waived,
                self.start_age,
            )
                for choice in self.choices
        )

    def can_cover(
        self,
        pile: dict[Resource, int],
        need: dict[Resource, int],
        usable: list[int],
        purchases: Sequence[tuple[GatherMethodPurchase, ...]],
    ) -> bool:
        """Whether the pile, and the origins it can bring in, cover the need."""
        if all(pile[resource] >= amount for resource, amount in need.items()):
            return True

        most = self.income(self.working(usable))
        if any(pile[resource] + most[resource] < amount for resource, amount in need.items()):
            return False   # purchases only ever add to the total

        return self.bootstrap(pile, need, usable, purchases) is not None

    def bootstrap(
        self,
        pile: dict[Resource, int],
        need: dict[Resource, int],
        usable: list[int],
        purchases: Sequence[tuple[GatherMethodPurchase, ...]],
    ) -> Bootstrap | None:
        """Bring origins in one at a time, each once its purchases are paid for out of the pile
        and what the origins already working bring in, trying every order. The first set that
        covers the need and its own purchases is the answer. A set's funds do not depend on the
        order it was reached in, so each set is looked at once."""
        most = self.income(self.working(usable))
        stack: list[frozenset[int]] = [frozenset()]
        seen: set[frozenset[int]] = set()

        while stack:
            chosen = stack.pop()
            if chosen in seen:
                continue
            seen.add(chosen)

            funded: dict[object, GatherMethodPurchase] = {}
            for choice in chosen:
                for purchase in purchases[choice]:
                    funded[purchase.identity] = purchase

            spent = dict.fromkeys(SAMPLED_RESOURCES, 0)
            extra = dict.fromkeys(SAMPLED_RESOURCES, 0)
            for purchase in funded.values():
                for resource, amount in purchase.cost:
                    spent[resource] += amount
                    if not purchase.already_charged:
                        extra[resource] += amount

            working = self.working(chosen)
            income_now = self.income(working)
            if all(
                pile[resource] + income_now[resource] >= need.get(resource, 0) + extra[resource]
                    for resource in SAMPLED_RESOURCES
            ):
                return Bootstrap(chosen, extra)
            if any(
                pile[resource] + most[resource] < need.get(resource, 0) + extra[resource]
                    for resource in SAMPLED_RESOURCES
            ):
                continue   # not even every source switched on could cover what this set bought

            for choice in usable:
                if self.choices[choice].source in working:
                    continue
                cost = dict.fromkeys(SAMPLED_RESOURCES, 0)
                for purchase in purchases[choice]:
                    if purchase.identity not in funded:
                        for resource, amount in purchase.cost:
                            cost[resource] += amount
                if all(
                    pile[resource] + income_now[resource] - spent[resource] >= cost[resource]
                        for resource in SAMPLED_RESOURCES
                ):
                    stack.append(chosen | {choice})

        return None
