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
from .Need import Need
from .Requirement import Requirement

if TYPE_CHECKING:
    from ... import Age2World

@dataclasses.dataclass(eq=False)
class ShownTotal:
    """One resource as an explanation shows it: how much, whether it is covered - None when no
    state was given to check against - and whether an easy source is what covers it."""
    resource: Resource
    amount: int
    covered: bool | None
    by_easy_source: bool = False

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

        # The table's rules and the easy sources are the children, so they register as
        # dependencies; it evaluates them itself.
        return self.Resolved(
            (*table.rules, *(rule for _, rule in easy)),
            table,
            self.scenario,
            self.location,
            tuple((resource, contributors(resource)) for resource in SAMPLED_RESOURCES),
            easy,
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
            total = self.table.total(state)
            return Requirement(total.need, total.waived)

        def easy_source_holds(self, resource: Resource, state: CollectionState) -> bool:
            return any(each is resource and rule(state) for each, rule in self.easy)

        @override
        def _evaluate(self, state: CollectionState) -> bool:
            """Every resource in the total, from the pile or from an easy source of it."""
            pile = self.pile(state)
            return all(
                pile[resource] >= amount or self.easy_source_holds(resource, state)
                    for resource, amount in self.table.total(state).cost
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
                waived, easy, pile = [], [], {}
            else:
                waived = sorted(self.table.total(state).waived, key=int)
                easy = [
                    resource for resource in SAMPLED_RESOURCES
                        if self.easy_source_holds(resource, state)
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
                "easy_sources": easy,
                "pile": pile,
            }

        def _totals(self, state: CollectionState | None) -> list[ShownTotal]:
            cost = self.table.total(state).cost
            if state is None:
                return [ShownTotal(resource, amount, None) for resource, amount in cost]

            pile = self.pile(state)
            shown: list[ShownTotal] = []
            for resource, amount in cost:
                if pile[resource] >= amount:
                    shown.append(ShownTotal(resource, amount, True))
                else:
                    easy = self.easy_source_holds(resource, state)
                    shown.append(ShownTotal(resource, amount, easy, by_easy_source=easy))
            return shown

        @staticmethod
        def _shown(total: ShownTotal) -> str:
            text = f"{total.amount} {total.resource.name.lower()}"
            return f"{text} (easy source)" if total.by_easy_source else text

        @override
        def explain_json(self, state: CollectionState | None = None) -> list[JSONMessagePart]:
            scenario = self.scenario.scenario_name
            parts: list[JSONMessagePart] = [
                {"type": "text", "text": f"{scenario}: starting pile covers "},
            ]
            for index, total in enumerate(self._totals(state)):
                if index:
                    parts.append({"type": "text", "text": ", "})
                if total.covered is None:
                    parts.append({"type": "text", "text": self._shown(total)})
                else:
                    parts.append({
                        "type": "color",
                        "color": "green" if total.covered else "salmon",
                        "text": self._shown(total),
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
            totals = ", ".join(self._shown(total) for total in self._totals(state))
            scenario = self.scenario.scenario_name
            text = f"{scenario}: starting pile covers {totals}"

            holding = self.table.waivers_holding(state)
            if holding:
                waived = "; ".join(waiver.explain_str(state) for waiver in holding)
                text += f" ({waived})"
            return text

        @override
        def __str__(self) -> str:
            return self.explain_str()
