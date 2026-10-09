"""A tech: researching it, and the prerequisite chain below it."""
from __future__ import annotations

import functools
from typing import TYPE_CHECKING

from rule_builder.rules import Rule

from ...locations.Techs import Age2TechData
from .BudgetItem import BudgetItem
from .Need import Need

if TYPE_CHECKING:
    from ...generation.Age2Pool import Age2Pool
    from ..ScenarioLogic import ScenarioLogic


class TechBudgetItem(BudgetItem):
    """Its price, its age and the buildings it is researched at; below it, its prerequisite.

    Asked for itself it is always charged. Below another item it is let off where the scenario
    cannot research it or researched it for itself."""

    rank = 2
    location: Age2TechData

    def scenario_rule(self, scenario: ScenarioLogic) -> Rule:
        return scenario.techs.can_research_structurally(self.location)

    def is_location(self, pool: Age2Pool) -> bool:
        return self.location in pool.techs.shuffled

    @functools.cached_property
    def node(self) -> Need:
        tech = self.location
        return (
            Need.pay(tech, tech.cost)
            + Need.reach(tech.age)
            + Need.one_of(*tech.buildings)
        )

    @functools.cached_property
    def children(self) -> list[TechBudgetItem]:
        prerequisite = self.location.prerequisite
        return [TechBudgetItem(prerequisite)] if prerequisite is not None else []

    def charged_in(self, scenario: ScenarioLogic) -> bool:
        """Whether a scenario pays for it below another item."""
        return (
            scenario.civilization.researches(self.location)
            and not scenario.techs.researched_at_start(self.location)
        )
