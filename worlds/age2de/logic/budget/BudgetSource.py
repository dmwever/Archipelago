"""The early gathering sources a budget counts, and the seed each has to be paid for first."""
from __future__ import annotations

import dataclasses
import itertools
from typing import TYPE_CHECKING, Callable, Iterable, Sequence

from rule_builder.rules import Rule

from ...generation.pools.BudgetPool import SAMPLED_RESOURCES
from ...items.Items import Resource
from ...locations.Ages import Age2AgeData
from ...locations.Buildings import BUILDING_PREREQUISITE, Age2BuildingData
from ...locations.Units import Age2UnitData
from ...locations.connections import ScenarioResources
from ..scenarios.ScenarioBuildingLogic import (
    FISHERMAN_DROPSITES,
    FOOD_DROPSITES,
    GOLD_DROPSITES,
    HUNT_DROPSITES,
    STONE_DROPSITES,
    WOOD_DROPSITES,
)
from .Need import CLIMBED_AGES, Cost, Need, as_cost
from .Requirement import Requirement
from .UnitBudgetItem import UnitBudgetItem

if TYPE_CHECKING:
    from ... import Age2World
    from ...locations.Scenarios import Age2ScenarioData
    from ..ScenarioLogic import ScenarioLogic
    from ..scenarios.ScenarioResourceLogic import ScenarioResourceLogic

# -- what an origin is worth ------------------------------------------------------------------

SOURCE_ALLOWANCE = 250
"""What one early gathering source is worth to a scenario's budget."""
RELIC_ALLOWANCE = 50
"""What each relic a scenario can collect is worth, in gold."""

def relic_allowance(scenario: Age2ScenarioData) -> int:
    return RELIC_ALLOWANCE * ScenarioResources.total(scenario).relic_count

# -- every resource origin --------------------------------------------------------------------

@dataclasses.dataclass(frozen=True, eq=False)
class GatheringMethod:
    """One way to work a source: the economy rule that switches it on, less paying for its seed,
    and the seed itself."""
    rule: Callable[[ScenarioResourceLogic], Rule]
    seed: Need

@dataclasses.dataclass(frozen=True, eq=False)
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
    ResourceOrigin(
        "hunt",
        Resource.FOOD,
        [GatheringMethod(lambda economy: economy.can_hunt(), Need.one_of(*HUNT_DROPSITES))],
    ),
    ResourceOrigin(
        "herd",
        Resource.FOOD,
        [GatheringMethod(lambda economy: economy.can_herd(), Need.one_of(*FOOD_DROPSITES))],
    ),
    ResourceOrigin(
        "forage",
        Resource.FOOD,
        [GatheringMethod(lambda economy: economy.can_forage(), Need.one_of(*FOOD_DROPSITES))],
    ),
    ResourceOrigin(
        "fish",
        Resource.FOOD,
        [
            GatheringMethod(
                lambda economy: economy.can_fish_from_shore(),
                Need.one_of(*FISHERMAN_DROPSITES),
            ),
            GatheringMethod(
                lambda economy: economy.can_fish_by_boat(seeded=False),
                _BOATS,
            ),
        ],
    ),
    ResourceOrigin(
        "chop",
        Resource.WOOD,
        [GatheringMethod(lambda economy: economy.can_chop_some(), Need.one_of(*WOOD_DROPSITES))],
    ),
    ResourceOrigin(
        "mine",
        Resource.GOLD,
        [GatheringMethod(lambda economy: economy.can_mine_some(), Need.one_of(*GOLD_DROPSITES))],
    ),
    ResourceOrigin(
        "oysters",
        Resource.GOLD,
        [
            GatheringMethod(
                lambda economy: economy.can_gather_oysters_from_shore(),
                Need.one_of(*FISHERMAN_DROPSITES),
            ),
            GatheringMethod(
                lambda economy: economy.can_gather_oysters_by_boat(seeded=False),
                _BOATS,
            ),
        ],
    ),
    ResourceOrigin(
        "whales",
        Resource.GOLD,
        [GatheringMethod(lambda economy: economy.can_hunt_whales(seeded=False), _BOATS)],
    ),
    ResourceOrigin(
        "quarry",
        Resource.STONE,
        [GatheringMethod(lambda economy: economy.can_quarry_some(), Need.one_of(*STONE_DROPSITES))],
    ),
    ResourceOrigin(
        "relics",
        Resource.GOLD,
        [GatheringMethod(lambda economy: economy.can_collect_relics(seeded=False), _MONKS)],
        per_relic=True,
    ),
]

