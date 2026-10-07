"""BudgetTotal: whether a scenario's opening pile, plus what its early gathering brings in, covers
its running total up to and including one location in the seed's budget order.

That is the one rule. Everything behind it is worked out while it resolves: a location's place in
its scenario's order depends on what the scenario could ever do, which is asked of the scenario's
own rules, and a rule only answers that once resolved. The order is built once per scenario, by
the first of its locations to resolve, and kept with the scenario questions' answers on Logic."""
from __future__ import annotations

import dataclasses
import itertools
from typing import TYPE_CHECKING, Any, Callable, Iterable, override

from BaseClasses import CollectionState
from NetUtils import JSONMessagePart

from rule_builder.rules import False_, NestedRule, Or, Rule

from ...generation.pools.BudgetPool import (SAMPLED_RESOURCES, SOURCE_ALLOWANCE, SOURCES,
                                            BudgetKind, BudgetLocation)
from ...items.Items import Age2ItemData, Resource
from ...locations.Ages import Age2AgeData
from ...locations.Buildings import BUILDING_PREREQUISITE, Age2BuildingData
from ...locations.Scenarios import Age2ScenarioData
from ...locations.Techs import Age2TechData
from ...locations.Units import Age2UnitData
from ..scenarios.ScenarioAgeLogic import AGE_BUILDINGS, PREVIOUS
from .ResourceAmount import contributors

if TYPE_CHECKING:
    from ... import Age2World
    from ..ScenarioLogic import ScenarioLogic


CLIMBED_AGES = (Age2AgeData.FEUDAL, Age2AgeData.CASTLE, Age2AgeData.IMPERIAL)

Climb = tuple[Age2AgeData, tuple[Age2BuildingData, ...], Age2BuildingData | None]
"""Per age: the buildings two of which leave the age before it, and the one counting for both."""


# -- what a location costs ---------------------------------------------------------------------

@dataclasses.dataclass(frozen=True)
class Need:
    """What one location makes a scenario pay for. Adding two is a union, so whatever both need
    is charged once."""
    own: frozenset[tuple[object, tuple[tuple[Resource, int], ...]]] = frozenset()
    """Paid for itself, once per identity: a tech, a unit line, the villager."""
    entry_buildings: frozenset[Age2BuildingData] = frozenset()
    """Buildings that are themselves locations: always charged, never waived."""
    groups: frozenset[tuple[Age2BuildingData, ...]] = frozenset()
    """Buildings it needs, each as the options any one of which will do."""
    top: Age2AgeData = Age2AgeData.DARK
    """The highest age it needs."""
    start: Age2AgeData = Age2AgeData.DARK
    """The age the scenario pays its way up from; set by in_scenario."""
    climbs: tuple[Climb, ...] = ()
    """What leaves each age in this scenario; set by in_scenario."""

    def __add__(self, other: 'Need') -> 'Need':
        return Need(self.own | other.own, self.entry_buildings | other.entry_buildings,
                    self.groups | other.groups, max(self.top, other.top))

    @staticmethod
    def pay(identity: object, cost: dict[Resource, int]) -> 'Need':
        priced = tuple(sorted(((resource, amount) for resource, amount in cost.items() if amount > 0),
                              key=lambda item: item[0].value))
        return Need(own=frozenset({(identity, priced)}))

    @staticmethod
    def build(building: Age2BuildingData) -> 'Need':
        return Need(entry_buildings=frozenset({building}))

    @staticmethod
    def one_of(options: tuple[Age2BuildingData, ...]) -> 'Need':
        return Need(groups=frozenset({options})) if options else Need()

    @staticmethod
    def reach(age: Age2AgeData) -> 'Need':
        return Need(top=age)

    def in_scenario(self, start: Age2AgeData, climbs: tuple[Climb, ...],
                    could_have: Callable[[Age2BuildingData], bool]) -> 'Need':
        """Settled for one scenario: where it starts, how it climbs, and only the building
        options it could ever have."""
        groups = frozenset(kept for group in self.groups if (kept := tuple(filter(could_have, group))))
        climbs = tuple((age, tuple(filter(could_have, options)),
                        alone if alone is not None and could_have(alone) else None)
                       for age, options, alone in climbs)
        return dataclasses.replace(self, groups=groups, top=max(start, self.top), start=start,
                                   climbs=climbs)

    def own_cost(self) -> dict[Resource, int]:
        cost: dict[Resource, int] = {}
        for _, priced in self.own:
            for resource, amount in priced:
                cost[resource] = cost.get(resource, 0) + amount
        return cost


@dataclasses.dataclass(frozen=True)
class Requirement:
    cost: dict[Resource, int]
    buildings: tuple[Age2BuildingData, ...]
    ages: tuple[Age2AgeData, ...]


