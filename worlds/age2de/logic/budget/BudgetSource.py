"""The early gathering sources a budget counts, and the seed each has to be paid for first."""
from __future__ import annotations

import dataclasses
import itertools
from typing import TYPE_CHECKING, Callable, Iterable, NamedTuple, Sequence

from rule_builder.rules import Rule

from ...generation.pools.BudgetPool import SAMPLED_RESOURCES
from ...items.Items import Resource
from ...locations.Ages import Age2AgeData
from ...locations.Buildings import BUILDING_PREREQUISITE, Age2BuildingData
from ...locations.Units import Age2UnitData
from ...locations.connections import ScenarioResources
from ..scenarios.ScenarioBuildingLogic import (FISHERMAN_DROPSITES, FOOD_DROPSITES,
                                               GOLD_DROPSITES, HUNT_DROPSITES, STONE_DROPSITES,
                                               WOOD_DROPSITES)
from .Need import CLIMBED_AGES, Need
from .Requirement import Requirement
from .UnitBudgetItem import UnitBudgetItem

if TYPE_CHECKING:
    from ...locations.Scenarios import Age2ScenarioData
    from ..scenarios.ScenarioResourceLogic import ScenarioResourceLogic


SOURCE_ALLOWANCE = 250
"""What one early gathering source is worth to a scenario's budget."""
RELIC_ALLOWANCE = 50
"""What each relic a scenario can collect is worth, in gold."""


def relic_allowance(scenario: Age2ScenarioData) -> int:
    return RELIC_ALLOWANCE * ScenarioResources.total(scenario).relic_count


Cost = tuple[tuple[Resource, int], ...]
"""Tuples, not lists: a part's cost ends up in a resolved rule, and those have to hash."""


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
    ways: list[tuple[Callable[[ScenarioResourceLogic], Rule], Need]]
    per_relic: bool = False
    """Worth 50 gold a relic rather than the flat 250."""


_BOATS = UnitBudgetItem(Age2UnitData.FISHING_SHIP).node     # a Dock, and a Fishing Ship to crew
_MONKS = UnitBudgetItem(Age2UnitData.MONK).node              # a Monastery, a Monk, the Castle Age

SOURCES: list[BudgetSource] = [
    BudgetSource("hunt", Resource.FOOD,
                 [(lambda economy: economy.can_hunt(), Need.one_of(*HUNT_DROPSITES))]),
    BudgetSource("herd", Resource.FOOD,
                 [(lambda economy: economy.can_herd(), Need.one_of(*FOOD_DROPSITES))]),
    BudgetSource("forage", Resource.FOOD,
                 [(lambda economy: economy.can_forage(), Need.one_of(*FOOD_DROPSITES))]),
    BudgetSource("fish", Resource.FOOD,
                 [(lambda economy: economy.can_fish_from_shore(),
                   Need.one_of(*FISHERMAN_DROPSITES)),
                  (lambda economy: economy.can_fish_by_boat(seeded=False), _BOATS)]),
    BudgetSource("chop", Resource.WOOD,
                 [(lambda economy: economy.can_chop_some(), Need.one_of(*WOOD_DROPSITES))]),
    BudgetSource("mine", Resource.GOLD,
                 [(lambda economy: economy.can_mine_some(), Need.one_of(*GOLD_DROPSITES))]),
    BudgetSource("oysters", Resource.GOLD,
                 [(lambda economy: economy.can_gather_oysters_from_shore(),
                   Need.one_of(*FISHERMAN_DROPSITES)),
                  (lambda economy: economy.can_gather_oysters_by_boat(seeded=False), _BOATS)]),
    BudgetSource("whales", Resource.GOLD,
                 [(lambda economy: economy.can_hunt_whales(seeded=False), _BOATS)]),
    BudgetSource("quarry", Resource.STONE,
                 [(lambda economy: economy.can_quarry_some(), Need.one_of(*STONE_DROPSITES))]),
    BudgetSource("relics", Resource.GOLD,
                 [(lambda economy: economy.can_collect_relics(seeded=False), _MONKS)],
                 per_relic=True),
]
"""Shore and boat take the same fish, and the same oysters, so each is one source with two ways.
Trade is no source here: when it is on it is an easy source of gold and wood outright."""