# -- seeds ------------------------------------------------------------------------------------

@dataclasses.dataclass(frozen=True, eq=False)
class Part:
    """One thing a seed buys: a building, a unit, the age-ups. Charged once however many seeds
    want it. `in_requirement` parts are bought for the location anyway; a seed only has to have
    them paid for before its source produces."""
    identity: object
    cost: Cost
    in_requirement: bool

def dropsite_choices(seed: Need) -> list[tuple[Age2BuildingData, ...]]:
    """Each way to put the seed's buildings up: one pick from each of its building choices."""
    groups = sorted(seed.building_choices, key=lambda group: tuple(map(int, group)))
    return list(itertools.product(*groups))

def seed_parts(
    seed: Need,
    picks: Sequence[Age2BuildingData],
    need: Need,
    requirement: Requirement,
    waived: frozenset[Age2BuildingData],
    start: Age2AgeData,
) -> tuple[Part, ...]:
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
            parts.append(
                Part(("building", building), as_cost(building.cost), building in in_total)
            )
            building = BUILDING_PREREQUISITE.get(building)

    for age in CLIMBED_AGES:
        if start < age <= seed.needed_age:
            parts.append(Part(("age", age), as_cost(age.cost), age in requirement.ages))

    return tuple(parts)   # kept in a resolved rule, which has to hash

# -- one scenario's origins -------------------------------------------------------------------

@dataclasses.dataclass(frozen=True, eq=False)
class ResolvedGatherMethod:
    """One way to work a source in one scenario: its rule, already resolved, and its seed."""
    rule: Rule.Resolved
    seed: Need

@dataclasses.dataclass(frozen=True, eq=False)
class ScenarioResourceOrigin:
    """A resource origin as one scenario could work it: what it brings in there, and each gather
    method it could use - the method's rule, already resolved, and its seed."""
    origin: ResourceOrigin
    allowance: int
    gather_methods: tuple[ResolvedGatherMethod, ...]

    @property
    def name(self) -> str:
        return self.origin.name

    @property
    def resource(self) -> Resource:
        return self.origin.resource

@dataclasses.dataclass(frozen=True, eq=False)
class DropsiteChoice:
    """One gather method with one pick of dropsite, by index: its origin, and the method's rule
    among ScenarioResourceOrigins.rules; then its seed, and the buildings picked."""
    source: int
    rule: int
    seed: Need
    site: tuple[Age2BuildingData, ...]

@dataclasses.dataclass(frozen=True, eq=False)
class Bootstrap:
    """What paid for a total: the choices brought in, and what their seeds added to it."""
    choices: frozenset[int]
    seeds_added: dict[Resource, int]

