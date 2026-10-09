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
from .BudgetSource import ScenarioResourceOrigins
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

_ITEMS: dict[type, type[BudgetItem]] = {
    Age2AgeData: AgeBudgetItem,
    Age2BuildingData: BuildingBudgetItem,
    Age2TechData: TechBudgetItem,
    Age2UnitData: UnitBudgetItem,
    Age2BaseData: BaseBudgetItem,
}

class CostWaiver(NamedTuple):
    rule: Rule.Resolved
    buildings: list[Age2BuildingData]
    purchases: list[PricedLocation]

class OrderPlace(NamedTuple):
    """Where an entry goes in a scenario's order, compared field by field: by age, then the
    scenario's own entries - its purchases, then its base - ahead of the sample, then the sample
    in the seed's rank."""
    age: Age2AgeData
    from_seed: bool
    """True if from the world's BudgetPool."""
    rank: int
    """The seed's rank for a sampled entry."""

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
    logic = scenario.logic
    key = scenario.scenario
    if key not in logic.budget_orders:
        if key in logic.budget_orders_open:
            raise RecursionError(
                f"{key.scenario_name}'s budget order asks for itself; it would never be built"
            )
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
            AgeUpBuildings(age, rule.buildings, rule.single_building) for age in CLIMBED_AGES
                for rule in [scenario.ages.two_from(PREVIOUS[age])]
        )

        self.standing_buildings = self._standing_buildings()
        self._could_have_building: dict[Age2BuildingData, bool] = {}

        self.resource_origins = ScenarioResourceOrigins.from_scenario(scenario, world, self.settle)

        self.required_purchases = {
            location: rule for location, rule in scenario.starting_state.required_purchases.items()
                if not isinstance(rule, False_)
        }
        self.cost_waivers: list[CostWaiver] = self._waivers()

        self._precursors: dict[PricedLocation, list[_Priced]] = {}
        self._needed: dict[frozenset[PricedLocation], frozenset[PricedLocation]] = {}
        self.order, self.pruned = self._build_order()

    # -- the scenario's terms -----------------------------------------------------------------

    def choice_order(self, building: Age2BuildingData) -> int:
        """Where a building stands among choices: the seed's building order."""
        return self.world.pool.budget.building_order[building]

    def is_impossible(self, rule: Rule) -> bool:
        return rule.resolve(self.world).always_false

    def could_have(self, building: Age2BuildingData) -> bool:
        if building not in self._could_have_building:
            has_building = self.scenario.has_building(building)
            self._could_have_building[building] = not self.is_impossible(has_building)
        return self._could_have_building[building]

    def settle(self, need: Need) -> Need:
        return need.by_scenario(
            self.start_age,
            self.age_up_buildings,
            self.could_have,
            self.choice_order,
        )

    def max_budget(self) -> dict[Resource, int]:
        """Every starting resource in the pool, and every source the scenario could ever count."""
        max_budget = {
            resource: self.world.pool.resources.totals[resource] for resource in SAMPLED_RESOURCES
        }

        for resource, amount in self.resource_origins.allowance().items():
            max_budget[resource] += amount
        return max_budget

    # -- pricing ------------------------------------------------------------------------------

    def priced(self, location: PricedLocation) -> _Priced | None:
        """The location as this scenario pays for it, or None if its own rule, less paying,
        could never be true here."""
        return self._priced(budget_item(location))

    def _priced(self, item: BudgetItem) -> _Priced | None:
        if self.is_impossible(item.scenario_rule(self.scenario)):
            return None
        return _Priced(item, item.need_in(self.scenario))

    def plan(self, budget_items: Iterable[_Priced]) -> Need:
        return self.settle(sum((budget_item.need for budget_item in budget_items), Need()))

    # -- the order ----------------------------------------------------------------------------

    def _build_order(self) -> tuple[list[_Priced], list[_Priced]]:
        """The order, and what was pruned from it."""
        self._initial_order = self._entries()

        self._precursors = {
            entry.location: self.precursors(entry) for entry in self._initial_order
        }

        return self._prune_order(self._with_precursors())

    def _entries(self) -> list[_Priced]:
        """The scenario's own purchases, its base, and the seed's sample."""
        budget = self.world.pool.budget
        required_purchases = self.scenario.starting_state.required_purchases

        # Added in order: scenario item, starting base, budget entries.
        items: list[BudgetItem] = [
            *(ScenarioBudgetItem(budget_item(location)) for location in required_purchases),
            budget_item(BASE),
            *(budget_item(location) for location in budget.entries
                if location not in required_purchases),
        ]

        def place(entry: _Priced) -> OrderPlace:
            if entry.item.first_in_age:
                return OrderPlace(entry.age, from_seed=False, rank=0)
            return OrderPlace(entry.age, from_seed=True, rank=budget.rank[entry.location])

        return sorted(filter(None, map(self._priced, items)), key=place)

    def precursors(self, entry: _Priced) -> list[_Priced]:
        """The locations this seed that the entry cannot be had without."""
        requirement = Requirement(self.plan([entry]), frozenset())

        candidates: list[PricedLocation] = [
            *self._prerequisite_buildings(requirement),
            *requirement.ages,
            *self._prerequisite_techs(entry),
        ]

        pool = self.world.pool
        found = [
            self._priced(item) for item in map(budget_item, candidates)
                if item.is_location(pool)
        ]

        # Only an age can name itself here: reaching the Castle Age charges the Castle Age.
        return sorted(
            (
                precursor for precursor in found
                    if precursor is not None and precursor.location is not entry.location
            ),
            key=lambda precursor: (precursor.age, precursor.item.rank),
        )

    def _with_precursors(self) -> list[_Priced]:
        placed: dict[PricedLocation, _Priced] = {}
        for entry in self._initial_order:
            for precursor in (*self._precursors[entry.location], entry):
                placed[precursor.location] = precursor
        return list(placed.values())

    def _prune_order(
        self,
        ordered_budget: list[_Priced],
    ) -> tuple[list[_Priced], list[_Priced]]:
        pile = {
            resource: self.world.pool.resources.totals[resource] for resource in SAMPLED_RESOURCES
        }

        every_standing_building = frozenset(self.standing_buildings)
        funded: list[_Priced] = []
        pruned: list[_Priced] = []

        for budget_item in ordered_budget:
            need = self.plan(funded + [budget_item])
            requirement = Requirement(need, every_standing_building)
            parts = self.resource_origins.seed_parts(
                need,
                requirement,
                every_standing_building,
                self.start_age,
            )
            can_fund = self.resource_origins.can_cover(
                pile,
                dict(requirement.cost),
                self.resource_origins.every_choice,
                parts,
            )

            (funded if can_fund else pruned).append(budget_item)
        return funded, pruned

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
            ordered += reversed(chain)   # earliest in the chain first
        return ordered

    @staticmethod
    def _prerequisite_techs(entry: _Priced) -> list[Age2TechData]:
        """The techs below the entry it actually pays for, oldest first."""
        paid = {price.identity for price in entry.need.own_price}
        oldest_first = reversed(list(entry.item.prerequisite_techs()))
        return [
            tech.location for tech in oldest_first
                if tech.location in paid
        ]

    # -- running totals -----------------------------------------------------------------------

    def needed(self, dropped: frozenset[PricedLocation]) -> frozenset[PricedLocation]:
        if dropped not in self._needed:
            self._needed[dropped] = frozenset(
                precursor.location for entry in self._initial_order
                    if entry.location not in dropped
                        for precursor in (*self._precursors[entry.location], entry)
            )
        return self._needed[dropped]

    def running_total_for(
        self,
        location: PricedLocation,
        dropped: frozenset[PricedLocation] = frozenset(),
    ) -> Need | None:
        index = next(
            (n for n, entry in enumerate(self.order) if entry.location is location),
            None,
        )
        if index is None:
            return None

        needed = self.needed(dropped)
        return self.plan(
            entry for entry in self.order[:index + 1]
                if entry.location in needed or entry.location is location
        )

    # -- waivers ------------------------------------------------------------------------------

    def _standing_buildings(self) -> dict[Age2BuildingData, Rule]:
        standing = self.scenario.starting_state.starts_with_building
        return {
            building: standing[building] for building in Age2BuildingData
                if self.scenario.civilization.can_build(building)
                and not isinstance(standing[building], False_)
        }

    def _waivers(self) -> list[CostWaiver]:
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
