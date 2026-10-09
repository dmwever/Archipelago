from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING, Iterable

from ...generation.pools.BudgetPool import SAMPLED_RESOURCES
from ...items.Items import Resource
from ...locations.Ages import Age2AgeData
from ...locations.Buildings import BUILDING_PREREQUISITE, Age2BuildingData
from ...locations.Techs import Age2TechData
from .BudgetItem import BASE, BudgetItem, PricedLocation
from .BudgetItemFactory import BudgetItemFactory
from .BudgetSource import ScenarioResourceOrigins
from .Need import Need
from .Requirement import Requirement
from .ScenarioBudgetItem import ScenarioBudgetItem

if TYPE_CHECKING:
    from ..ScenarioLogic import ScenarioLogic

@dataclasses.dataclass(frozen=True, order=True)
class OrderPlace:
    """Where an entry goes in a scenario's order - compared by value, field by field, as it is a
    sort key: by age, then the
    scenario's own entries - its purchases, then its base - ahead of the sample, then the sample
    in the seed's rank."""
    age: Age2AgeData
    from_seed: bool
    """True if from the world's BudgetPool."""
    rank: int
    """The seed's rank for a sampled entry."""

@dataclasses.dataclass(frozen=True)
class ScenarioPricedBudgetItem:
    """One budget item as one scenario would pay for it: the item, and its need in that
    scenario - its own node and the techs below it the scenario does not have for itself."""
    item: BudgetItem
    need: Need

    @property
    def location(self) -> PricedLocation:
        return self.item.location

    @property
    def age(self) -> Age2AgeData:
        return self.item.age

class BudgetOrder:
    def __init__(self, scenario: 'ScenarioLogic') -> None:
        self.scenario = scenario
        self.world = scenario.logic.world

        self.resource_origins = ScenarioResourceOrigins.from_scenario(scenario, self.world)

        self._precursors: dict[PricedLocation, list[ScenarioPricedBudgetItem]] = {}
        self._needed: dict[frozenset[PricedLocation], frozenset[PricedLocation]] = {}
        self.order, self.pruned = self._build_order()

    # -- the budget -----------------------------------------------------------------------------

    def max_budget(self) -> dict[Resource, int]:
        """Every starting resource in the pool, and every source the scenario could ever count."""
        max_budget = {
            resource: self.world.pool.resources.totals[resource] for resource in SAMPLED_RESOURCES
        }

        for resource, amount in self.resource_origins.allowance().items():
            max_budget[resource] += amount
        return max_budget

    # -- pricing ------------------------------------------------------------------------------

    def get_scenario_priced_location(
        self,
        location: PricedLocation,
    ) -> ScenarioPricedBudgetItem | None:
        """The location as this scenario pays for it, or None if its own rule, less paying,
        could never be true here."""
        return self.get_scenario_priced_budget_item(BudgetItemFactory.for_location(location))

    def get_scenario_priced_budget_item(
        self,
        item: BudgetItem,
    ) -> ScenarioPricedBudgetItem | None:
        if self.scenario.logic.is_impossible(item.scenario_rule(self.scenario)):
            return None
        return ScenarioPricedBudgetItem(item, item.need_in_scenario(self.scenario))

    def plan(self, budget_items: Iterable[ScenarioPricedBudgetItem]) -> Need:
        total = sum((budget_item.need for budget_item in budget_items), Need())
        return self.scenario.budget.settle(total)

    # -- the order ----------------------------------------------------------------------------

    def _build_order(self) -> tuple[list[ScenarioPricedBudgetItem], list[ScenarioPricedBudgetItem]]:
        """The order, and what was pruned from it."""
        self._initial_order = self._entries()

        self._precursors = {
            entry.location: self.precursors(entry) for entry in self._initial_order
        }

        return self._prune_order(self._with_precursors())

    def _entries(self) -> list[ScenarioPricedBudgetItem]:
        """The scenario's own purchases, its base, and the seed's sample."""
        budget = self.world.pool.budget
        required_purchases = self.scenario.starting_state.required_purchases

        # Added in order: scenario item, starting base, budget entries.
        items: list[BudgetItem] = [
            *(
                ScenarioBudgetItem(BudgetItemFactory.for_location(location))
                    for location in required_purchases
            ),
            BudgetItemFactory.for_location(BASE),
            *(BudgetItemFactory.for_location(location) for location in budget.entries
                if location not in required_purchases),
        ]

        def place(entry: ScenarioPricedBudgetItem) -> OrderPlace:
            if entry.item.first_in_age:
                return OrderPlace(entry.age, from_seed=False, rank=0)
            return OrderPlace(entry.age, from_seed=True, rank=budget.rank[entry.location])

        priced = map(self.get_scenario_priced_budget_item, items)
        return sorted(filter(None, priced), key=place)

    def precursors(self, entry: ScenarioPricedBudgetItem) -> list[ScenarioPricedBudgetItem]:
        """The locations this seed that the entry cannot be had without."""
        requirement = Requirement(self.plan([entry]), frozenset())

        candidates: list[PricedLocation] = [
            *self._prerequisite_buildings(requirement),
            *requirement.ages,
            *self._prerequisite_techs(entry),
        ]

        pool = self.world.pool
        found = [
            self.get_scenario_priced_budget_item(item)
                for item in map(BudgetItemFactory.for_location, candidates)
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

    def _with_precursors(self) -> list[ScenarioPricedBudgetItem]:
        placed: dict[PricedLocation, ScenarioPricedBudgetItem] = {}
        for entry in self._initial_order:
            for precursor in (*self._precursors[entry.location], entry):
                placed[precursor.location] = precursor
        return list(placed.values())

    def _prune_order(
        self,
        ordered_budget: list[ScenarioPricedBudgetItem],
    ) -> tuple[list[ScenarioPricedBudgetItem], list[ScenarioPricedBudgetItem]]:
        pile = {
            resource: self.world.pool.resources.totals[resource] for resource in SAMPLED_RESOURCES
        }

        every_standing_building = frozenset(self.scenario.budget.standing_buildings)
        funded: list[ScenarioPricedBudgetItem] = []
        pruned: list[ScenarioPricedBudgetItem] = []

        for budget_item in ordered_budget:
            need = self.plan(funded + [budget_item])
            requirement = Requirement(need, every_standing_building)
            parts = self.resource_origins.seed_parts(
                need,
                requirement,
                every_standing_building,
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
    def _prerequisite_techs(entry: ScenarioPricedBudgetItem) -> list[Age2TechData]:
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
