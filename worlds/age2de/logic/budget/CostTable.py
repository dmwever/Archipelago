"""What one location's running total costs under each combination of waivers, and the switches
that pick between them at runtime."""
from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING

from BaseClasses import CollectionState
from rule_builder.rules import Rule

from ...items.Items import Resource
from ...locations.Buildings import Age2BuildingData
from ..custom_logic.ScenarioQuestions import ScenarioCostWaived
from .BudgetItem import PricedLocation
from .GatherMethodPurchases import GatherMethodPurchase
from .Need import Cost, Need, as_cost
from .Requirement import Requirement
from .ScenarioResourceOrigins import ScenarioResourceOrigin, ScenarioResourceOrigins

if TYPE_CHECKING:
    from .BudgetOrder import BudgetOrder

@dataclasses.dataclass(frozen=True, eq=False)
class RunningTotal:
    """The running total under one combination of waivers: the buildings they waive, what it
    needs, what that costs, and what each dropsite choice's gather method would buy on top."""
    waived: frozenset[Age2BuildingData]
    need: Need
    cost: Cost
    gather_method_purchases: tuple[tuple[GatherMethodPurchase, ...], ...]

@dataclasses.dataclass(frozen=True, eq=False)
class CostTable:
    waivers: tuple[ScenarioCostWaived.Resolved, ...]
    """One per bit of the mask."""
    totals_by_mask: tuple[RunningTotal, ...]
    """The running total under each combination of waivers, indexed by mask."""
    resource_origins: ScenarioResourceOrigins

    @classmethod
    def for_location(cls, order: BudgetOrder, location: PricedLocation) -> CostTable | None:
        """The table for a location in the order, or None if it is not in the order."""
        if order.running_total_for(location) is None:
            return None

        budget = order.scenario.budget
        waivers = tuple(budget.cost_waivers)

        def on(mask: int) -> list[ScenarioCostWaived.Resolved]:
            """The waivers this combination holds: one bit per waiver."""
            return [waiver for bit, waiver in enumerate(waivers) if mask >> bit & 1]

        totals_by_mask: list[RunningTotal] = []
        for mask in range(1 << len(waivers)):
            waived = budget.always_standing | frozenset(
                building for waiver in on(mask)
                    for building in waiver.buildings
            )
            dropped = budget.always_spared | frozenset(
                purchase for waiver in on(mask)
                    for purchase in waiver.purchases
            )
            need = order.running_total_for(location, dropped)
            requirement = Requirement(need, waived)
            purchases = order.resource_origins.gather_method_purchases(
                need,
                requirement,
                waived,
            )
            totals_by_mask.append(
                RunningTotal(
                    waived,
                    need,
                    as_cost(requirement.cost),
                    purchases,
                )
            )

        return cls(waivers, tuple(totals_by_mask), order.resource_origins)

    @property
    def rules(self) -> tuple[Rule.Resolved, ...]:
        """Every rule the table switches on: the waivers, then every gather method's."""
        return (*self.waivers, *self.resource_origins.rules)

    def mask(self, state: CollectionState) -> int:
        """Which waivers hold: one bit each."""
        return sum(
            1 << bit for bit, waiver in enumerate(self.waivers)
                if waiver(state)
        )

    def waivers_holding(self, state: CollectionState | None) -> list[ScenarioCostWaived.Resolved]:
        """The waivers that hold - none, when there is no state."""
        if state is None:
            return []
        return [waiver for waiver in self.waivers if waiver(state)]

    def total(self, state: CollectionState | None) -> RunningTotal:
        """The running total with the waivers that hold - none, when there is no state."""
        return self.totals_by_mask[0 if state is None else self.mask(state)]

    def usable(self, state: CollectionState) -> list[int]:
        """The dropsite choices whose gather method is switched on."""
        on = [rule(state) for rule in self.resource_origins.rules]
        return [
            index for index, choice in enumerate(self.resource_origins.choices)
                if on[choice.rule]
        ]

    def sources_on(self, state: CollectionState) -> list[ScenarioResourceOrigin]:
        working = self.resource_origins.working(self.usable(state))
        return [
            origin for index, origin in enumerate(self.resource_origins.origins)
                if index in working
        ]

    def allowance(self, state: CollectionState) -> dict[Resource, int]:
        origins = self.resource_origins
        return origins.income(origins.working(self.usable(state)))
