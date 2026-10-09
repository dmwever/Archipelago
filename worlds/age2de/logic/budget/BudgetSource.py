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


class GatheringMethod(NamedTuple):
    """One way to work a source: the economy rule that switches it on, less paying for its seed,
    and the seed itself."""
    rule: Callable[[ScenarioResourceLogic], Rule]
    seed: Need


@dataclasses.dataclass(frozen=True)
class ResourceOrigin:
    """An early gathering source: what it brings in, and each way to work it - the rule that
    switches the way on, less paying for its seed, and the seed itself."""
    name: str
    resource: Resource
    gather_methods: list[GatheringMethod]
    per_relic: bool = False
    """Worth 50 gold a relic rather than the flat 250."""


_BOATS = UnitBudgetItem(Age2UnitData.FISHING_SHIP).node     # a Dock, and a Fishing Ship to crew
_MONKS = UnitBudgetItem(Age2UnitData.MONK).node              # a Monastery, a Monk, the Castle Age

RESOURCE_ORIGINS: list[ResourceOrigin] = [
    ResourceOrigin("hunt", Resource.FOOD,
                [GatheringMethod(lambda economy: economy.can_hunt(), Need.one_of(*HUNT_DROPSITES))]),
    ResourceOrigin("herd", Resource.FOOD,
                [GatheringMethod(lambda economy: economy.can_herd(), Need.one_of(*FOOD_DROPSITES))]),
    ResourceOrigin("forage", Resource.FOOD,
                [GatheringMethod(lambda economy: economy.can_forage(), Need.one_of(*FOOD_DROPSITES))]),
    ResourceOrigin("fish", Resource.FOOD,
                [
                    GatheringMethod(lambda economy: economy.can_fish_from_shore(), Need.one_of(*FISHERMAN_DROPSITES)),
                    GatheringMethod(lambda economy: economy.can_fish_by_boat(seeded=False), _BOATS)
                ]),
    ResourceOrigin("chop", Resource.WOOD,
                [GatheringMethod(lambda economy: economy.can_chop_some(), Need.one_of(*WOOD_DROPSITES))]),
    ResourceOrigin("mine", Resource.GOLD,
                [GatheringMethod(lambda economy: economy.can_mine_some(), Need.one_of(*GOLD_DROPSITES))]),
    ResourceOrigin("oysters", Resource.GOLD,
                [
                    GatheringMethod(lambda economy: economy.can_gather_oysters_from_shore(), Need.one_of(*FISHERMAN_DROPSITES)),
                    GatheringMethod(lambda economy: economy.can_gather_oysters_by_boat(seeded=False), _BOATS)
                ]),
    ResourceOrigin("whales", Resource.GOLD,
                [GatheringMethod(lambda economy: economy.can_hunt_whales(seeded=False), _BOATS)]),
    ResourceOrigin("quarry", Resource.STONE,
                [GatheringMethod(lambda economy: economy.can_quarry_some(), Need.one_of(*STONE_DROPSITES))]),
    ResourceOrigin("relics", Resource.GOLD,
                [GatheringMethod(lambda economy: economy.can_collect_relics(seeded=False), _MONKS)],
                 per_relic=True),
]

def dropsite_chioces(seed: Need) -> list[list[Age2BuildingData]]:
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
    owned = {price.identity for price in need.own_price}
    parts: list[Part] = []
    for price in sorted(seed.own_price, key=lambda price: str(price.identity)):
        parts.append(Part(("own", price.identity), price.cost, price.identity in owned))
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


class ResolvedGatherMethod(NamedTuple):
    """One way to work a source in one scenario: its rule, already resolved, and its seed."""
    rule: Rule.Resolved
    seed: Need


class ScenarioOrigin(NamedTuple):
    """A gathering source as one scenario could work it: what it brings in, and each way to work
    it - the way's rule, already resolved, and the seed it buys. Tuples throughout: a resolved
    budget total keeps these, and it has to hash."""
    name: str
    resource: Resource
    allowance: int
    gather_methods: tuple[ResolvedGatherMethod, ...]


class GatherMethodChoice(NamedTuple):
    """A DropsiteChoice cut to what a resolved budget total needs, by index: its origin, and the
    child rule that switches its gather method on. A tuple, as the resolved total hashes."""
    source: int
    rule: int


class Bootstrap(NamedTuple):
    """What paid for a total: the ways brought in, and what their seeds added to it."""
    ways: frozenset[int]
    seeds_added: dict[Resource, int]


def income(working: Iterable[int], origins: Sequence[ScenarioOrigin]) -> dict[Resource, int]:
    """What the origins at these indices bring in, per resource."""
    total = dict.fromkeys(SAMPLED_RESOURCES, 0)
    for index in working:
        origin = origins[index]
        total[origin.resource] += origin.allowance
    return total


def pays(pile: dict[Resource, int], need: dict[Resource, int], usable: list[int],
         choices: Sequence[GatherMethodChoice], parts: Sequence[tuple[Part, ...]], origins: Sequence[ScenarioOrigin]) -> bool:
    """Whether the pile, and the origins it can bring in, cover the need."""
    if all(pile[resource] >= amount for resource, amount in need.items()):
        return True
    most = income({choices[way].source for way in usable}, origins)
    if any(pile[resource] + most[resource] < amount for resource, amount in need.items()):
        return False   # seeds only ever add to the total
    return bootstrap(pile, need, usable, choices, parts, origins) is not None


def bootstrap(pile: dict[Resource, int], need: dict[Resource, int], usable: list[int],
              choices: Sequence[GatherMethodChoice], parts: Sequence[tuple[Part, ...]],
              origins: Sequence[ScenarioOrigin]) -> Bootstrap | None:
    """Bring origins in one at a time, each once its seed is paid for out of the pile and what
    the origins already working bring in, trying every order. The first set that covers the need
    and its own seeds is the answer. A set's funds do not depend on the order it was reached in,
    so each set is looked at once."""
    most = income({choices[way].source for way in usable}, origins)
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
        working = {choices[way].source for way in chosen}
        income_now = income(working, origins)
        if all(pile[resource] + income_now[resource] >= need.get(resource, 0) + extra[resource]
               for resource in SAMPLED_RESOURCES):
            return Bootstrap(chosen, extra)
        if any(pile[resource] + most[resource] < need.get(resource, 0) + extra[resource]
               for resource in SAMPLED_RESOURCES):
            continue   # not even every source switched on could cover what this set bought
        for way in usable:
            if choices[way].source in working:
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
