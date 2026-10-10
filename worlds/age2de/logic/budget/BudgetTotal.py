"""The one budget rule: is this location's place in its scenario's budget order in logic yet?"""
from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING, Any, override

from BaseClasses import CollectionState
from NetUtils import JSONMessagePart

from rule_builder.rules import False_, NestedRule, Rule

from ...generation.pools.BudgetPool import SAMPLED_RESOURCES
from ...items.Items import Resource
from ...locations.Scenarios import Age2ScenarioData
from ..custom_logic.ResourceAmount import contributors
from .BudgetItem import BASE, PricedLocation
from .CostTable import CostTable
from .Need import Cost, Need
from .Requirement import Requirement

if TYPE_CHECKING:
    from ... import Age2World

@dataclasses.dataclass(frozen=True)
class Bill:
    """What a player is shown for one location: what it needs and what each part costs, on its
    own. Not its running total, and nothing about what earlier entries or waivers let off - an
    Archer and a Skirmisher both show the Archery Range they are made at."""
    lines: tuple[tuple[str, Cost], ...]

    @classmethod
    def of(cls, requirement: Requirement) -> Bill:
        need = requirement.need
        lines = [
            *((building.location_name, Need.as_cost(building.cost))
                for building in sorted(need.entry_buildings, key=int)),
            *((building.location_name, Need.as_cost(building.cost))
                for building in requirement.buildings),
            *((age.location_name, Need.as_cost(age.cost)) for age in requirement.ages),
            *((_label(price.identity), price.cost)
                for price in sorted(need.own_price, key=lambda price: str(price.identity))),
        ]
        return cls(tuple((label, cost) for label, cost in lines if cost))


def _label(identity: object) -> str:
    """A price's name as the player knows it: a tech, a unit line, the villager."""
    return getattr(identity, "location_name", None) or str(identity).title()