def required(need: Need, waived: frozenset[Age2BuildingData]) -> Requirement:
    """What a settled Need costs once the buildings in `waived` are standing for free."""
    cost = dict.fromkeys(SAMPLED_RESOURCES, 0)
    for resource, amount in tuple(need.own_cost().items()) + tuple(
            item for building in need.entry_buildings for item in building.cost.items()):
        cost[resource] += amount
    have, charged = set(need.entry_buildings), []

    def chain(building: Age2BuildingData | None) -> list[Age2BuildingData]:
        """The building and its prerequisites, up to the first one already paid or standing."""
        out: list[Age2BuildingData] = []
        while building is not None and building not in waived | have and building not in out:
            out.append(building)
            building = BUILDING_PREREQUISITE.get(building)
        return out

    def take(buildings: Iterable[Age2BuildingData]) -> None:
        charged.extend(building for building in buildings if building not in have)
        have.update(buildings)

    def worth(buildings: Iterable[Age2BuildingData]) -> int:
        return sum(sum(building.cost.values()) for building in buildings)

    for options in sorted(need.groups, key=lambda group: (len(group), tuple(map(int, group)))):
        take(chain(min(options, key=lambda option: (worth(chain(option)), int(option)))))
    ages = tuple(age for age in CLIMBED_AGES if need.start < age <= need.top)
    if ages:
        take(chain(Age2BuildingData.TOWN_CENTER))   # every age is researched at a Town Center
    climbs = {age: (options, alone) for age, options, alone in need.climbs}
    for age in ages:
        for resource, amount in age.cost.items():
            cost[resource] += amount
        options, alone = climbs[age]
        candidates = []
        for first, second in itertools.combinations(options, 2):
            both = chain(first)
            both += [building for building in chain(second) if building not in both]
            candidates.append((worth(both), (int(first), int(second)), both))
        if alone is not None:
            candidates.append((worth(chain(alone)), (int(alone),), chain(alone)))
        if candidates:
            take(min(candidates, key=lambda candidate: candidate[:2])[2])
    for resource, amount in (item for building in charged for item in building.cost.items()):
        cost[resource] += amount
    return Requirement({resource: amount for resource, amount in cost.items() if amount > 0},
                       tuple(charged), ages)


# -- a scenario's order, built while its first budget rule resolves ---------------------------

@dataclasses.dataclass(frozen=True)
class _Priced:
    """One location as one scenario would pay for it."""
    kind: BudgetKind
    location: BudgetLocation
    age: Age2AgeData
    need: Need

    @property
    def key(self) -> tuple[BudgetKind, BudgetLocation]:
        return self.kind, self.location


def budget_order(scenario: 'ScenarioLogic', world: 'Age2World') -> '_ScenarioOrder':
    """The scenario's budget order, built once and kept with the scenario questions' answers.
    Rules have to be resolvable, so this is for resolving BudgetTotal and for what reads the
    result once rules exist (the spoiler)."""
    logic = scenario.logic
    key = ("BudgetOrder", scenario.scenario)
    order = logic.scenario_answers.get(key)
    if order is None:
        if key in logic.scenario_answers_open:
            raise RecursionError(f"{key} asks itself; the order would never be built")
        logic.scenario_answers_open.add(key)
        try:
            order = logic.scenario_answers[key] = _ScenarioOrder(scenario, world)
        finally:
            logic.scenario_answers_open.discard(key)
    return order


