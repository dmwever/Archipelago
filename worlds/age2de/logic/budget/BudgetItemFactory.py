"""The one BudgetItem per priced location."""
from __future__ import annotations

import functools
from typing import ClassVar

from ...generation.pools.BudgetPool import VILLAGER
from ...locations.Ages import Age2AgeData
from ...locations.Buildings import Age2BuildingData
from ...locations.Techs import Age2TechData
from ...locations.Units import Age2UnitData
from .AgeBudgetItem import AgeBudgetItem
from .BaseBudgetItem import BaseBudgetItem
from .BudgetItem import Age2BaseData, BudgetItem, PricedLocation
from .BuildingBudgetItem import BuildingBudgetItem
from .TechBudgetItem import TechBudgetItem
from .UnitBudgetItem import UnitBudgetItem
from .VillagerBudgetItem import VillagerBudgetItem

class BudgetItemFactory:
    """Makes the BudgetItem for a priced location, by the kind of location it is. Each is made
    once and shared: an item is the same in every scenario, so its tree is built only once."""

    _ITEMS: ClassVar[dict[type, type[BudgetItem]]] = {
        Age2AgeData: AgeBudgetItem,
        Age2BuildingData: BuildingBudgetItem,
        Age2TechData: TechBudgetItem,
        Age2UnitData: UnitBudgetItem,
        Age2BaseData: BaseBudgetItem,
    }

    @staticmethod
    @functools.cache
    def for_location(location: PricedLocation) -> BudgetItem:
        if location is VILLAGER:
            return VillagerBudgetItem(location)   # every villager location is the one villager
        return BudgetItemFactory._ITEMS[type(location)](location)
