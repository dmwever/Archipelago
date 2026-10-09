"""A unit location: training one."""
from __future__ import annotations

import functools
from typing import TYPE_CHECKING

from rule_builder.rules import Rule

from ...locations.Units import Age2UnitData
from .BudgetItem import BudgetItem
from .Need import Need
from .TechBudgetItem import TechBudgetItem
from ...locations.connections.UnitBuildings import logic_buildings

if TYPE_CHECKING:
    from ..ScenarioLogic import ScenarioLogic

class UnitBudgetItem(BudgetItem):
    """One unit of its line - every tier costs the same, so units of one line share it - where it
    is trained and its age; below it, the upgrade techs that make this tier."""

    rank = 3
    location: Age2UnitData

    def scenario_rule(self, scenario: ScenarioLogic) -> Rule:
        return scenario.units.can_train_structurally(self.location)

    @functools.cached_property
    def node(self) -> Need:
        unit = self.location
        return (
            Need.pay(unit.line, unit.cost)
            + Need.reach(unit.age)
            + Need.one_of(*logic_buildings(unit))
        )

    @functools.cached_property
    def children(self) -> list[TechBudgetItem]:
        upgrade = self.location.upgrade_tech
        return [TechBudgetItem(upgrade)] if upgrade is not None else []