class _ScenarioOrder:
    def __init__(self, scenario: 'ScenarioLogic', world: 'Age2World') -> None:
        self.scenario = scenario
        self.world = world
        ages = world.pool.ages
        # The age the scenario pays its way up from: Dark when starts are pulled back.
        self.start = Age2AgeData.DARK if ages.dark_start else ages.starts_in(scenario.scenario)
        # What leaves each age, as two_from reads it: two of these, or a Castle alone.
        self.climbs = tuple((age, AGE_BUILDINGS[PREVIOUS[age]],
                             Age2BuildingData.CASTLE if PREVIOUS[age] is Age2AgeData.CASTLE else None)
                            for age in CLIMBED_AGES)
        self.waivers = self._waivers()
        self._could_have: dict[Age2BuildingData, bool] = {}
        self.sources = self._sources()
        self.order, self.pruned = self._build_order()

    def _waivers(self) -> dict[Age2BuildingData, Rule]:
        """The buildings the scenario can find standing, and the rule that says so. A base is a
        standing Town Center."""
        state = self.scenario.starting_state
        rules = {building: state.starts_with_building[building] for building in Age2BuildingData
                 if self.scenario.civilization.can_build(building)}
        if Age2BuildingData.TOWN_CENTER in rules and not isinstance(state.has_base, False_):
            standing = rules[Age2BuildingData.TOWN_CENTER]
            rules[Age2BuildingData.TOWN_CENTER] = (
                state.has_base if isinstance(standing, False_) else standing | state.has_base)
        return {building: rule for building, rule in rules.items() if not isinstance(rule, False_)}

    def impossible(self, rule: Rule) -> bool:
        return rule.resolve(self.world).always_false

    def could_have(self, building: Age2BuildingData) -> bool:
        if building not in self._could_have:
            self._could_have[building] = not self.impossible(self.scenario.has_building(building))
        return self._could_have[building]

    def _sources(self) -> list[tuple[str, Resource, int, Rule]]:
        """The early gathering sources this scenario could ever count toward its budget."""
        economy = self.scenario.economy
        sources = []
        for name, resource, methods in SOURCES:
            rules = [getattr(economy, method)() for method in methods]
            sources.append((name, resource, SOURCE_ALLOWANCE,
                            rules[0] if len(rules) == 1 else Or(*rules)))
        if relics := self.world.pool.budget.relic_allowance(self.scenario.scenario):
            sources.append(("relics", Resource.GOLD, relics, economy.can_collect_relics()))
        return [source for source in sources if not self.impossible(source[3])]

    def max_budget(self) -> dict[Resource, int]:
        """Every starting resource in the pool, and every source the scenario could ever count."""
        budget = {resource: self.world.pool.resources.totals[resource]
                  for resource in SAMPLED_RESOURCES}
        for _, resource, amount, _ in self.sources:
            budget[resource] += amount
        return budget

    def priced(self, kind: BudgetKind, location: BudgetLocation) -> _Priced | None:
        """The location as this scenario pays for it, or None if its own rule, less paying,
        could never be true here."""
        scenario = self.scenario
        if kind is BudgetKind.AGE:
            rule, need = scenario.ages.can_research(location), Need.reach(location)
        elif kind is BudgetKind.BUILDING:
            rule, need = scenario.buildings.can_build_building(location), self._build(location)
        elif kind is BudgetKind.TECH:
            rule, need = (scenario.techs.can_research_structurally(location),
                          self._research(location))
        else:
            rule = scenario.units.can_train_structurally(location)
            need = self._villager() if kind is BudgetKind.VILLAGER else self._train(location)
        if self.impossible(rule):
            return None
        return _Priced(kind, location, location if kind is BudgetKind.AGE else location.age, need)

    @staticmethod
    def _build(building: Age2BuildingData) -> Need:
        """Putting one up: itself, always, and its prerequisite."""
        prerequisite = BUILDING_PREREQUISITE.get(building)
        return (Need.build(building) + Need.reach(building.age)
                + (Need.one_of((prerequisite,)) if prerequisite is not None else Need()))

    def _research(self, tech: Age2TechData | None, entry: bool = True) -> Need:
        """It and its prerequisites, each at a building and an age, less those the scenario
        researched for itself. `entry` is the tech asked for, which is never let off."""
        need = Need()
        while tech is not None:
            if self.scenario.civilization.researches(tech) and (
                    entry or not self.scenario.techs.researched_at_start(tech)):
                need += (Need.pay(tech, tech.cost) + Need.reach(tech.age)
                         + Need.one_of(tuple(tech.buildings)))
            entry, tech = False, tech.prerequisite
        return need

    def _train(self, unit: Age2UnitData) -> Need:
        """One unit of its line (every tier costs the same), where it is trained, its age, and
        the upgrade techs that make this tier."""
        return (Need.pay(unit.line, unit.cost) + Need.reach(unit.age)
                + Need.one_of(tuple(unit.buildings))
                + self._research(unit.upgrade_tech, entry=False))

    @staticmethod
    def _villager() -> Need:
        """One villager, whichever villager location: priced at the food that staffs a base."""
        villager, food = Age2UnitData.VILLAGER_MALE, Age2ItemData.STARTING_VILLAGER_FOOD.type
        return (Need.pay("villager", {food.type: food.amount}) + Need.reach(villager.age)
                + Need.one_of(tuple(villager.buildings)))

    def plan(self, entries: Iterable[_Priced]) -> Need:
        return sum((entry.need for entry in entries), Need()).in_scenario(
            self.start, self.climbs, self.could_have)

    def precursors(self, entry: _Priced) -> list[_Priced]:
        """What this location cannot be had without, that is a location this scenario could do:
        the buildings and ages it charges, and the techs it pays for. They keep the order they
        arrive in, with every prerequisite ahead of what needs it: a building's prerequisites go
        just before it, a tech chain runs oldest first, and grouping by age then kind puts an age
        ahead of its buildings and techs and the climb buildings ahead of the age-up."""
        pool = self.world.pool
        requirement = required(self.plan([entry]), frozenset())
        charged, buildings = set(requirement.buildings), []
        for building in requirement.buildings:
            chain = []
            while building in charged and building not in buildings and building not in chain:
                chain.append(building)
                building = BUILDING_PREREQUISITE.get(building)
            buildings += reversed(chain)
        paid = {identity for identity, _ in entry.need.own}
        tech, chain = (entry.location if entry.kind is BudgetKind.TECH else
                       entry.location.upgrade_tech if entry.kind is BudgetKind.UNIT else None), []
        while tech is not None:
            chain.append(tech)
            tech = tech.prerequisite
        techs = [tech for tech in reversed(chain) if tech in paid and tech is not entry.location]
        found = ([self.priced(BudgetKind.BUILDING, building) for building in buildings
                  if building in pool.buildings.locations]
                 + [self.priced(BudgetKind.AGE, age) for age in requirement.ages
                    if age in pool.ages.locations]
                 + [self.priced(BudgetKind.TECH, tech) for tech in techs
                    if tech in pool.techs.shuffled])
        return sorted((precursor for precursor in found
                       if precursor is not None and precursor.key != entry.key),
                      key=lambda precursor: (precursor.age, precursor.kind))

    def _build_order(self) -> tuple[tuple[_Priced, ...], tuple[_Priced, ...]]:
        """The sample by age, then the scenario's random rank, each entry after its precursors,
        less what could never fit the most the scenario could ever have."""
        budget = self.world.pool.budget
        rank = budget.rank.get(self.scenario.scenario, {})
        base = sorted(filter(None, (self.priced(*key) for key in budget.entries)),
                      key=lambda entry: (entry.age, rank[entry.key]))
        ordered = list({precursor.key: precursor for entry in base
                        for precursor in (*self.precursors(entry), entry)}.values())
        most, every_waiver = self.max_budget(), frozenset(self.waivers)
        kept, pruned = [], []
        for entry in ordered:
            need = required(self.plan(kept + [entry]), every_waiver).cost
            fits = all(amount <= most[resource] for resource, amount in need.items())
            (kept if fits else pruned).append(entry)
        return tuple(kept), tuple(pruned)

    def need_for(self, kind: BudgetKind, location: BudgetLocation) -> Need | None:
        """The running total up to and including this location, if the order holds it."""
        index = next((n for n, entry in enumerate(self.order) if entry.key == (kind, location)),
                     None)
        return None if index is None else self.plan(self.order[:index + 1])

    def switches(self) -> list[tuple[Rule, tuple[Age2BuildingData, ...]]]:
        """The waivers as switches: buildings that stand on the same rule (all of a camp's) are
        one switch, so a cost table needs one entry per combination of switches, not buildings."""
        switches: list[tuple[Rule, list[Age2BuildingData]]] = []
        for building, rule in self.waivers.items():
            same = next((switch for switch in switches if switch[0] == rule), None)
            if same is None:
                switches.append((rule, [building]))
            else:
                same[1].append(building)
        return [(rule, tuple(buildings)) for rule, buildings in switches]


