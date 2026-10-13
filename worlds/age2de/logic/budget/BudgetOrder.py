from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING, Iterable

from ...items.Items import Resource
from ...locations.Ages import Age2AgeData
from ...locations.Buildings import BUILDING_PREREQUISITE, Age2BuildingData
from ...locations.Techs import Age2TechData
from .BudgetItem import BASE, BudgetItem, PricedLocation, for_location
from .Need import Cost, Need
from .Requirement import Requirement

if TYPE_CHECKING:
    from ..ScenarioLogic import ScenarioLogic

@dataclasses.dataclass(frozen=True)
class PricedBudgetItem:
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

        self._precursors: dict[PricedLocation, list[PricedBudgetItem]] = {}
        self._needed: dict[frozenset[PricedLocation], frozenset[PricedLocation]] = {}
        self.order = self._build_order()

    # -- pricing ------------------------------------------------------------------------------

    def get_priced_item(self, location: PricedLocation) -> PricedBudgetItem | None:
        item = for_location(location)
        if self.scenario.logic.is_impossible(item.scenario_rule(self.scenario)):
            return None
        return PricedBudgetItem(item, item.need_in_scenario(self.scenario))

    def plan(self, budget_items: Iterable[PricedBudgetItem]) -> Need:
        total = sum((budget_item.need for budget_item in budget_items), Need())
        return self.scenario.budget.settle(total)

    def requirement(
        self,
        budget_items: Iterable[PricedBudgetItem],
        waived: frozenset[Age2BuildingData] = frozenset(),
    ) -> Requirement:
        """What these entries cost together in this scenario, with `waived` standing."""
        return Requirement(self.plan(budget_items), waived, self.scenario.budget.terms)

    # -- the order ----------------------------------------------------------------------------

    def _build_order(self) -> list[PricedBudgetItem]:
        """The entries in their places, each after its precursors."""
        self._initial_order = self._entries()

        self._precursors = {
            entry.location: self.precursors(entry) for entry in self._initial_order
        }

        return self._with_precursors()

    def _entries(self) -> list[PricedBudgetItem]:
        budget = self.world.pool.budget
        required_purchases = self.scenario.starting_state.required_purchases

        # Added in order: the scenario's purchases, its base, the seed's sample.
        locations: list[PricedLocation] = [
            *required_purchases,
            BASE,
            *(location for location in budget.entries if location not in required_purchases),
        ]

        def place(entry: PricedBudgetItem) -> tuple[Age2AgeData, bool, int]:
            if entry.location is BASE or entry.location in required_purchases:
                return entry.age, False, 0
            return entry.age, True, budget.rank[entry.location]

        return sorted(filter(None, map(self.get_priced_item, locations)), key=place)

    def precursors(self, entry: PricedBudgetItem) -> list[PricedBudgetItem]:
        requirement = self.requirement([entry])

        candidates: list[PricedLocation] = [
            *self._prerequisite_buildings(requirement),
            *requirement.ages,
            *self._prerequisite_techs(entry),
        ]

        # Only an age, building or tech that is a location this seed can stand in the order.
        pool = self.world.pool
        found = [
            self.get_priced_item(location) for location in candidates
                if location in pool.ages.locations
                    or location in pool.buildings.locations
                    or location in pool.techs.shuffled
        ]

        # Only an age can name itself here: reaching the Castle Age charges the Castle Age.
        return sorted(
            (precursor for precursor in found
                    if precursor is not None and precursor.location is not entry.location),
            key=lambda precursor: (precursor.age, precursor.item.rank),
        )

    def _with_precursors(self) -> list[PricedBudgetItem]:
        placed: dict[PricedLocation, PricedBudgetItem] = {}
        for entry in self._initial_order:
            for precursor in (*self._precursors[entry.location], entry):
                placed[precursor.location] = precursor
        return list(placed.values())

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
    def _prerequisite_techs(entry: PricedBudgetItem) -> list[Age2TechData]:
        """The techs below the entry it actually pays for, oldest first."""
        paid = {price.identity for price in entry.need.own_price}
        return [tech for tech in reversed(entry.item.techs_below) if tech in paid]

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

    # -- the spoiler --------------------------------------------------------------------------

    def spoiler_lines(self) -> list[str]:
        """The order as the spoiler lists it: each entry, what it would cost alone, and the
        running total it asks - with no waiver holding, and with every one.

        A resource the total asks more of than every pile item in the seed adds up to can only
        come from an easy source, so it shows as easy. An entry whose own price is paid only in
        easy resources, even with every waiver, gets nothing from the budget, and is left out."""
        from .CostTable import CostTable   # the table reads the order back

        most_pile = self.world.pool.resources.totals
        budget = self.scenario.budget
        name = self.scenario.scenario.scenario_name
        lines = [f"{name} (pays up from the {budget.start_age.name.title()} Age)"]
        for waiver in budget.always_waived:
            lines.append(f"    always: {waiver.explain_str()}")
        for waiver in budget.cost_waivers:
            lines.append(f"    waiver: {waiver.explain_str()}")

        rows: list[tuple[int, str, str, str]] = []
        for number, entry in enumerate(self.order, start=1):
            table = CostTable.for_location(self, entry.location)
            alone = Need.as_cost(self.requirement([entry]).cost)
            least, most = table.totals_by_mask[-1].cost, table.totals_by_mask[0].cost
            # The base asks no easy source: the pile alone pays for it.
            pile_limit = None if entry.location is BASE else most_pile
            if pile_limit is not None and self._is_paid_only_by_easy(entry, least, pile_limit):
                continue
            total = self._cost_text(most, pile_limit)
            if least != most:
                total += f" ({self._cost_text(least, pile_limit)} with every waiver)"
            rows.append((number, entry.location.location_name, self._cost_text(alone), total))

        # Columns as wide as their longest cell, so the total always starts past every cost.
        name_width = max((len(location_name) for _, location_name, _, _ in rows), default=0)
        alone_width = max((len(alone) for _, _, alone, _ in rows), default=0)
        for number, location_name, alone, total in rows:
            lines.append(
                f"    {number:>3}. {location_name:<{name_width}}  "
                f"alone {alone:<{alone_width}}  total {total}"
            )
        return lines

    @staticmethod
    def _is_paid_only_by_easy(
        entry: BudgetItem,
        total: Cost,
        pile_limit: dict[Resource, int],
    ) -> bool:
        """Whether every resource the entry's own price asks is one the total has run past the
        pile on. Stone left under its limit does not keep a food-and-gold tech in."""
        asked = dict(total)
        paid_in = [resource for resource, amount in entry.location.cost.items() if amount > 0]
        return bool(paid_in) and all(
            resource in asked and asked[resource] > pile_limit[resource]
                for resource in paid_in
        )

    @staticmethod
    def _cost_text(cost: Cost, pile_limit: dict[Resource, int] | None = None) -> str:
        """A cost as text. With a pile limit, an amount past it shows as easy."""
        return ", ".join(
            f"easy {resource.name.lower()}"
                if pile_limit is not None and amount > pile_limit[resource]
                else f"{amount} {resource.name.lower()}"
                for resource, amount in cost
        ) or "free"
