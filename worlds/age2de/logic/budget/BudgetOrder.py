"""A scenario's budget order: the sample by age and the scenario's rank, each entry after its
precursors, less what could never fit the most the scenario could ever have."""
from __future__ import annotations

import dataclasses
import functools
from typing import TYPE_CHECKING, Iterable

from rule_builder.rules import False_, Or, Rule

from ...generation.pools.BudgetPool import (SAMPLED_RESOURCES, SOURCE_ALLOWANCE, SOURCES,
                                            VILLAGER, PricedLocation)
from ...items.Items import Resource
from ...locations.Ages import Age2AgeData
from ...locations.Buildings import BUILDING_PREREQUISITE, Age2BuildingData
from ...locations.Techs import Age2TechData
from ...locations.Units import Age2UnitData
from ..scenarios.ScenarioAgeLogic import AGE_BUILDINGS, PREVIOUS
from .AgeBudgetItem import AgeBudgetItem
from .BudgetItem import BudgetItem
from .BuildingBudgetItem import BuildingBudgetItem
from .Need import CLIMBED_AGES, Need
from .Requirement import required
from .TechBudgetItem import TechBudgetItem
from .UnitBudgetItem import UnitBudgetItem
from .VillagerBudgetItem import VillagerBudgetItem

if TYPE_CHECKING:
    from ... import Age2World
    from ..ScenarioLogic import ScenarioLogic


_ITEMS: dict[type, type[BudgetItem]] = {Age2AgeData: AgeBudgetItem,
                                        Age2BuildingData: BuildingBudgetItem,
                                        Age2TechData: TechBudgetItem,
                                        Age2UnitData: UnitBudgetItem}


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

    def priced(self, location: PricedLocation) -> _Priced | None:
        """The location as this scenario pays for it, or None if its own rule, less paying,
        could never be true here."""
        item = budget_item(location)
        if self.impossible(item.structural(self.scenario)):
            return None
        return _Priced(item, item.need_in(self.scenario))

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
        techs = [tech.location for tech in reversed(tuple(entry.item.below()))
                 if tech.location in paid]
        found = ([self.priced(building) for building in buildings
                  if building in pool.buildings.locations]
                 + [self.priced(age) for age in requirement.ages if age in pool.ages.locations]
                 + [self.priced(tech) for tech in techs if tech in pool.techs.shuffled])
        return sorted((precursor for precursor in found
                       if precursor is not None and precursor.location is not entry.location),
                      key=lambda precursor: (precursor.age, precursor.item.rank))

    def _build_order(self) -> tuple[tuple[_Priced, ...], tuple[_Priced, ...]]:
        """The sample by age, then the scenario's random rank, each entry after its precursors,
        less what could never fit the most the scenario could ever have."""
        budget = self.world.pool.budget
        rank = budget.rank.get(self.scenario.scenario, {})
        base = sorted(filter(None, map(self.priced, budget.entries)),
                      key=lambda entry: (entry.age, rank[entry.location]))
        ordered = list({precursor.location: precursor for entry in base
                        for precursor in (*self.precursors(entry), entry)}.values())
        most, every_waiver = self.max_budget(), frozenset(self.waivers)
        kept, pruned = [], []
        for entry in ordered:
            need = required(self.plan(kept + [entry]), every_waiver).cost
            fits = all(amount <= most[resource] for resource, amount in need.items())
            (kept if fits else pruned).append(entry)
        return tuple(kept), tuple(pruned)

    def need_for(self, location: PricedLocation) -> Need | None:
        """The running total up to and including this location, if the order holds it."""
        index = next((n for n, entry in enumerate(self.order) if entry.location is location),
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
