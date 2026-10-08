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
from .BudgetSource import (SOURCE_ALLOWANCE, RESOURCE_ORIGINS, Part, ScenarioOrigin, ResolvedGatherMethod, GatherMethodChoice, dropsite_chioces, pays,
                           relic_allowance, seed_parts)
from .BuildingBudgetItem import BuildingBudgetItem
from .Need import CLIMBED_AGES, AgeUpBuildings, Need
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


class CostWaiver(NamedTuple):
    rule: Rule.Resolved
    buildings: list[Age2BuildingData]
    purchases: list[PricedLocation]


class DropsiteChoice(NamedTuple):
    """One gather method with one pick of dropsite: its origin and the method's rule by index
    (into gather_method_rules), its seed, and the buildings picked."""
    source: int
    rule: int
    seed: Need
    site: list[Age2BuildingData]


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


def budget_order(scenario: 'ScenarioLogic', world: 'Age2World') -> 'BudgetOrder':
    """The scenario's budget order, built once and kept on Logic.
    Rules have to be resolvable, so this is for resolving BudgetTotal and for what reads the
    result once rules exist (the spoiler)."""
    logic = scenario.logic
    key = scenario.scenario
    if key not in logic.budget_orders:
        if key in logic.budget_orders_open:
            raise RecursionError(f"{key.scenario_name}'s budget order asks for itself; "
                                 f"it would never be built")
        logic.budget_orders_open.add(key)
        try:
            logic.budget_orders[key] = BudgetOrder(scenario, world)
        finally:
            logic.budget_orders_open.discard(key)
    return logic.budget_orders[key]


