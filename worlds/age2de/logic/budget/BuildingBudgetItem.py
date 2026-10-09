"""A building location: putting one up."""
from __future__ import annotations

import functools
from typing import TYPE_CHECKING

from rule_builder.rules import Rule

from ...locations.Buildings import BUILDING_PREREQUISITE, Age2BuildingData
from .BudgetItem import BudgetItem
from .Need import Need

if TYPE_CHECKING:
    from ...generation.Age2Pool import Age2Pool
    from ..ScenarioLogic import ScenarioLogic


class BuildingBudgetItem(BudgetItem):
    """Itself, always, even where the scenario starts with one standing, and its prerequisite."""

    rank = 1
    location: Age2BuildingData

    def scenario_rule(self, scenario: ScenarioLogic) -> Rule:
        return scenario.buildings.can_build_building(self.location)

    def is_location(self, pool: Age2Pool) -> bool:
        return self.location in pool.buildings.locations

    @functools.cached_property
    def node(self) -> Need:
        building = self.location
        prerequisite = BUILDING_PREREQUISITE.get(building)
        return (
            Need.build(building)
            + Need.reach(building.age)
            + (Need.one_of(prerequisite) if prerequisite is not None else Need())
        )
