"""What a gather method has to buy before it brings anything in, against one running total."""
from __future__ import annotations

import dataclasses
from typing import Sequence

from ...locations.Ages import Age2AgeData
from ...locations.Buildings import BUILDING_PREREQUISITE, Age2BuildingData
from .Need import CLIMBED_AGES, Cost, Need
from .Requirement import Requirement

@dataclasses.dataclass(frozen=True, eq=False)
class GatherMethodPurchase:
    """One thing a gather method buys: a building, a unit, an age-up. Charged once however many
    methods want it. One `already_charged` is bought for the location anyway; the method only has
    to have it paid for before it brings anything in."""
    identity: object
    cost: Cost
    already_charged: bool

    @classmethod
    def for_running_total(
        cls,
        method_need: Need,
        picks: Sequence[Age2BuildingData],
        running_total_need: Need,
        requirement: Requirement,
        waived: frozenset[Age2BuildingData],
        start: Age2AgeData,
    ) -> tuple[GatherMethodPurchase, ...]:
        """What working a source this way buys, against one location's running total: each
        building picked and its prerequisites up to one standing, the crew, and the age-ups.
        Age-ups past the total's are charged their price alone: the climb buildings and the Town
        Center a later age asks are left to the total that reaches it."""
        in_total = set(requirement.buildings) | set(running_total_need.entry_buildings)
        owned = {price.identity for price in running_total_need.own_price}
        purchases: list[GatherMethodPurchase] = []

        for price in sorted(method_need.own_price, key=lambda price: str(price.identity)):
            purchases.append(
                cls(("own", price.identity), price.cost, price.identity in owned)
            )

        seen: set[Age2BuildingData] = set()
        for building in picks:
            while building is not None and building not in waived and building not in seen:
                seen.add(building)
                purchases.append(
                    cls(
                        ("building", building),
                        Need.as_cost(building.cost),
                        building in in_total,
                    )
                )
                building = BUILDING_PREREQUISITE.get(building)

        for age in CLIMBED_AGES:
            if start < age <= method_need.needed_age:
                purchases.append(
                    cls(("age", age), Need.as_cost(age.cost), age in requirement.ages)
                )

        return tuple(purchases)   # kept in a resolved rule, which has to hash
