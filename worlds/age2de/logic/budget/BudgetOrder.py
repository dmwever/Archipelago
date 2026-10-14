from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING, Collection, Iterable, Mapping, Sequence

from rule_builder.rules import Rule

from ...generation.pools.BudgetPool import SAMPLED_RESOURCES, VILLAGER
from ...items.Items import Resource
from ...locations.Ages import Age2AgeData
from ...locations.Buildings import BUILDING_PREREQUISITE, Age2BuildingData
from ...locations.Techs import Age2TechData
from .BudgetItem import BASE, BudgetItem, PricedLocation, for_location, villager_food
from .Need import Cost, Need
from .Requirement import Requirement

if TYPE_CHECKING:
    from ..ScenarioLogic import ScenarioLogic
    from ..custom_logic.ScenarioQuestions import ScenarioCostWaived
    from BaseClasses import CollectionState

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
        self._standing_precursors: dict[frozenset[Age2BuildingData],
                                        dict[PricedLocation, list[PricedBudgetItem]]] = {}
        self._needed: dict[tuple[frozenset[PricedLocation], frozenset[Age2BuildingData]],
                           frozenset[PricedLocation]] = {}
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

    def precursors(self, entry: PricedBudgetItem,
                   waived: frozenset[Age2BuildingData] = frozenset()) -> list[PricedBudgetItem]:
        requirement = self.requirement([entry], waived)

        candidates: list[PricedLocation] = [
            *self._prerequisite_buildings(requirement),
            *requirement.ages,
            *self._prerequisite_techs(entry),
        ]

        # Only an age, building or tech that is a location this seed can stand in the order.
        pool = self.world.pool
        found = [
            self.get_priced_item(location) for location in candidates
                if location in pool.budget.ages
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

    def needed(self, dropped: frozenset[PricedLocation],
               waived: frozenset[Age2BuildingData] = frozenset()) -> frozenset[PricedLocation]:
        key = (dropped, waived)
        if key not in self._needed:
            precursors = self._precursors_with(waived)
            self._needed[key] = frozenset(
                precursor.location for entry in self._initial_order
                    if entry.location not in dropped
                        for precursor in (*precursors[entry.location], entry)
            )
        return self._needed[key]

    def _precursors_with(self, waived: frozenset[Age2BuildingData]) -> dict[PricedLocation, list[PricedBudgetItem]]:
        if not waived:
            return self._precursors
        if waived not in self._standing_precursors:
            self._standing_precursors[waived] = {
                entry.location: self.precursors(entry, waived) for entry in self._initial_order
            }
        return self._standing_precursors[waived]

    def running_total_for(
        self,
        location: PricedLocation,
        dropped: frozenset[PricedLocation] = frozenset(),
        waived: frozenset[Age2BuildingData] = frozenset(),
    ) -> Need | None:
        index = next(
            (n for n, entry in enumerate(self.order) if entry.location is location),
            None,
        )
        if index is None:
            return None

        needed = self.needed(dropped, waived)
        return self.plan(
            entry for entry in self.order[:index + 1]
                if entry.location in needed or entry.location is location
        )

    # -- the spoiler --------------------------------------------------------------------------

    def spoiler_lines(self, states: Sequence[CollectionState], first: Mapping[str, int]) -> list[str]:
        """The order as the spoiler lists it, against this seed's playthrough: each entry the
        seed expects the starting pile to pay for, the sphere it comes into logic in, what it
        costs alone, and the running total it asks then - with the waivers that hold by then.

        An entry shows in this scenario only if this scenario's budget pays for it in the sphere
        it first comes into logic. A resource this scenario has an easy source of by then shows
        starred. An entry whose own price is all starred is the easy sources' to pay, not the
        pile's, and is left out - and so is any entry that needs one left out. With nothing left,
        there is no budget to show."""
        from .CostTable import CostTable   # the table reads the order back

        scenario = self.scenario
        budget = scenario.budget
        unlocked = self._first_holding(scenario.is_unlocked(), states)
        if unlocked is None:
            return []

        every_waived = frozenset(
            building for waiver in (*budget.always_waived, *budget.cost_waivers)
                for building in waiver.buildings
        )
        hidden: set[PricedLocation] = set()
        rows: list[tuple[int, str, str, str, str]] = []
        for number, entry in enumerate(self.order, start=1):
            sphere = self._paid_in_sphere(entry, states, first, unlocked)
            if sphere is None:
                hidden.add(entry.location)
                continue
            # The base asks no easy source: the pile alone pays for it.
            easy = set() if entry.location is BASE else {
                resource for resource in SAMPLED_RESOURCES
                    if self._holds(scenario.economy.has_easy_source(resource), states[sphere])
            }
            alone = self._own_price(entry)
            paid_in = [resource for resource, amount in alone if amount > 0]
            if paid_in and all(resource in easy for resource in paid_in):
                hidden.add(entry.location)
                continue
            # Nor is one shown that needs a hidden one: it waits on the same easy source.
            needs = self.precursors(entry, every_waived)
            if any(precursor.location in hidden for precursor in needs):
                hidden.add(entry.location)
                continue
            table = CostTable.for_location(self, entry.location)
            total = table.total(states[sphere]).cost
            rows.append((
                number,
                f"[s{sphere + 1}]",
                self._row_name(entry),
                self._cost_text(alone),
                f"total: {self._cost_text(total, easy)}",
            ))
        if not rows:
            return []

        name = scenario.scenario.scenario_name
        lines = [f"{name} (pays up from the {budget.start_age.name.title()} Age, "
                 f"unlocked in sphere {unlocked + 1})"]
        for waiver in budget.always_waived:
            let_off = self._what_it_lets_off(waiver)
            if let_off:
                lines.append(f"    always: {let_off}: {waiver.answer.explain_str()}")
        for waiver in budget.cost_waivers:
            let_off = self._what_it_lets_off(waiver)
            if not let_off:
                continue
            held = self._first_holding(waiver, states)
            when = "never holds" if held is None else f"holds by sphere {held + 1}"
            lines.append(f"    waiver ({when}): {let_off}: {waiver.answer.explain_str()}")

        # Columns as wide as their longest cell, so the total always starts past every cost.
        sphere_width = max(len(sphere) for _, sphere, _, _, _ in rows)
        name_width = max(len(location_name) for _, _, location_name, _, _ in rows)
        alone_width = max(len(alone) for _, _, _, alone, _ in rows)
        for number, sphere, location_name, alone, total in rows:
            lines.append(
                f"    {number:>3}. {sphere:<{sphere_width}} {location_name:<{name_width}}  "
                f"{alone:<{alone_width}}  {total}"
            )
        return lines

    def _paid_in_sphere(
        self,
        entry: PricedBudgetItem,
        states: Sequence[CollectionState],
        first: Mapping[str, int],
        unlocked: int,
    ) -> int | None:
        """The sphere the entry first comes into logic in, if this scenario's budget pays for it
        then; None if it never does, or some other way gets there first. The base is no location:
        its sphere is the first one this scenario can have a base paid for in."""
        from .BudgetTotal import BudgetTotal   # the total reads the order back

        scenario = self.scenario
        location = entry.location
        if location is BASE:
            return self._first_holding(scenario.has_base(), states, unlocked)

        easily = tuple(sorted(
            (resource for resource, amount in location.cost.items() if amount > 0),
            key=lambda resource: resource.value,
        ))
        paid = (scenario.is_unlocked()
                & entry.item.scenario_rule(scenario)
                & BudgetTotal(scenario=scenario.scenario, location=location, easily=easily))
        name = location.location_name
        if location in self.world.pool.budget.ages and location not in self.world.pool.ages.locations:
            return self._first_holding(paid, states, unlocked)
        if name not in first:
            return None
        sphere = first[name]
        return sphere if self._holds(paid, states[sphere]) else None

    def _holds(self, rule: Rule | Rule.Resolved, state: CollectionState) -> bool:
        resolved = rule if isinstance(rule, Rule.Resolved) else rule.resolve(self.world)
        return resolved(state)

    def _first_holding(
        self,
        rule: Rule | Rule.Resolved,
        states: Sequence[CollectionState],
        since: int = 0,
    ) -> int | None:
        """The first sphere, from `since` on, whose items make the rule hold; None if none do."""
        return next(
            (sphere for sphere in range(since, len(states)) if self._holds(rule, states[sphere])),
            None,
        )

    def _what_it_lets_off(self, waiver: ScenarioCostWaived.Resolved) -> str:
        """The buildings and purchases of a waiver that take something off this order's total,
        as text. A building the order draws is paid for anyway, since its check needs a new one
        built, and one nothing in the order needs saves nothing either: neither is named."""
        budget = self.scenario.budget
        always_waived = frozenset(
            building for always in budget.always_waived for building in always.buildings
        )
        always_dropped = frozenset(
            purchase for always in budget.always_waived for purchase in always.purchases
        )

        def full_cost(dropped: frozenset[PricedLocation],
                      waived: frozenset[Age2BuildingData]) -> dict[Resource, int]:
            """What the whole order costs with these let off."""
            need = self.running_total_for(self.order[-1].location, dropped, waived)
            return Requirement(need, waived, budget.terms).cost

        # Every other waiver that always holds stays let off; this one's are tried one by one.
        others_waived = always_waived - set(waiver.buildings)
        others_dropped = always_dropped - set(waiver.purchases)
        baseline = full_cost(others_dropped, others_waived)
        standing = [
            building for building in waiver.buildings
                if full_cost(others_dropped, others_waived | {building}) != baseline
        ]
        spared = [
            purchase for purchase in waiver.purchases
                if full_cost(others_dropped | {purchase}, others_waived) != baseline
        ]

        let_off = []
        if standing:
            names = ", ".join(building.location_name.removeprefix("Build ") for building in standing)
            let_off.append(f"{names} standing")
        if spared:
            names = ", ".join(purchase.location_name.removeprefix("Own ") for purchase in spared)
            let_off.append(f"{names} spared")
        return ", ".join(let_off)

    @staticmethod
    def _row_name(entry: PricedBudgetItem) -> str:
        """The entry's name as a row reads it: a unit is trained, not owned."""
        name = entry.location.location_name
        if name.startswith("Own "):
            return "Train " + name.removeprefix("Own ")
        return name

    def _own_price(self, entry: PricedBudgetItem) -> Cost:
        """What the entry costs for itself, with nothing it needs first. The base is what it is
        made of: its villagers' food, a Town Center and, where the civilisation needs one, a
        House. The villager is priced as the budget charges it, at the food that staffs a base,
        not at one villager's 50."""
        if entry.location is BASE:
            return Need.as_cost(self.requirement([entry]).cost)
        if entry.location is VILLAGER:
            return Need.as_cost(villager_food().own_cost())
        return Need.as_cost(entry.location.cost)

    @staticmethod
    def _cost_text(cost: Cost, easy: Collection[Resource] = ()) -> str:
        """A cost as text, each resource by its initial: 100w, 50g. A resource with an easy
        source is starred, as that source pays it: w*."""
        return ", ".join(
            f"{resource.name[0].lower()}*" if resource in easy
                else f"{amount}{resource.name[0].lower()}"
                for resource, amount in cost
        ) or "free"