class BudgetOrder:
    def __init__(self, scenario: 'ScenarioLogic', world: 'Age2World') -> None:
        self.scenario = scenario
        self.world = world
        ages = world.pool.ages
        self.start_age = Age2AgeData.DARK if ages.dark_start else ages.starts_in(scenario.scenario)
        self.age_up_buildings: tuple[AgeUpBuildings, ...] = tuple(
            AgeUpBuildings(age, rule.buildings, rule.single_building)
            for age in CLIMBED_AGES for rule in [scenario.ages.two_from(PREVIOUS[age])])
        self.standing_buildings = self._standing_buildings()
        self._could_have_building: dict[Age2BuildingData, bool] = {}
        self.resource_origins = self._resource_origins()
        self.dropsite_choices: list[DropsiteChoice] = []
        rule_index = 0   # where the method's rule sits in gather_method_rules
        
        for index, origin in enumerate(self.resource_origins):
            for method in origin.gather_methods:
                self.dropsite_choices += [DropsiteChoice(index, rule_index, method.seed, choice)
                                        for choice in dropsite_chioces(method.seed)]
                rule_index += 1
        
        self.gather_method_choices: tuple[GatherMethodChoice, ...] = tuple(GatherMethodChoice(choice.source, choice.rule)
                                           for choice in self.dropsite_choices)

        self.required_purchases = {
            location: rule for location, rule
            in scenario.starting_state.required_purchases.items()
            if not isinstance(rule, False_)
        }
        
        self.cost_waivers: list[CostWaiver] = self._waivers()
        self._precursors: dict[PricedLocation, list[_Priced]] = {}
        self._needed: dict[frozenset[PricedLocation], frozenset[PricedLocation]] = {}
        self.order, self.pruned = self._build_order()

    @property
    def gather_method_rules(self) -> list[Rule.Resolved]:
        """Every gather method's rule, flat, in the order DropsiteChoice.rule counts them."""
        return [method.rule for origin in self.resource_origins
                for method in origin.gather_methods]

    def _standing_buildings(self) -> dict[Age2BuildingData, Rule]:
        standing = self.scenario.starting_state.starts_with_building
        return {building: standing[building] for building in Age2BuildingData
                if self.scenario.civilization.can_build(building)
                and not isinstance(standing[building], False_)}

    def choice_order(self, building: Age2BuildingData) -> int:
        """Where a building stands among choices: the seed's building order."""
        return self.world.pool.budget.building_order[building]

    def impossible(self, rule: Rule) -> bool:
        return rule.resolve(self.world).always_false

    def could_have(self, building: Age2BuildingData) -> bool:
        if building not in self._could_have_building:
            self._could_have_building[building] = not self.impossible(self.scenario.has_building(building))
        return self._could_have_building[building]

    def _resource_origins(self) -> list[ScenarioOrigin]:
        """The resource origins this scenario could ever count toward its budget, each with the
        gather methods it could use here and the seed each is paid for with."""
        economy = self.scenario.economy
        relic_sum = relic_allowance(self.scenario.scenario)
        origins = []
        for origin in RESOURCE_ORIGINS:
            resolved_methods: list[ResolvedGatherMethod] = []
            for method in origin.gather_methods:
                resolved = method.rule(economy).resolve(self.world)   # once: every budget total reuses it
                if not resolved.always_false:
                    resolved_methods.append(ResolvedGatherMethod(resolved, method.seed.in_scenario(
                        self.start_age, self.age_up_buildings, self.could_have,
                        self.choice_order)))
            allowance = relic_sum if origin.per_relic else SOURCE_ALLOWANCE
            if resolved_methods and allowance:
                origins.append(ScenarioOrigin(origin.name, origin.resource, allowance,
                                              tuple(resolved_methods)))
        return origins

    def max_budget(self) -> dict[Resource, int]:
        """Every starting resource in the pool, and every source the scenario could ever count."""
        budget = {resource: self.world.pool.resources.totals[resource]
                  for resource in SAMPLED_RESOURCES}
        for origin in self.resource_origins:
            budget[origin.resource] += origin.allowance
        return budget

    def seed_parts(self, need: Need, requirement: Requirement,
                   waived: frozenset[Age2BuildingData]) -> tuple[tuple[Part, ...], ...]:
        """What each way's seed buys, against this running total."""
        return tuple(seed_parts(choice.seed, choice.site, need, requirement, waived,
                                self.start_age)
                     for choice in self.dropsite_choices)

    def priced(self, location: PricedLocation) -> _Priced | None:
        """The location as this scenario pays for it, or None if its own rule, less paying,
        could never be true here."""
        return self._priced(budget_item(location))

    def _priced(self, item: BudgetItem) -> _Priced | None:
        if self.impossible(item.scenario_rule(self.scenario)):
            return None
        return _Priced(item, item.charges_in_scenario(self.scenario))

    def plan(self, entries: Iterable[_Priced]) -> Need:
        return sum((entry.need for entry in entries), Need()).in_scenario(
            self.start_age, self.age_up_buildings, self.could_have, self.choice_order)

    def _build_order(self) -> tuple[list[_Priced], list[_Priced]]:
        """The order, and what was pruned from it: every entry, each after its precursors, less
        what could never fit the most the scenario could ever have."""
        self._initial_order = self._entries()
        self._precursors = {entry.location: self.precursors(entry)
                            for entry in self._initial_order}
        return self._prune(self._with_precursors())

    def _entries(self) -> list[_Priced]:
        """The scenario's own purchases, its base, and the seed's sample, each as the scenario
        pays for it - less what its own rule could never allow here - by age. Within an age the
        purchases come first, then the base, then the sample in the seed's rank."""
        budget = self.world.pool.budget
        purchases = self.scenario.starting_state.required_purchases
        items: list[BudgetItem] = [
            *(ScenarioBudgetItem(budget_item(location)) for location in purchases),
            budget_item(BASE),
            *(budget_item(location) for location in budget.entries
              if location not in purchases),
        ]

        def place(entry: _Priced) -> tuple[Age2AgeData, int, int]:
            if entry.item.first_in_age:
                return entry.age, 0, 0   # the sort is stable: purchases, then the base
            return entry.age, 1, budget.rank[entry.location]

        return sorted(filter(None, map(self._priced, items)), key=place)

    def _with_precursors(self) -> list[_Priced]:
        """Every entry, each after its precursors, each location once - where it first comes
        (a dict keeps a key where it was first put)."""
        placed: dict[PricedLocation, _Priced] = {}
        for entry in self._initial_order:
            for precursor in (*self._precursors[entry.location], entry):
                placed[precursor.location] = precursor
        return list(placed.values())

    def _prune(self, ordered: list[_Priced]) -> tuple[list[_Priced], list[_Priced]]:
        """Walk the order, dropping each entry that, with everything kept before it, could not
        be paid for even at the most: every starting resource in the pool, every building that
        can stand standing, every gather method brought in, seeds paid for."""
        pile = {resource: self.world.pool.resources.totals[resource]
                for resource in SAMPLED_RESOURCES}
        every_standing_building = frozenset(self.standing_buildings)
        every_gather_method_choice = list(range(len(self.gather_method_choices)))
        kept: list[_Priced] = []
        pruned: list[_Priced] = []
        for entry in ordered:
            need = self.plan(kept + [entry])
            requirement = Requirement(need, every_standing_building)
            fits = pays(pile, dict(requirement.cost), every_gather_method_choice,
                        self.gather_method_choices,
                        self.seed_parts(need, requirement, every_standing_building),
                        self.resource_origins)
            (kept if fits else pruned).append(entry)
        return kept, pruned

    def precursors(self, entry: _Priced) -> list[_Priced]:
        """The locations this seed that the entry cannot be had without."""
        requirement = Requirement(self.plan([entry]), frozenset())
        candidates: list[PricedLocation] = [
            *self._prerequisite_buildings(requirement),
            *requirement.ages,
            *self._prerequisite_techs(entry)
        ]

        pool = self.world.pool
        found = [self._priced(item) for item in map(budget_item, candidates)
                 if item.is_location(pool)]
        
        return sorted((precursor for precursor in found
                       if precursor is not None and precursor.location is not entry.location),
                      key=lambda precursor: (precursor.age, precursor.item.rank))

    @staticmethod
    def _prerequisite_buildings(requirement: Requirement) -> list[Age2BuildingData]:
        """The buildings a requirement charges, each after the prerequisites it also charges."""
        charged = set(requirement.buildings)
        ordered: list[Age2BuildingData] = []
        for building in requirement.buildings:
            chain: list[Age2BuildingData] = []
            while building in charged and building not in ordered and building not in chain:
                chain.append(building)
                building = BUILDING_PREREQUISITE.get(building)
            ordered += reversed(chain)  # earliest in the chain first.
        return ordered

    @staticmethod
    def _prerequisite_techs(entry: _Priced) -> list[Age2TechData]:
        """The techs below the entry it actually pays for, oldest first."""
        paid = {price.identity for price in entry.need.own_price}
        return [tech.location for tech 
                in reversed(list(entry.item.prerequisite_techs()))   # earliest in the chain first.
                if tech.location in paid]

    def needed(self, dropped: frozenset[PricedLocation]) -> frozenset[PricedLocation]:
        """What the order still needs once these purchases are unnecessary: everything but them
        and what only they brought in."""
        if dropped not in self._needed:
            self._needed[dropped] = frozenset(
                precursor.location for entry in self._initial_order if entry.location not in dropped
                for precursor in (*self._precursors[entry.location], entry))
        return self._needed[dropped]

    def running_total_for(self, location: PricedLocation,
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

    def _waivers(self) -> list[CostWaiver]:
        """The standing buildings and the purchases a rule can spare, gathered by rule."""
        waivers: list[CostWaiver] = []

        def waiver(rule: Rule) -> CostWaiver:
            resolved = rule.resolve(self.world)
            same = next((waiver for waiver in waivers if waiver.rule == resolved), None)
            if same is None:
                same = CostWaiver(resolved, [], [])
                waivers.append(same)
            return same

        for building, rule in self.standing_buildings.items():
            waiver(rule).buildings.append(building)
        for location, rule in self.required_purchases.items():
            waiver(rule).purchases.append(location)
        return waivers