@dataclasses.dataclass(frozen=True, eq=False)
class ScenarioResourceOrigins:
    """Every resource origin one scenario could bring in, each gather method it could use there,
    and each pick of dropsite for those. Frozen and tupled throughout: a resolved budget total
    keeps it, and it has to hash. It hashes by identity: there is one per scenario, shared by
    every budget total there, and hashing its contents for each would be slow. It keeps the
    scenario's start age, not its ScenarioPriceLogic: a resolved rule outlives its world, and
    holding the price logic would hold the world with it."""
    start_age: Age2AgeData
    origins: tuple[ScenarioResourceOrigin, ...]
    choices: tuple[DropsiteChoice, ...]
    """Each gather method once per pick of dropsite: what the search brings in, one at a time."""

    @classmethod
    def from_scenario(
        cls,
        scenario: ScenarioLogic,
        world: Age2World,
    ) -> ScenarioResourceOrigins:
        relic_sum = relic_allowance(scenario.scenario)
        origins: list[ScenarioResourceOrigin] = []

        for origin in RESOURCE_ORIGINS:
            methods: list[ResolvedGatherMethod] = []
            for method in origin.gather_methods:
                resolved = method.rule(scenario.economy).resolve(world)
                if not resolved.always_false:
                    methods.append(
                        ResolvedGatherMethod(resolved, scenario.prices.settle(method.seed))
                    )

            allowance = relic_sum if origin.per_relic else SOURCE_ALLOWANCE
            if methods and allowance:
                origins.append(
                    ScenarioResourceOrigin(origin, allowance, tuple(methods))
                )

        choices: list[DropsiteChoice] = []
        rule_index = 0   # where the method's rule sits in rules
        for index, origin in enumerate(origins):
            for method in origin.gather_methods:
                choices += [
                    DropsiteChoice(index, rule_index, method.seed, site)
                        for site in dropsite_choices(method.seed)
                ]
                rule_index += 1

        return cls(scenario.prices.start_age, tuple(origins), tuple(choices))

    @property
    def rules(self) -> list[Rule.Resolved]:
        """Every gather method's rule, flat, in the order DropsiteChoice.rule counts them."""
        return [
            method.rule for origin in self.origins
                for method in origin.gather_methods
        ]

    @property
    def every_choice(self) -> list[int]:
        return list(range(len(self.choices)))

    def working(self, usable: Iterable[int]) -> set[int]:
        """The origins these choices bring in."""
        return {self.choices[choice].source for choice in usable}

    def income(self, working: Iterable[int]) -> dict[Resource, int]:
        """What the origins at these indices bring in, per resource."""
        total = dict.fromkeys(SAMPLED_RESOURCES, 0)
        for index in working:
            origin = self.origins[index]
            total[origin.resource] += origin.allowance
        return total

    def allowance(self) -> dict[Resource, int]:
        """What every origin together brings in."""
        return self.income(range(len(self.origins)))

    def seed_parts(
        self,
        need: Need,
        requirement: Requirement,
        waived: frozenset[Age2BuildingData],
    ) -> tuple[tuple[Part, ...], ...]:
        """What each choice's seed buys, against this running total."""
        return tuple(
            seed_parts(choice.seed, choice.site, need, requirement, waived, self.start_age)
                for choice in self.choices
        )

    def can_cover(
        self,
        pile: dict[Resource, int],
        need: dict[Resource, int],
        usable: list[int],
        parts: Sequence[tuple[Part, ...]],
    ) -> bool:
        """Whether the pile, and the origins it can bring in, cover the need."""
        if all(pile[resource] >= amount for resource, amount in need.items()):
            return True

        most = self.income(self.working(usable))
        if any(pile[resource] + most[resource] < amount for resource, amount in need.items()):
            return False   # seeds only ever add to the total

        return self.bootstrap(pile, need, usable, parts) is not None

    def bootstrap(
        self,
        pile: dict[Resource, int],
        need: dict[Resource, int],
        usable: list[int],
        parts: Sequence[tuple[Part, ...]],
    ) -> Bootstrap | None:
        """Bring origins in one at a time, each once its seed is paid for out of the pile and
        what the origins already working bring in, trying every order. The first set that covers
        the need and its own seeds is the answer. A set's funds do not depend on the order it was
        reached in, so each set is looked at once."""
        most = self.income(self.working(usable))
        stack: list[frozenset[int]] = [frozenset()]
        seen: set[frozenset[int]] = set()

        while stack:
            chosen = stack.pop()
            if chosen in seen:
                continue
            seen.add(chosen)

            funded: dict[object, Part] = {}
            for choice in chosen:
                for part in parts[choice]:
                    funded[part.identity] = part

            spent = dict.fromkeys(SAMPLED_RESOURCES, 0)
            extra = dict.fromkeys(SAMPLED_RESOURCES, 0)
            for part in funded.values():
                for resource, amount in part.cost:
                    spent[resource] += amount
                    if not part.in_requirement:
                        extra[resource] += amount

            working = self.working(chosen)
            income_now = self.income(working)
            if all(
                pile[resource] + income_now[resource] >= need.get(resource, 0) + extra[resource]
                    for resource in SAMPLED_RESOURCES
            ):
                return Bootstrap(chosen, extra)
            if any(
                pile[resource] + most[resource] < need.get(resource, 0) + extra[resource]
                    for resource in SAMPLED_RESOURCES
            ):
                continue   # not even every source switched on could cover what this set bought

            for choice in usable:
                if self.choices[choice].source in working:
                    continue
                cost = dict.fromkeys(SAMPLED_RESOURCES, 0)
                for part in parts[choice]:
                    if part.identity not in funded:
                        for resource, amount in part.cost:
                            cost[resource] += amount
                if all(
                    pile[resource] + income_now[resource] - spent[resource] >= cost[resource]
                        for resource in SAMPLED_RESOURCES
                ):
                    stack.append(chosen | {choice})

        return None
