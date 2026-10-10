"""One priced location as the budget sees it, the same in every scenario."""
from __future__ import annotations

import dataclasses
import enum
import functools
from typing import TYPE_CHECKING, Callable, Iterator

from rule_builder.rules import Rule

from ...generation.pools.BudgetPool import VILLAGER
from ...items.Items import Age2ItemData
from ...locations.Ages import Age2AgeData
from ...locations.Buildings import BUILDING_PREREQUISITE, Age2BuildingData
from ...locations.Techs import Age2TechData
from ...locations.Units import Age2UnitData
from ...locations.connections.UnitBuildings import logic_buildings
from .Need import Need

if TYPE_CHECKING:
    from ..ScenarioLogic import ScenarioLogic

class Age2BaseData(enum.IntEnum):
    BASE = 1

    @property
    def location_name(self) -> str:
        return "Base"

    @property
    def age(self) -> Age2AgeData:
        return Age2AgeData.DARK

BASE = Age2BaseData.BASE

type PricedLocation = (Age2AgeData | Age2BuildingData | Age2TechData | Age2UnitData | Age2BaseData)

@dataclasses.dataclass(frozen=True, eq=False)
class BudgetItem:
    location: PricedLocation
    age: Age2AgeData
    rank: int
    """Within an age, an age-up comes before its buildings, and buildings before what is made
    there."""
    node: Need
    scenario_rule: Callable[[ScenarioLogic], Rule]
    """Its own rule in the scenario, less paying."""
    techs_below: tuple[Age2TechData, ...] = ()
    """Every tech below it, nearest first: a tech's prerequisites, a unit's upgrade chain."""

    def need_in_scenario(self, scenario: ScenarioLogic) -> Need:
        """As the scenario pays for it: its own node, and every tech below it the scenario does not
        have for itself. A tech let off takes its building and age with it."""
        charged = [
            for_location(tech).node for tech in self.techs_below
                if scenario.civilization.researches(tech)
                    and not scenario.techs.researched_at_start(tech)
        ]
        return sum(charged, self.node)

    def __repr__(self) -> str:
        return f"BudgetItem({self.location.name})"


def villager_food() -> Need:
    """One villager, priced at the food that staffs a base. The villager entry and the base both
    ask it under one identity, so a scenario pays it once."""
    food = Age2ItemData.STARTING_VILLAGER_FOOD.type
    return Need.pay("villager", {food.type: food.amount})


def _chain(tech: Age2TechData | None) -> Iterator[Age2TechData]:
    """A tech and every prerequisite below it, nearest first."""
    while tech is not None:
        yield tech
        tech = tech.prerequisite


@functools.cache
def for_location(location: PricedLocation) -> BudgetItem:
    """The one item for a priced location, by the kind of location it is."""
    if location is VILLAGER:   # every villager location is the one villager; nothing upgrades it
        return BudgetItem(
            location, location.age, 3,
            villager_food() + Need.reach(location.age) + Need.one_of(*location.buildings),
            lambda scenario: scenario.units.can_train_structurally(location),
        )

    match location:
        case Age2AgeData():
            return BudgetItem(
                location, location, 0,
                Need.reach(location),
                lambda scenario: scenario.ages.can_research(location),
            )
        case Age2BaseData():
            # The Huns build no Houses, so their scenarios' trim drops the House group and the base
            # is the villager and a Town Center alone.
            return BudgetItem(
                location, location.age, 0,
                villager_food()
                + Need.one_of(Age2BuildingData.TOWN_CENTER)
                + Need.one_of(Age2BuildingData.HOUSE),
                lambda scenario: scenario.can_have_base(),
            )
        case Age2BuildingData():
            # Itself, always, even where the scenario starts with one standing, and its prerequisite.
            prerequisite = BUILDING_PREREQUISITE.get(location)
            return BudgetItem(
                location, location.age, 1,
                Need.build(location)
                + Need.reach(location.age)
                + (Need.one_of(prerequisite) if prerequisite is not None else Need()),
                lambda scenario: scenario.buildings.can_build_building(location),
            )
        case Age2TechData():
            # Asked for itself it is always charged; below another item it is let off where the
            # scenario cannot research it or researched it for itself.
            return BudgetItem(
                location, location.age, 2,
                Need.pay(location, location.cost)
                + Need.reach(location.age)
                + Need.one_of(*location.buildings),
                lambda scenario: scenario.techs.can_research_structurally(location),
                tuple(_chain(location.prerequisite)),
            )
        case Age2UnitData():
            # One unit of its line - every tier costs the same, so units of one line share it.
            return BudgetItem(
                location, location.age, 3,
                Need.pay(location.line, location.cost)
                + Need.reach(location.age)
                + Need.one_of(*logic_buildings(location)),
                lambda scenario: scenario.units.can_train_structurally(location),
                tuple(_chain(location.upgrade_tech)),
            )
    raise TypeError(f"{location!r} is not a priced location")
