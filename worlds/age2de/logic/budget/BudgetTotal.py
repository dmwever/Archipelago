"""The one budget rule: is this location's place in its scenario's budget order in logic yet?"""
from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING, Any, override

from BaseClasses import CollectionState
from NetUtils import JSONMessagePart

from rule_builder.rules import False_, NestedRule, Rule

from ...generation.pools.BudgetPool import SAMPLED_RESOURCES, PricedLocation
from ...items.Items import Resource
from ...locations.Buildings import Age2BuildingData
from ...locations.Scenarios import Age2ScenarioData
from ..custom_logic.ResourceAmount import contributors
from .BudgetOrder import Switch, budget_order
from .Need import Need
from .Requirement import Requirement, required

if TYPE_CHECKING:
    from ... import Age2World


@dataclasses.dataclass
class BudgetTotal(Rule["Age2World"], game="Age Of Empires II: Definitive Edition"):
    """Is this location's place in its scenario's budget order in logic yet?

    Unresolved it is only the question: which scenario, which location. Resolved, its children
    are the waiver switches (buildings the scenario starts with, purchases it can be spared),
    then the rules that switch a gathering source on. Every combination of switches has its cost worked out at resolve time,
    so evaluating is a lookup and a sum of the pile. More items only ever turn more switches on
    and the pile only grows, so the rule never goes from true to false.
    """

    scenario: Age2ScenarioData
    location: PricedLocation

    @override
    def _instantiate(self, world: 'Age2World') -> Rule.Resolved:
        order = budget_order(world.rules.logic.for_scenario(self.scenario), world)
        if order.need_for(self.location) is None:
            return False_().resolve(world)   # not in this scenario's order
        switches = order.switches()
        masks = range(1 << len(switches))

        def on(mask: int) -> list[Switch]:
            return [switch for bit, switch in enumerate(switches) if mask >> bit & 1]

        needs = tuple(order.need_for(self.location, frozenset(
            purchase for _, _, purchases in on(mask) for purchase in purchases)) for mask in masks)
        costs = tuple(
            tuple(required(needs[mask], frozenset(
                building for _, buildings, _ in on(mask) for building in buildings)).cost.items())
            for mask in masks)
        rules = (*(rule for rule, _, _ in switches), *(source[3] for source in order.sources))
        return self.Resolved(
            tuple(rule.resolve(world) for rule in rules),
            needs,
            tuple(buildings for _, buildings, _ in switches),
            tuple(source[:3] for source in order.sources),
            self.scenario,
            tuple((resource, contributors(resource)) for resource in SAMPLED_RESOURCES),
            costs,
            player=world.player,
            caching_enabled=False,
        )

    @override
    def __str__(self) -> str:
        return f"BudgetTotal({self.scenario.scenario_name}, {self.location.location_name})"

    class Resolved(NestedRule.Resolved):
        needs: tuple[Need, ...]
        """The running total for each combination of switches, by bit mask: a switch can make a
        purchase unnecessary, which takes it out of the total."""
        switches: tuple[tuple[Age2BuildingData, ...], ...]
        sources: tuple[tuple[str, Resource, int], ...]
        scenario: Age2ScenarioData
        contributors: tuple[tuple[Resource, tuple[tuple[str, int], ...]], ...]
        costs: tuple[tuple[tuple[Resource, int], ...], ...]
        """What the running total costs for each combination of switches, by bit mask. Pairs
        rather than dicts, because a resolved rule has to hash."""

        skip_cache = True
        """Sums over the pile, which is no child; item_dependencies names every pile item instead."""

        def mask(self, state: CollectionState) -> int:
            return sum(1 << bit for bit, rule in enumerate(self.children[:len(self.switches)])
                       if rule(state))

        def waived_now(self, state: CollectionState) -> frozenset[Age2BuildingData]:
            mask = self.mask(state)
            return frozenset(building for bit, buildings in enumerate(self.switches)
                             if mask >> bit & 1 for building in buildings)

        def sources_on(self, state: CollectionState) -> tuple[tuple[str, Resource, int], ...]:
            rules = self.children[len(self.switches):]
            return tuple(source for source, rule in zip(self.sources, rules) if rule(state))

        def allowance(self, state: CollectionState) -> dict[Resource, int]:
            total = {resource: 0 for resource in SAMPLED_RESOURCES}
            for _, resource, amount in self.sources_on(state):
                total[resource] += amount
            return total

        def pile(self, state: CollectionState) -> dict[Resource, int]:
            held = state.prog_items[self.player]
            return {resource: sum(held[name] * each for name, each in items)
                    for resource, items in self.contributors}

        def need(self, state: CollectionState | None) -> Need:
            return self.needs[0 if state is None else self.mask(state)]

        def requirement(self, state: CollectionState | None) -> Requirement:
            return required(self.need(state),
                            frozenset() if state is None else self.waived_now(state))

        @override
        def _evaluate(self, state: CollectionState) -> bool:
            need = dict(self.costs[self.mask(state)])
            held = state.prog_items[self.player]
            allowance: dict[Resource, int] | None = None
            for resource, items in self.contributors:
                wanted = need.get(resource, 0)
                if wanted <= 0:
                    continue
                total = 0
                for name, each in items:
                    total += held[name] * each
                    if total >= wanted:
                        break
                if total >= wanted:
                    continue
                if allowance is None:
                    allowance = self.allowance(state)
                if total + allowance[resource] < wanted:
                    return False
            return True

        @override
        def item_dependencies(self) -> dict[str, set[int]]:
            """Every pile item can move the sum. LocalStart narrows its candidates by this set."""
            deps = super().item_dependencies()
            for _, items in self.contributors:
                for name, _ in items:
                    deps.setdefault(name, set()).add(id(self))
            return deps

        def breakdown(self, state: CollectionState | None = None) -> dict[str, Any]:
            """Everything the short explanation sums up, for a longer view to show."""
            requirement = self.requirement(state)
            return {
                "scenario": self.scenario.scenario_name,
                "requirement": dict(requirement.cost),
                "own": self.need(state).own_cost(),
                "building_entries": sorted(self.need(state).entry_buildings, key=int),
                "buildings_charged": list(requirement.buildings),
                "ages_charged": list(requirement.ages),
                "waived": sorted(self.waived_now(state), key=int) if state is not None else [],
                "sources_on": list(self.sources_on(state)) if state is not None else [],
                "pile": self.pile(state) if state is not None else {},
            }

        def _totals(self, state: CollectionState | None) -> list[tuple[Resource, int, bool | None]]:
            need = dict(self.costs[0 if state is None else self.mask(state)])
            if state is None:
                return [(resource, need[resource], None)
                        for resource in SAMPLED_RESOURCES if need.get(resource, 0) > 0]
            pile, allowance = self.pile(state), self.allowance(state)
            return [(resource, need[resource], pile[resource] + allowance[resource] >= need[resource])
                    for resource in SAMPLED_RESOURCES if need.get(resource, 0) > 0]

        @override
        def explain_json(self, state: CollectionState | None = None) -> list[JSONMessagePart]:
            parts: list[JSONMessagePart] = [
                {"type": "text",
                 "text": f"{self.scenario.scenario_name}: starting pile + early gathering covers "}]
            for index, (resource, amount, met) in enumerate(self._totals(state)):
                if index:
                    parts.append({"type": "text", "text": ", "})
                text = f"{amount} {resource.name.lower()}"
                if met is None:
                    parts.append({"type": "text", "text": text})
                else:
                    parts.append({"type": "color", "color": "green" if met else "salmon",
                                  "text": text})
            return parts

        @override
        def explain_str(self, state: CollectionState | None = None) -> str:
            totals = ", ".join(f"{amount} {resource.name.lower()}"
                               for resource, amount, _ in self._totals(state))
            return f"{self.scenario.scenario_name}: starting pile + early gathering covers {totals}"

        @override
        def __str__(self) -> str:
            return self.explain_str()
