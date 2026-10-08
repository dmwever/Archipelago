"""A scenario's budget order: the sample by age and the scenario's rank, each entry after its
precursors, less what could never fit the most the scenario could ever have."""
from __future__ import annotations

import dataclasses
import functools
from typing import TYPE_CHECKING, Iterable, NamedTuple

from rule_builder.rules import False_, Rule

from ...generation.pools.BudgetPool import SAMPLED_RESOURCES, VILLAGER
from ...items.Items import Resource
from ...locations.Ages import Age2AgeData
from ...locations.Buildings import BUILDING_PREREQUISITE, Age2BuildingData
from ...locations.Techs import Age2TechData
from ...locations.Units import Age2UnitData
from ..scenarios.ScenarioAgeLogic import PREVIOUS
from .AgeBudgetItem import AgeBudgetItem
from .BaseBudgetItem import BaseBudgetItem
from .BudgetItem import BASE, Age2BaseData, BudgetItem, PricedLocation
from .BudgetSource import (SOURCE_ALLOWANCE, SOURCES, Part, Way, options, pays,
                           relic_allowance, seed_parts)
from .BuildingBudgetItem import BuildingBudgetItem
from .Need import CLIMBED_AGES, Need
from .Requirement import Requirement
from .ScenarioBudgetItem import ScenarioBudgetItem
from .TechBudgetItem import TechBudgetItem
from .UnitBudgetItem import UnitBudgetItem
from .VillagerBudgetItem import VillagerBudgetItem

if TYPE_CHECKING:
    from ... import Age2World
    from ..ScenarioLogic import ScenarioLogic


_ITEMS: dict[type, type[BudgetItem]] = {Age2AgeData: AgeBudgetItem,
                                        Age2BuildingData: BuildingBudgetItem,
                                        Age2TechData: TechBudgetItem,
                                        Age2UnitData: UnitBudgetItem,
                                        Age2BaseData: BaseBudgetItem}


Switch = tuple[Rule, list[Age2BuildingData], list[PricedLocation]]


class ScenarioSource(NamedTuple):
    """A gathering source as one scenario could work it: each way - its rule, already resolved -
    and the seed it buys."""
    name: str
    resource: Resource
    allowance: int
    ways: list[tuple[Rule.Resolved, Need]]
"""One waiver rule, the buildings it stands up and the purchases it makes unnecessary."""


@functools.cache
def budget_item(location: PricedLocation) -> BudgetItem:
    """The one item per location, so each tree is built once whatever the scenario."""
    if location is VILLAGER:
        return VillagerBudgetItem(location)
    return _ITEMS[type(location)](location)


@dataclasses.dataclass(frozen=True)
class _Priced:
    """One location as one scenario would pay for it: its item, trimmed for the scenario."""
    item: BudgetItem
    need: Need

    @property
    def location(self) -> PricedLocation:
        return self.item.location

    @property
    def age(self) -> Age2AgeData:
        return self.item.age


