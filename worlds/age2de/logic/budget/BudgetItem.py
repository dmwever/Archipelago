"""One priced location as the budget sees it, the same in every scenario."""
from __future__ import annotations

import enum

from typing import TYPE_CHECKING, ClassVar, Iterator

from rule_builder.rules import Rule

from ...locations.Ages import Age2AgeData
from ...locations.Buildings import Age2BuildingData
from ...locations.Techs import Age2TechData
from ...locations.Units import Age2UnitData
from .Need import Need

if TYPE_CHECKING:
    from ..ScenarioLogic import ScenarioLogic
    from .TechBudgetItem import TechBudgetItem


class Age2BaseData(enum.IntEnum):
    BASE = 1

    @property
    def location_name(self) -> str:
        return "Base"

    @property
    def age(self) -> Age2AgeData:
        return Age2AgeData.DARK


BASE = Age2BaseData.BASE

PricedLocation = Age2AgeData | Age2BuildingData | Age2TechData | Age2UnitData | Age2BaseData

class BudgetItem:
    rank: ClassVar[int]
    """Within an age, an age-up comes before its buildings, and buildings before what is made
    there."""
    location: PricedLocation
    node: Need
    first_in_age: ClassVar[bool] = False

    def __init__(self, location: PricedLocation) -> None:
        self.location = location

    @property
    def age(self) -> Age2AgeData:
        return self.location.age

    def scenario_rule(self, scenario: ScenarioLogic) -> Rule:
        """Its own rule in the scenario, less paying."""
        raise NotImplementedError

    @property
    def children(self) -> list[TechBudgetItem]:
        """The techs directly below it."""
        return []

    def prerequisite_techs(self) -> Iterator[TechBudgetItem]:
        """Every tech below it, nearest first."""
        for child in self.children:
            yield child
            yield from child.prerequisite_techs()

    def need_in(self, scenario: ScenarioLogic) -> Need:
        """As the scenario pays for it: its own node, and every tech below it the scenario does not
        have for itself. A tech let off takes its building and age with it."""
        return sum((tech.node for tech in self.prerequisite_techs() if tech.charged_in(scenario)), self.node)

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.location.name})"
