"""The one villager entry, whichever villager location."""
from __future__ import annotations

import functools

from ...items.Items import Age2ItemData
from .Need import Need
from .TechBudgetItem import TechBudgetItem
from .UnitBudgetItem import UnitBudgetItem

class VillagerBudgetItem(UnitBudgetItem):
    """Male, female and every profession are the same unit: one villager, priced at the food that
    staffs a base rather than the unit's own cost. Nothing upgrades it."""

    @staticmethod
    def villager_food() -> Need:
        """One villager, priced at the food that staffs a base. The villager entry and the base
        both ask it under one identity, so a scenario pays it once."""
        food = Age2ItemData.STARTING_VILLAGER_FOOD.type
        return Need.pay("villager", {food.type: food.amount})

    @property
    def children(self) -> list[TechBudgetItem]:
        return []

    @functools.cached_property
    def node(self) -> Need:
        villager = self.location
        return (
            self.villager_food()
            + Need.reach(villager.age)
            + Need.one_of(*villager.buildings)
        )
