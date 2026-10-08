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
    """Not a location: the base a scenario works from, given a key so the budget can charge for it
    like one. Its value is outside every location id band."""
    BASE = 1

    @property
    def location_name(self) -> str:
        return "Base"

    @property
    def age(self) -> Age2AgeData:
        return Age2AgeData.DARK


BASE = Age2BaseData.BASE

PricedLocation = Age2AgeData | Age2BuildingData | Age2TechData | Age2UnitData | Age2BaseData
"""A location the budget can price, or the base. Location ids are unique across the game, so one
is its own key whatever its type."""


class BudgetItem:
    """A priced location and what it makes a scenario pay for, as a tree: its own node, and below
    it the techs it cannot be had without, each owning its own price, age and building. Built once
    per location; need_in trims it for one scenario."""

    rank: ClassVar[int]
    """Within an age, an age-up comes before its buildings, and buildings before what is made
    there."""

    location: PricedLocation
    node: Need
    """What it charges for itself: its price, the age it needs, where it is made."""


    first_in_age: ClassVar[bool] = False
    """Whether it goes ahead of the sample's own entries of its age in the scenario's order."""

    def __init__(self, location: PricedLocation) -> None:
        self.location = location

    @property
    def age(self) -> Age2AgeData:
        return self.location.age

    def structural(self, scenario: ScenarioLogic) -> Rule:
        """Its own rule in the scenario, less paying."""
        raise NotImplementedError

    @property
    def children(self) -> list[TechBudgetItem]:
        """The techs directly below it."""
        return []

    def below(self) -> Iterator[TechBudgetItem]:
        """Every tech below it, nearest first."""
        for child in self.children:
            yield child
            yield from child.below()

    def need_in(self, scenario: ScenarioLogic) -> Need:
        """As the scenario pays for it: its own node, and every tech below it the scenario does not
        have for itself. A tech let off takes its building and age with it."""
        return sum((tech.node for tech in self.below() if tech.charged_in(scenario)), self.node)

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.location.name})"