@dataclasses.dataclass
class BudgetTotal(Rule["Age2World"], game="Age Of Empires II: Definitive Edition"):
    scenario: Age2ScenarioData
    location: PricedLocation

    @override
    def _instantiate(self, world: 'Age2World') -> Rule.Resolved:
        """Resolved once per seed and shared, like the scenario questions: the base's total sits
        in every has_base, and its purchases and source rules are not cheap to work out again."""
        logic = world.rules.logic
        key = (self.scenario, self.location)
        if key not in logic.budget_totals:
            if key in logic.budget_totals_open:
                raise RecursionError(f"{self} asks for itself; the rule would never terminate")
            logic.budget_totals_open.add(key)
            try:
                logic.budget_totals[key] = self._resolve(world)
            finally:
                logic.budget_totals_open.discard(key)
        return logic.budget_totals[key]

    def _resolve(self, world: 'Age2World') -> Rule.Resolved:
        order = world.rules.logic.for_scenario(self.scenario).budget.order
        table = CostTable.for_location(order, self.location)
        if table is None:
            return False_().resolve(world)   # not in this scenario's order

        # Every playable scenario has an easy source of every resource (TestEveryScenarioCanLive),
        # and a fixed force has no order, so it never gets here. The base asks none: the easy
        # sources of gold and stone ask for the base themselves.
        economy = world.rules.logic.for_scenario(self.scenario).economy
        easy = () if self.location is BASE else tuple(
            (resource, economy.has_easy_source(resource).resolve(world))
                for resource in SAMPLED_RESOURCES
        )

        # What the player is shown: the location on its own, with nothing standing.
        bill = Bill.of(order.requirement([order.get_priced_item(self.location)]))

        # The waivers and the easy sources are the children, so they register as dependencies;
        # it evaluates them itself.
        return self.Resolved(
            (*table.waivers, *(rule for _, rule in easy)),
            table,
            self.scenario,
            self.location,
            tuple((resource, contributors(resource)) for resource in SAMPLED_RESOURCES),
            easy,
            bill,
            player=world.player,
            caching_enabled=False,
        )

    @override
    def __str__(self) -> str:
        return f"BudgetTotal({self.scenario.scenario_name}, {self.location.location_name})"

    class Resolved(NestedRule.Resolved):
        # Every field hashes: tuples, and records compared by identity.
        table: CostTable
        scenario: Age2ScenarioData
        location: PricedLocation
        contributors: tuple[tuple[Resource, tuple[tuple[str, int], ...]], ...]
        easy: tuple[tuple[Resource, Rule.Resolved], ...]
        """Each resource's easy source: while it holds, the total asks the pile for none of that
        resource. Empty for the base, which the pile alone pays for."""
        bill: Bill

        skip_cache = True
        """Sums over the pile, which is no child; item_dependencies names every pile item
        instead."""

        # -- evaluating -----------------------------------------------------------------------

        def pile(self, state: CollectionState) -> dict[Resource, int]:
            held = state.prog_items[self.player]
            return {
                resource: sum(held[name] * each for name, each in items)
                    for resource, items in self.contributors
            }

        def need(self, state: CollectionState | None) -> Need:
            return self.table.total(state).need

        def requirement(self, state: CollectionState | None) -> Requirement:
            return self.table.total(state).requirement

        def easy_source_holds(self, resource: Resource, state: CollectionState) -> bool:
            return any(each is resource and rule(state) for each, rule in self.easy)

        def covers(self, state: CollectionState) -> dict[Resource, bool]:
            """Each resource in the total: from the pile, or from an easy source of it."""
            pile = self.pile(state)
            return {
                resource: pile[resource] >= amount or self.easy_source_holds(resource, state)
                    for resource, amount in self.table.total(state).cost
            }

        @override
        def _evaluate(self, state: CollectionState) -> bool:
            return all(self.covers(state).values())

        @override
        def item_dependencies(self) -> dict[str, set[int]]:
            """Every pile item can move the sum. LocalStart narrows its candidates by this set."""
            deps = super().item_dependencies()
            for _, items in self.contributors:
                for name, _ in items:
                    deps.setdefault(name, set()).add(id(self))
            return deps

        # -- explaining -----------------------------------------------------------------------

        def breakdown(self, state: CollectionState | None = None) -> dict[str, Any]:
            """Everything the short explanation sums up, for a longer view to show."""
            requirement = self.requirement(state)
            if state is None:
                easy, pile = [], {}
            else:
                easy = [
                    resource for resource in SAMPLED_RESOURCES
                        if self.easy_source_holds(resource, state)
                ]
                pile = self.pile(state)

            return {
                "scenario": self.scenario.scenario_name,
                "bill": list(self.bill.lines),
                "requirement": dict(requirement.cost),
                "easy_sources": easy,
                "pile": pile,
            }

        def _json_parts(self, state: CollectionState | None) -> list[tuple[str, bool | None]]:
            """The bill as text, each amount with whether the rule covers its resource - None
            with no state to check against."""
            covers = {} if state is None else self.covers(state)
            parts: list[tuple[str, bool | None]] = [(f"{self.scenario.scenario_name}: ", None)]
            for line, (label, cost) in enumerate(self.bill.lines):
                parts.append((f"{', ' if line else ''}{label} (", None))
                for index, (resource, amount) in enumerate(cost):
                    if index:
                        parts.append((", ", None))
                    covered = None if state is None else covers.get(resource, True)
                    parts.append((f"{amount} {resource.name.lower()}", covered))
                parts.append((")", None))
            return parts

        @override
        def explain_json(self, state: CollectionState | None = None) -> list[JSONMessagePart]:
            return [
                {"type": "text", "text": text} if covered is None
                else {"type": "color", "color": "green" if covered else "salmon", "text": text}
                    for text, covered in self._json_parts(state)
            ]

        @override
        def explain_str(self, state: CollectionState | None = None) -> str:
            return "".join(text for text, _ in self._json_parts(state))

        @override
        def __str__(self) -> str:
            return self.explain_str()