def budget_order(scenario: 'ScenarioLogic', world: 'Age2World') -> '_ScenarioOrder':
    """The scenario's budget order, built once and kept with the budget's other answers.
    Rules have to be resolvable, so this is for resolving BudgetTotal and for what reads the
    result once rules exist (the spoiler)."""
    logic = scenario.logic
    key = ("BudgetOrder", scenario.scenario)
    order = logic.budget_answers.get(key)
    if order is None:
        if key in logic.scenario_answers_open:
            raise RecursionError(f"{key} asks itself; the order would never be built")
        logic.scenario_answers_open.add(key)
        try:
            order = logic.budget_answers[key] = _ScenarioOrder(scenario, world)
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
        # What leaves the age before each one, read off the rule that asks it. A tuple, as it
        # ends up in a Need, which hashes.
        self.climbs = tuple((age, climb.buildings, climb.single_building)
                            for age in CLIMBED_AGES
                            for climb in [scenario.ages.two_from(PREVIOUS[age])])
        self.waivers = self._waivers()
        self._could_have: dict[Age2BuildingData, bool] = {}
        self.sources = self._sources()
        self.worth = tuple((source.name, source.resource, source.allowance)
                           for source in self.sources)
        self.way_rules: list[Rule.Resolved] = []
        self.picks: list[tuple[int, int, Need, list[Age2BuildingData]]] = []
        """Each way to bring a source in, once per pick of dropsite: its source, its rule (an
        index into way_rules), its seed, and the pick."""
        for index, source in enumerate(self.sources):
            for rule, seed in source.ways:
                self.way_rules.append(rule)
                self.picks += [(index, len(self.way_rules) - 1, seed, pick)
                               for pick in options(seed)]
        self.ways: tuple[Way, ...] = tuple((source, rule) for source, rule, _, _ in self.picks)
        self.purchases = {location: rule for location, rule
                          in scenario.starting_state.required_purchases.items()
                          if not isinstance(rule, False_)}
        """The scenario's purchases that something can make unnecessary, and the rule that does."""
        self.switches: list[Switch] = self._switches()
        self.switch_rules: list[Rule.Resolved] = [rule.resolve(world)
                                                  for rule, _, _ in self.switches]
        """Each switch's rule, resolved once for every budget total in the scenario."""
        self._precursors: dict[PricedLocation, list[_Priced]] = {}
        self._needed: dict[frozenset[PricedLocation], frozenset[PricedLocation]] = {}
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

    def choice_order(self, building: Age2BuildingData) -> int:
        """Where a building stands among choices: the seed's building order."""
        return self.world.pool.budget.building_order[building]

    def impossible(self, rule: Rule) -> bool:
        return rule.resolve(self.world).always_false

    def could_have(self, building: Age2BuildingData) -> bool:
        if building not in self._could_have:
            self._could_have[building] = not self.impossible(self.scenario.has_building(building))
        return self._could_have[building]

    def _sources(self) -> list[ScenarioSource]:
        """The early gathering sources this scenario could ever count toward its budget, each
        with the ways it could be worked here and the seed each way is paid for with."""
        economy = self.scenario.economy
        relics = relic_allowance(self.scenario.scenario)
        sources = []
        for source in SOURCES:
            ways: list[tuple[Rule.Resolved, Need]] = []
            for way, seed in source.ways:
                rule = way(economy).resolve(self.world)   # once: every budget total reuses it
                if not rule.always_false:
                    ways.append((rule, seed.in_scenario(self.start, self.climbs, self.could_have,
                                                        self.choice_order)))
            allowance = relics if source.per_relic else SOURCE_ALLOWANCE
            if ways and allowance:
                sources.append(ScenarioSource(source.name, source.resource, allowance, ways))
        return sources

    def max_budget(self) -> dict[Resource, int]:
        """Every starting resource in the pool, and every source the scenario could ever count."""
        budget = {resource: self.world.pool.resources.totals[resource]
                  for resource in SAMPLED_RESOURCES}
        for _, resource, amount, _ in self.sources:
            budget[resource] += amount
        return budget

    def seed_parts(self, need: Need, requirement: Requirement,
                   waived: frozenset[Age2BuildingData]) -> tuple[tuple[Part, ...], ...]:
        # Tuples: a resolved rule keeps these, and it has to hash.
        """What each way's seed buys, against this running total."""
        return tuple(seed_parts(seed, pick, need, requirement, waived, self.start)
                     for _, _, seed, pick in self.picks)

    def priced(self, location: PricedLocation) -> _Priced | None:
        """The location as this scenario pays for it, or None if its own rule, less paying,
        could never be true here."""
        return self._priced(budget_item(location))

    def _priced(self, item: BudgetItem) -> _Priced | None:
        if self.impossible(item.scenario_rule(self.scenario)):
            return None
        return _Priced(item, item.need_in(self.scenario))

    def plan(self, entries: Iterable[_Priced]) -> Need:
        return sum((entry.need for entry in entries), Need()).in_scenario(
            self.start, self.climbs, self.could_have, self.choice_order)

    def precursors(self, entry: _Priced) -> list[_Priced]:
        """What this location cannot be had without, that is a location this scenario could do:
        the buildings and ages it charges, and the techs it pays for. They keep the order they
        arrive in, with every prerequisite ahead of what needs it: a building's prerequisites go
        just before it, a tech chain runs oldest first, and grouping by age then kind puts an age
        ahead of its buildings and techs and the climb buildings ahead of the age-up."""
        pool = self.world.pool
        requirement = Requirement(self.plan([entry]), frozenset())
        charged, buildings = set(requirement.buildings), []
        for building in requirement.buildings:
            chain = []
            while building in charged and building not in buildings and building not in chain:
                chain.append(building)
                building = BUILDING_PREREQUISITE.get(building)
            buildings += reversed(chain)
        paid = {identity for identity, _ in entry.need.own}
        techs = [tech.location for tech in reversed(list(entry.item.prerequisite_techs()))
                 if tech.location in paid]
        found = ([self.priced(building) for building in buildings
                  if building in pool.buildings.locations]
                 + [self.priced(age) for age in requirement.ages if age in pool.ages.locations]
                 + [self.priced(tech) for tech in techs if tech in pool.techs.shuffled])
        return sorted((precursor for precursor in found
                       if precursor is not None and precursor.location is not entry.location),
                      key=lambda precursor: (precursor.age, precursor.item.rank))

    def _build_order(self) -> tuple[list[_Priced], list[_Priced]]:
        """The sample, the scenario's own purchases and its base by age: its purchases first, then
        the base, then the scenario's random rank; each entry after its precursors, less what
        could never fit the most the scenario could ever have: every starting resource in the
        pool, every building it could find standing, every source it could bring in - seeds
        paid for."""
        budget = self.world.pool.budget
        rank = budget.rank
        purchases = self.scenario.starting_state.required_purchases
        items = ([ScenarioBudgetItem(budget_item(location)) for location in purchases]
                 + [budget_item(BASE)]
                 + [budget_item(location) for location in budget.entries
                    if location not in purchases])
        self._base = sorted(filter(None, map(self._priced, items)),
                            key=lambda entry: (entry.age, 0, 0) if entry.item.first_in_age
                            else (entry.age, 1, rank[entry.location]))
        self._precursors = {entry.location: self.precursors(entry) for entry in self._base}
        ordered = list({precursor.location: precursor for entry in self._base
                        for precursor in (*self._precursors[entry.location], entry)}.values())
        pile = {resource: self.world.pool.resources.totals[resource]
                for resource in SAMPLED_RESOURCES}
        every_waiver, every_way = frozenset(self.waivers), list(range(len(self.ways)))
        kept, pruned = [], []
        for entry in ordered:
            need = self.plan(kept + [entry])
            requirement = Requirement(need, every_waiver)
            fits = pays(pile, dict(requirement.cost), every_way, self.ways,
                        self.seed_parts(need, requirement, every_waiver), self.worth)
            (kept if fits else pruned).append(entry)
        return kept, pruned

    def needed(self, dropped: frozenset[PricedLocation]) -> frozenset[PricedLocation]:
        """What the order still needs once these purchases are unnecessary: everything but them
        and what only they brought in."""
        if dropped not in self._needed:
            self._needed[dropped] = frozenset(
                precursor.location for entry in self._base if entry.location not in dropped
                for precursor in (*self._precursors[entry.location], entry))
        return self._needed[dropped]

    def need_for(self, location: PricedLocation,
                 dropped: frozenset[PricedLocation] = frozenset()) -> Need | None:
        """The running total up to and including this location, if the order holds it, with
        these purchases unnecessary. The order itself never moves, and the location always pays
        for itself, so sparing a purchase only ever takes cost away."""
        index = next((n for n, entry in enumerate(self.order) if entry.location is location),
                     None)
        if index is None:
            return None
        needed = self.needed(dropped)
        return self.plan(entry for entry in self.order[:index + 1]
                         if entry.location in needed or entry.location is location)

    def _switches(self) -> list[Switch]:
        """The waivers as switches: buildings that stand on the same rule (all of a camp's) and
        purchases that rule makes unnecessary are one switch, so a cost table needs one entry per
        combination of switches, not per building."""
        switches: list[Switch] = []

        def switch(rule: Rule) -> Switch:
            same = next((switch for switch in switches if switch[0] == rule), None)
            if same is None:
                same = (rule, [], [])
                switches.append(same)
            return same

        for building, rule in self.waivers.items():
            switch(rule)[1].append(building)
        for location, rule in self.purchases.items():
            switch(rule)[2].append(location)
        return switches
