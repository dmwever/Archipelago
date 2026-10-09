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
from .BudgetItem import PricedLocation
from .CostTable import CostTable
from .Need import Need
from .Requirement import Requirement
from .ScenarioResourceOrigins import Bootstrap

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

        # The table's rules are the children, so they register as dependencies; it evaluates
        # them itself.
        return self.Resolved(
            table.rules,
            table,
            self.scenario,
            self.location,
            tuple((resource, contributors(resource)) for resource in SAMPLED_RESOURCES),
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

        skip_cache = True
        """Sums over the pile, which is no child; item_dependencies names every pile item
        instead."""

        # -- evaluating -----------------------------------------------------------------------

        def bootstrap(self, state: CollectionState) -> Bootstrap | None:
            """The choices that pay for it, and what their purchases add to the total, if any do."""
            total = self.table.total(state)
            return self.table.resource_origins.bootstrap(
                self.pile(state),
                dict(total.cost),
                self.table.usable(state),
                total.gather_method_purchases,
            )

        def pile(self, state: CollectionState) -> dict[Resource, int]:
            held = state.prog_items[self.player]
            return {
                resource: sum(held[name] * each for name, each in items)
                    for resource, items in self.contributors
            }

        def need(self, state: CollectionState | None) -> Need:
            return self.table.total(state).need

        def requirement(self, state: CollectionState | None) -> Requirement:
            total = self.table.total(state)
            return Requirement(total.need, total.waived)

        @override
        def _evaluate(self, state: CollectionState) -> bool:
            total = self.table.total(state)
            pile, need = self.pile(state), dict(total.cost)
            if all(pile[resource] >= amount for resource, amount in need.items()):
                return True   # before asking which sources are on
            return self.table.resource_origins.can_cover(
                pile,
                need,
                self.table.usable(state),
                total.gather_method_purchases,
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
                waived = sorted(self.table.total(state).waived, key=int)
                sources_on = [
                    (origin.name, origin.resource, origin.allowance)
                        for origin in self.table.sources_on(state)
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
            origins = self.table.resource_origins
            return sorted({
                origins.origins[origins.choices[way].source].name
                    for way in found.choices
            })

        def _totals(self, state: CollectionState | None) -> list[ShownTotal]:
            need = dict(self.table.total(state).cost)
            if state is None:
                return [
                    ShownTotal(resource, need[resource], None) for resource in SAMPLED_RESOURCES
                        if need.get(resource, 0) > 0
                ]

            found = self.bootstrap(state)
            if found is not None:   # the total with what the paying sources had to buy
                with_purchases = {
                    resource: need.get(resource, 0) + found.purchases_added[resource]
                        for resource in SAMPLED_RESOURCES
                }
                return [
                    ShownTotal(resource, amount, True)
                        for resource, amount in with_purchases.items()
                            if amount > 0
                ]

            pile, allowance = self.pile(state), self.table.allowance(state)
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

            holding = self.table.waivers_holding(state)
            if holding:
                parts.append({"type": "text", "text": " ("})
                for index, waiver in enumerate(holding):
                    if index:
                        parts.append({"type": "text", "text": "; "})
                    parts.extend(waiver.explain_json(state))
                parts.append({"type": "text", "text": ")"})
            return parts

        @override
        def explain_str(self, state: CollectionState | None = None) -> str:
            totals = ", ".join(
                f"{total.amount} {total.resource.name.lower()}" for total in self._totals(state)
            )
            scenario = self.scenario.scenario_name
            text = f"{scenario}: starting pile + early gathering covers {totals}"

            holding = self.table.waivers_holding(state)
            if holding:
                waived = "; ".join(waiver.explain_str(state) for waiver in holding)
                text += f" ({waived})"
            return text

        @override
        def __str__(self) -> str:
            return self.explain_str()
