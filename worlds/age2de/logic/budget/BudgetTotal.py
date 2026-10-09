"""The one budget rule: is this location's place in its scenario's budget order in logic yet?"""
from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING, Any, override

from BaseClasses import CollectionState
from NetUtils import JSONMessagePart

from rule_builder.rules import False_, NestedRule, Rule

from ...generation.pools.BudgetPool import SAMPLED_RESOURCES
from ...items.Items import Resource
from ...locations.Buildings import Age2BuildingData
from ...locations.Scenarios import Age2ScenarioData
from ..custom_logic.ResourceAmount import contributors
from .BudgetItem import PricedLocation
from .BudgetOrder import CostWaiver, budget_order
from .BudgetSource import Bootstrap, Part, ScenarioResourceOrigin, ScenarioResourceOrigins
from .Need import Cost, Need, as_cost
from .Requirement import Requirement

if TYPE_CHECKING:
    from ... import Age2World

@dataclasses.dataclass(eq=False)
class ShownTotal:
    """One resource as an explanation shows it: how much, and whether it is covered - None when
    no state was given to check against."""
    resource: Resource
    amount: int
    covered: bool | None

@dataclasses.dataclass
class BudgetTotal(Rule["Age2World"], game="Age Of Empires II: Definitive Edition"):
    scenario: Age2ScenarioData
    location: PricedLocation

    @override
    def _instantiate(self, world: 'Age2World') -> Rule.Resolved:
        """Resolved once per seed and shared, like the scenario questions: the base's total sits
        in every has_base, and its seeds and source rules are not cheap to work out again."""
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
        order = budget_order(world.rules.logic.for_scenario(self.scenario), world)
        if order.running_total_for(self.location) is None:
            return False_().resolve(world)   # not in this scenario's order

        waivers = order.cost_waivers
        masks = range(1 << len(waivers))

        def on(mask: int) -> list[CostWaiver]:
            """The waivers this combination holds: one bit per waiver."""
            return [waiver for bit, waiver in enumerate(waivers) if mask >> bit & 1]

        needs: list[Need] = []
        costs: list[Cost] = []
        parts: list[tuple[tuple[Part, ...], ...]] = []
        for mask in masks:
            waived = frozenset(
                building for waiver in on(mask)
                    for building in waiver.buildings
            )
            dropped = frozenset(
                purchase for waiver in on(mask)
                    for purchase in waiver.purchases
            )
            need = order.running_total_for(self.location, dropped)
            requirement = Requirement(need, waived)
            needs.append(need)
            costs.append(as_cost(requirement.cost))
            parts.append(order.resource_origins.seed_parts(need, requirement, waived,
                                                           order.start_age))

        # Tuples throughout: a resolved rule has to hash. Its children were resolved once, by
        # the order: the waivers' rules, then every gather method's.
        return self.Resolved(
            (
                *(waiver.rule for waiver in waivers),
                *order.resource_origins.rules,
            ),
            tuple(needs),
            tuple(tuple(waiver.buildings) for waiver in waivers),
            order.resource_origins,
            tuple(parts),
            self.scenario,
            self.location,
            tuple((resource, contributors(resource)) for resource in SAMPLED_RESOURCES),
            tuple(costs),
            player=world.player,
            caching_enabled=False,
        )

    @override
    def __str__(self) -> str:
        return f"BudgetTotal({self.scenario.scenario_name}, {self.location.location_name})"

    class Resolved(NestedRule.Resolved):
        # Every field is a tuple, not a list: a resolved rule has to hash.
        needs: tuple[Need, ...]
        waived_buildings: tuple[tuple[Age2BuildingData, ...], ...]
        """The buildings each waiver stands up, one entry per waiver - per bit of the mask."""
        resource_origins: ScenarioResourceOrigins
        parts: tuple[tuple[tuple[Part, ...], ...], ...]
        scenario: Age2ScenarioData
        location: PricedLocation
        contributors: tuple[tuple[Resource, tuple[tuple[str, int], ...]], ...]
        costs: tuple[Cost, ...]

        skip_cache = True
        """Sums over the pile, which is no child; item_dependencies names every pile item
        instead."""

        # -- evaluating -----------------------------------------------------------------------

        def mask(self, state: CollectionState) -> int:
            waiver_rules = self.children[:len(self.waived_buildings)]
            return sum(
                1 << bit for bit, rule in enumerate(waiver_rules)
                    if rule(state)
            )

        def waived_now(self, state: CollectionState) -> frozenset[Age2BuildingData]:
            mask = self.mask(state)
            return frozenset(
                building for bit, buildings in enumerate(self.waived_buildings)
                    if mask >> bit & 1
                        for building in buildings
            )

        def usable(self, state: CollectionState) -> list[int]:
            """The dropsite choices whose gather method is switched on."""
            on = [rule(state) for rule in self.children[len(self.waived_buildings):]]
            return [
                index for index, choice in enumerate(self.resource_origins.choices)
                    if on[choice.rule]
            ]

        def sources_on(self, state: CollectionState) -> list[ScenarioResourceOrigin]:
            working = self.resource_origins.working(self.usable(state))
            return [
                origin for index, origin in enumerate(self.resource_origins.origins)
                    if index in working
            ]

        def allowance(self, state: CollectionState) -> dict[Resource, int]:
            origins = self.resource_origins
            return origins.income(origins.working(self.usable(state)))

        def bootstrap(self, state: CollectionState) -> Bootstrap | None:
            """The choices that pay for it, and the seeds they add to the total, if any do."""
            mask = self.mask(state)
            return self.resource_origins.bootstrap(
                self.pile(state),
                dict(self.costs[mask]),
                self.usable(state),
                self.parts[mask],
            )

        def pile(self, state: CollectionState) -> dict[Resource, int]:
            held = state.prog_items[self.player]
            return {
                resource: sum(held[name] * each for name, each in items)
                    for resource, items in self.contributors
            }

        def need(self, state: CollectionState | None) -> Need:
            return self.needs[0 if state is None else self.mask(state)]

        def requirement(self, state: CollectionState | None) -> Requirement:
            waived = frozenset() if state is None else self.waived_now(state)
            return Requirement(self.need(state), waived)

        @override
        def _evaluate(self, state: CollectionState) -> bool:
            mask = self.mask(state)
            pile, need = self.pile(state), dict(self.costs[mask])
            if all(pile[resource] >= amount for resource, amount in need.items()):
                return True   # before asking which sources are on
            return self.resource_origins.can_cover(
                pile,
                need,
                self.usable(state),
                self.parts[mask],
            )

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
                waived, sources_on, pile = [], [], {}
            else:
                waived = sorted(self.waived_now(state), key=int)
                sources_on = [
                    (origin.name, origin.resource, origin.allowance)
                        for origin in self.sources_on(state)
                ]
                pile = self.pile(state)

            return {
                "scenario": self.scenario.scenario_name,
                "requirement": dict(requirement.cost),
                "own": self.need(state).own_cost(),
                "building_entries": sorted(self.need(state).entry_buildings, key=int),
                "buildings_charged": list(requirement.buildings),
                "ages_charged": list(requirement.ages),
                "waived": waived,
                "sources_on": sources_on,
                "sources_used": self._used(state),
                "pile": pile,
            }

        def _used(self, state: CollectionState | None) -> list[str]:
            found = None if state is None else self.bootstrap(state)
            if found is None:
                return []
            return sorted({
                self.resource_origins.origins[self.resource_origins.choices[way].source].name
                    for way in found.choices
            })

        def _totals(self, state: CollectionState | None) -> list[ShownTotal]:
            need = dict(self.costs[0 if state is None else self.mask(state)])
            if state is None:
                return [
                    ShownTotal(resource, need[resource], None) for resource in SAMPLED_RESOURCES
                        if need.get(resource, 0) > 0
                ]

            found = self.bootstrap(state)
            if found is not None:   # the total with the seeds of the sources that paid for it
                return [
                    ShownTotal(resource, need.get(resource, 0) + found.seeds_added[resource], True)
                        for resource in SAMPLED_RESOURCES
                        if need.get(resource, 0) + found.seeds_added[resource] > 0
                ]

            pile, allowance = self.pile(state), self.allowance(state)
            return [
                ShownTotal(
                    resource,
                    need[resource],
                    pile[resource] + allowance[resource] >= need[resource],
                )
                    for resource in SAMPLED_RESOURCES
                        if need.get(resource, 0) > 0
            ]

        @override
        def explain_json(self, state: CollectionState | None = None) -> list[JSONMessagePart]:
            scenario = self.scenario.scenario_name
            parts: list[JSONMessagePart] = [
                {
                    "type": "text",
                    "text": f"{scenario}: starting pile + early gathering covers ",
                },
            ]
            for index, total in enumerate(self._totals(state)):
                if index:
                    parts.append({"type": "text", "text": ", "})
                text = f"{total.amount} {total.resource.name.lower()}"
                if total.covered is None:
                    parts.append({"type": "text", "text": text})
                else:
                    parts.append({
                        "type": "color",
                        "color": "green" if total.covered else "salmon",
                        "text": text,
                    })
            return parts

        @override
        def explain_str(self, state: CollectionState | None = None) -> str:
            totals = ", ".join(
                f"{amount} {resource.name.lower()}" for resource, amount, _ in self._totals(state)
            )
            scenario = self.scenario.scenario_name
            return f"{scenario}: starting pile + early gathering covers {totals}"

        @override
        def __str__(self) -> str:
            return self.explain_str()
