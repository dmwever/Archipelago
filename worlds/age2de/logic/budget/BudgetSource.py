"""The early gathering sources a budget counts, and the seed each has to be paid for first."""
from __future__ import annotations

import dataclasses
import itertools
from typing import TYPE_CHECKING, Callable, NamedTuple

from rule_builder.rules import Rule

from ...items.Items import Resource
from ...locations.Ages import Age2AgeData
from ...locations.Buildings import BUILDING_PREREQUISITE, Age2BuildingData
from ...locations.Units import Age2UnitData
from ..scenarios.ScenarioBuildingLogic import (FISHERMAN_DROPSITES, FOOD_DROPSITES,
                                               GOLD_DROPSITES, HUNT_DROPSITES, STONE_DROPSITES,
                                               WOOD_DROPSITES)
from .Need import CLIMBED_AGES, Need
from .Requirement import Requirement
from .UnitBudgetItem import UnitBudgetItem

if TYPE_CHECKING:
    from ..scenarios.ScenarioResourceLogic import ScenarioResourceLogic


Cost = tuple[tuple[Resource, int], ...]


class Part(NamedTuple):
    """One thing a seed buys: a building, a unit, the age-ups. Charged once however many seeds
    want it. `in_requirement` parts are bought for the location anyway; a seed only has to have
    them paid for before its source produces."""
    identity: object
    cost: Cost
    in_requirement: bool


@dataclasses.dataclass(frozen=True)
class BudgetSource:
    """An early gathering source: what it brings in, and each way to work it - the rule that
    switches the way on, less paying for its seed, and the seed itself."""
    name: str
    resource: Resource
    ways: tuple[tuple[Callable[[ScenarioResourceLogic], Rule], Need], ...]
    per_relic: bool = False
    """Worth 50 gold a relic rather than the flat 250."""


def _dropsite(options: tuple[Age2BuildingData, ...]) -> Need:
    return Need.one_of(options)


_BOATS = UnitBudgetItem(Age2UnitData.FISHING_SHIP).node     # a Dock, and a Fishing Ship to crew
_MONKS = UnitBudgetItem(Age2UnitData.MONK).node              # a Monastery, a Monk, the Castle Age

SOURCES: tuple[BudgetSource, ...] = (
    BudgetSource("hunt", Resource.FOOD, ((lambda economy: economy.can_hunt(),
                                          _dropsite(HUNT_DROPSITES)),)),
    BudgetSource("herd", Resource.FOOD, ((lambda economy: economy.can_herd(),
                                          _dropsite(FOOD_DROPSITES)),)),
    BudgetSource("forage", Resource.FOOD, ((lambda economy: economy.can_forage(),
                                            _dropsite(FOOD_DROPSITES)),)),
    BudgetSource("fish", Resource.FOOD, (
        (lambda economy: economy.can_fish_from_shore(), _dropsite(FISHERMAN_DROPSITES)),
        (lambda economy: economy.can_fish_by_boat(seeded=False), _BOATS))),
    BudgetSource("chop", Resource.WOOD, ((lambda economy: economy.can_chop_some(),
                                          _dropsite(WOOD_DROPSITES)),)),
    BudgetSource("mine", Resource.GOLD, ((lambda economy: economy.can_mine_some(),
                                          _dropsite(GOLD_DROPSITES)),)),
    BudgetSource("oysters", Resource.GOLD, (
        (lambda economy: economy.can_gather_oysters_from_shore(), _dropsite(FISHERMAN_DROPSITES)),
        (lambda economy: economy.can_gather_oysters_by_boat(seeded=False), _BOATS))),
    BudgetSource("whales", Resource.GOLD, ((lambda economy: economy.can_hunt_whales(seeded=False),
                                            _BOATS),)),
    BudgetSource("quarry", Resource.STONE, ((lambda economy: economy.can_quarry_some(),
                                             _dropsite(STONE_DROPSITES)),)),
    BudgetSource("relics", Resource.GOLD,
                 ((lambda economy: economy.can_collect_relics(seeded=False), _MONKS),),
                 per_relic=True),
)
"""Shore and boat take the same fish, and the same oysters, so each is one source with two ways.
Trade is no source here: when it is on it is an easy source of gold and wood outright."""

def options(seed: Need) -> list[tuple[Age2BuildingData, ...]]:
    """Each way to put the seed's buildings up: one pick from each of its groups."""
    groups = sorted(seed.groups, key=lambda group: tuple(map(int, group)))
    return [tuple(pick) for pick in itertools.product(*groups)]


def seed_parts(seed: Need, picks: tuple[Age2BuildingData, ...], need: Need,
               requirement: Requirement, waived: frozenset[Age2BuildingData],
               start: Age2AgeData) -> tuple[Part, ...]:
    """What working a source this way buys, against one location's running total: each
    building picked and its prerequisites up to one standing, the crew, and the age-ups.
    Age-ups past the total's are charged their price alone: the climb buildings and the Town
    Center a later age asks are left to the total that reaches it."""
    in_total = set(requirement.buildings) | set(need.entry_buildings)
    owned = {identity for identity, _ in need.own}
    parts: list[Part] = []
    for identity, priced in sorted(seed.own, key=lambda item: str(item[0])):
        parts.append(Part(("own", identity), priced, identity in owned))
    seen: set[Age2BuildingData] = set()
    for building in picks:
        while building is not None and building not in waived and building not in seen:
            seen.add(building)
            parts.append(Part(("building", building), _cost(building.cost),
                              building in in_total))
            building = BUILDING_PREREQUISITE.get(building)
    for age in CLIMBED_AGES:
        if start < age <= seed.top:
            parts.append(Part(("age", age), _cost(age.cost), age in requirement.ages))
    return tuple(parts)


def _cost(cost: dict[Resource, int]) -> Cost:
    return tuple(sorted(((resource, amount) for resource, amount in cost.items() if amount > 0),
                        key=lambda item: item[0].value))