def options(seed: Need) -> list[list[Age2BuildingData]]:
    """Each way to put the seed's buildings up: one pick from each of its groups."""
    groups = sorted(seed.building_choices, key=lambda group: tuple(map(int, group)))
    return [list(pick) for pick in itertools.product(*groups)]


def seed_parts(seed: Need, picks: list[Age2BuildingData], need: Need,
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
        if start < age <= seed.needed_age:
            parts.append(Part(("age", age), _cost(age.cost), age in requirement.ages))
    return tuple(parts)   # kept in a resolved rule, which has to hash


def _cost(cost: dict[Resource, int]) -> Cost:
    return tuple(sorted(((resource, amount) for resource, amount in cost.items() if amount > 0),
                        key=lambda item: item[0].value))


Worth = Sequence[tuple[str, Resource, int]]
"""Each source: its name, what it brings in, and how much."""
Way = tuple[int, int]
"""One way to bring a source in, with one pick of dropsite: its source, and the rule switching it."""
Bootstrap = tuple[frozenset[int], dict[Resource, int]]
"""The ways that paid, and what their seeds added to the total."""


def income(sources: Iterable[int], worth: Worth) -> dict[Resource, int]:
    total = dict.fromkeys(SAMPLED_RESOURCES, 0)
    for index in sources:
        _, resource, amount = worth[index]
        total[resource] += amount
    return total


def pays(pile: dict[Resource, int], need: dict[Resource, int], usable: list[int],
         ways: Sequence[Way], parts: Sequence[tuple[Part, ...]], worth: Worth) -> bool:
    """Whether the pile, and the sources it can bring in, cover the need."""
    if all(pile[resource] >= amount for resource, amount in need.items()):
        return True
    most = income({ways[way][0] for way in usable}, worth)
    if any(pile[resource] + most[resource] < amount for resource, amount in need.items()):
        return False   # seeds only ever add to the total
    return bootstrap(pile, need, usable, ways, parts, worth) is not None


def bootstrap(pile: dict[Resource, int], need: dict[Resource, int], usable: list[int],
              ways: Sequence[Way], parts: Sequence[tuple[Part, ...]],
              worth: Worth) -> Bootstrap | None:
    """Bring sources in one at a time, each once its seed is paid for out of the pile and what
    the sources already working bring in, trying every order. The first set that covers the need
    and its own seeds is the answer. A set's funds do not depend on the order it was reached in,
    so each set is looked at once."""
    most = income({ways[way][0] for way in usable}, worth)
    stack: list[frozenset[int]] = [frozenset()]
    seen: set[frozenset[int]] = set()
    while stack:
        chosen = stack.pop()
        if chosen in seen:
            continue
        seen.add(chosen)
        funded: dict[object, Part] = {}
        for way in chosen:
            for part in parts[way]:
                funded[part.identity] = part
        spent = dict.fromkeys(SAMPLED_RESOURCES, 0)
        extra = dict.fromkeys(SAMPLED_RESOURCES, 0)
        for part in funded.values():
            for resource, amount in part.cost:
                spent[resource] += amount
                if not part.in_requirement:
                    extra[resource] += amount
        working = {ways[way][0] for way in chosen}
        income_now = income(working, worth)
        if all(pile[resource] + income_now[resource] >= need.get(resource, 0) + extra[resource]
               for resource in SAMPLED_RESOURCES):
            return chosen, extra
        if any(pile[resource] + most[resource] < need.get(resource, 0) + extra[resource]
               for resource in SAMPLED_RESOURCES):
            continue   # not even every source switched on could cover what this set bought
        for way in usable:
            if ways[way][0] in working:
                continue
            cost = dict.fromkeys(SAMPLED_RESOURCES, 0)
            for part in parts[way]:
                if part.identity not in funded:
                    for resource, amount in part.cost:
                        cost[resource] += amount
            if all(pile[resource] + income_now[resource] - spent[resource] >= cost[resource]
                   for resource in SAMPLED_RESOURCES):
                stack.append(chosen | {way})
    return None