# -- the rule ----------------------------------------------------------------------------------

@dataclasses.dataclass
class BudgetTotal(Rule["Age2World"], game="Age Of Empires II: Definitive Edition"):
    """Is this location's place in its scenario's budget order in logic yet?

    Unresolved it is only the question: which scenario, which location. Resolved, its children
    are the waiver switches (buildings the scenario starts with), then the rules that switch a
    gathering source on. Every combination of switches has its cost worked out at resolve time,
    so evaluating is a lookup and a sum of the pile. More items only ever turn more switches on
    and the pile only grows, so the rule never goes from true to false.
    """

    scenario: Age2ScenarioData
    kind: BudgetKind
    location: BudgetLocation

    @override
    def _instantiate(self, world: 'Age2World') -> Rule.Resolved:
        order = budget_order(world.rules.logic.for_scenario(self.scenario), world)
        need = order.need_for(self.kind, self.location)
        if need is None:
            return False_().resolve(world)   # not in this scenario's order
        switches = order.switches()
        costs = tuple(
            tuple(required(need, frozenset(building for bit, (_, buildings) in enumerate(switches)
                                           if mask >> bit & 1 for building in buildings)).cost.items())
            for mask in range(1 << len(switches)))
        rules = (*(rule for rule, _ in switches), *(source[3] for source in order.sources))
        return self.Resolved(
            tuple(rule.resolve(world) for rule in rules),
            need,
            tuple(buildings for _, buildings in switches),
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
        need: Need
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

        def requirement(self, state: CollectionState | None) -> Requirement:
            return required(self.need, frozenset() if state is None else self.waived_now(state))

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
                "own": self.need.own_cost(),
                "building_entries": sorted(self.need.entry_buildings, key=int),
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
