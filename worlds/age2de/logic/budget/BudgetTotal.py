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
from .BudgetSource import Part, options, seed_parts
from .Need import Need
from .Requirement import Requirement, required

if TYPE_CHECKING:
    from ... import Age2World

Bootstrap = tuple[frozenset[int], dict[Resource, int]]
"""The ways that paid, and what their seeds added to the total."""


@dataclasses.dataclass
class BudgetTotal(Rule["Age2World"], game="Age Of Empires II: Definitive Edition"):
    """Is this location's place in its scenario's budget order in logic yet?

    Unresolved it is only the question: which scenario, which location. Resolved, its children
    are the waiver switches (buildings the scenario starts with, purchases it can be spared),
    then the rules that switch a way of working a gathering source on. Every combination of
    switches has its cost, and each way's seed, worked out at resolve time.

    Evaluating, the pile alone may cover it. Otherwise sources are brought in one at a time, each
    once its seed - a dropsite, a crew, an age - is paid for out of what is in hand, which is the
    pile plus what the sources already working bring in. Every order is tried. More items only
    turn more switches and ways on and the pile only grows, so the rule never goes from true to
    false.
    """

    scenario: Age2ScenarioData
    location: PricedLocation

    @override
    def _instantiate(self, world: 'Age2World') -> Rule.Resolved:
        """Resolved once per seed and shared, like the scenario questions: the base's total sits
        in every has_base, and its seeds and source rules are not cheap to work out again."""
        logic = world.rules.logic
        key = ("BudgetTotal", self.scenario, self.location)
        resolved = logic.scenario_answers.get(key)
        if resolved is None:
            if key in logic.scenario_answers_open:
                raise RecursionError(f"{key} asks itself; the rule would never terminate")
            logic.scenario_answers_open.add(key)
            try:
                resolved = logic.scenario_answers[key] = self._resolve(world)
            finally:
                logic.scenario_answers_open.discard(key)
        return resolved

    def _resolve(self, world: 'Age2World') -> Rule.Resolved:
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
        way_rules: list[Rule] = []
        picks: list[tuple[int, int, Need, tuple[Age2BuildingData, ...]]] = []
        for index, source in enumerate(order.sources):
            for rule, seed in source.ways:
                way_rules.append(rule)
                picks += [(index, len(way_rules) - 1, seed, pick) for pick in options(seed)]
        parts = []
        for mask in masks:
            waived = frozenset(building for _, buildings, _ in on(mask) for building in buildings)
            requirement = required(needs[mask], waived)
            parts.append(tuple(seed_parts(seed, pick, needs[mask], requirement, waived,
                                          order.start)
                               for _, _, seed, pick in picks))
        rules = (*(rule for rule, _, _ in switches), *way_rules)
        return self.Resolved(
            tuple(rule.resolve(world) for rule in rules),
            needs,
            tuple(buildings for _, buildings, _ in switches),
            tuple((source.name, source.resource, source.allowance) for source in order.sources),
            tuple((source, rule) for source, rule, _, _ in picks),
            tuple(parts),
            self.scenario,
            self.location,
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
        ways: tuple[tuple[int, int], ...]
        """Each way to bring a source in, with one pick of dropsite: its source, and the child
        (after the switches) whose rule switches that way on."""
        parts: tuple[tuple[tuple[Part, ...], ...], ...]
        """What each way's seed buys, for each combination of switches, by bit mask."""
        scenario: Age2ScenarioData
        location: PricedLocation
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

        def usable(self, state: CollectionState) -> list[int]:
            """The ways switched on."""
            on = [rule(state) for rule in self.children[len(self.switches):]]
            return [index for index, (_, rule) in enumerate(self.ways) if on[rule]]

        def sources_on(self, state: CollectionState) -> tuple[tuple[str, Resource, int], ...]:
            on = {self.ways[index][0] for index in self.usable(state)}
            return tuple(source for index, source in enumerate(self.sources) if index in on)

        def allowance(self, state: CollectionState) -> dict[Resource, int]:
            return self._income({self.ways[index][0] for index in self.usable(state)})

        def _income(self, sources: set[int]) -> dict[Resource, int]:
            total = dict.fromkeys(SAMPLED_RESOURCES, 0)
            for index in sources:
                _, resource, amount = self.sources[index]
                total[resource] += amount
            return total

        def bootstrap(self, state: CollectionState) -> 'Bootstrap | None':
            """The ways that pay for it, and the seeds they add to the total, if any do."""
            mask = self.mask(state)
            return self._bootstrap(mask, self.pile(state), dict(self.costs[mask]),
                                   self.usable(state))

        def _bootstrap(self, mask: int, pile: dict[Resource, int], need: dict[Resource, int],
                       usable: list[int]) -> 'Bootstrap | None':
            parts = self.parts[mask]
            most = self._income({self.ways[way][0] for way in usable})
            stack: list[frozenset[int]] = [frozenset()]
            seen: set[frozenset[int]] = set()
            while stack:
                chosen = stack.pop()
                if chosen in seen:
                    continue
                seen.add(chosen)
                funded: dict[object, Part] = {}
                for way in chosen:
                    for part in parts[way]:
                        funded[part.identity] = part
                spent = dict.fromkeys(SAMPLED_RESOURCES, 0)
                extra = dict.fromkeys(SAMPLED_RESOURCES, 0)
                for part in funded.values():
                    for resource, amount in part.cost:
                        spent[resource] += amount
                        if not part.in_requirement:
                            extra[resource] += amount
                working = {self.ways[way][0] for way in chosen}
                income = self._income(working)
                if all(pile[resource] + income[resource] >= need.get(resource, 0) + extra[resource]
                       for resource in SAMPLED_RESOURCES):
                    return chosen, extra
                if any(pile[resource] + most[resource] < need.get(resource, 0) + extra[resource]
                       for resource in SAMPLED_RESOURCES):
                    continue   # not even every source switched on could cover what this set bought
                for way in usable:
                    if self.ways[way][0] in working:
                        continue
                    cost = dict.fromkeys(SAMPLED_RESOURCES, 0)
                    for part in parts[way]:
                        if part.identity not in funded:
                            for resource, amount in part.cost:
                                cost[resource] += amount
                    if all(pile[resource] + income[resource] - spent[resource] >= cost[resource]
                           for resource in SAMPLED_RESOURCES):
                        stack.append(chosen | {way})
            return None

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
            mask = self.mask(state)
            need = dict(self.costs[mask])
            pile = self.pile(state)
            if all(pile[resource] >= amount for resource, amount in need.items()):
                return True
            usable = self.usable(state)
            most = self._income({self.ways[way][0] for way in usable})
            if any(pile[resource] + most[resource] < amount for resource, amount in need.items()):
                return False   # seeds only ever add to the total
            return self._bootstrap(mask, pile, need, usable) is not None

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
                "sources_used": self._used(state),
                "pile": self.pile(state) if state is not None else {},
            }

        def _used(self, state: CollectionState | None) -> list[str]:
            found = None if state is None else self.bootstrap(state)
            if found is None:
                return []
            return sorted({self.sources[self.ways[way][0]][0] for way in found[0]})

        def _totals(self, state: CollectionState | None) -> list[tuple[Resource, int, bool | None]]:
            need = dict(self.costs[0 if state is None else self.mask(state)])
            if state is None:
                return [(resource, need[resource], None)
                        for resource in SAMPLED_RESOURCES if need.get(resource, 0) > 0]
            found = self.bootstrap(state)
            if found is not None:   # the total with the seeds of the sources that paid for it
                return [(resource, need.get(resource, 0) + found[1][resource], True)
                        for resource in SAMPLED_RESOURCES
                        if need.get(resource, 0) + found[1][resource] > 0]
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
