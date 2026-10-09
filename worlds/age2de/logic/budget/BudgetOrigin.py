"""Every early gathering source a budget can count, what it is worth, and each way to work it."""
from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING, Callable

from rule_builder.rules import Rule

from ...items.Items import Resource
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
from .Need import Need
from .UnitBudgetItem import UnitBudgetItem

if TYPE_CHECKING:
    from ...locations.Scenarios import Age2ScenarioData
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
    """One way to work a source: the economy rule that switches it on, less paying for what it
    needs, and what it needs paid for before it brings anything in."""
    rule: Callable[[ScenarioResourceLogic], Rule]
    need: Need

@dataclasses.dataclass(frozen=True, eq=False)
class ResourceOrigin:
    """An early gathering source: what it brings in, and each gather method that can work it."""
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
                lambda economy: economy.can_fish_by_boat(pays_for_need=False),
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
                lambda economy: economy.can_gather_oysters_by_boat(pays_for_need=False),
                _BOATS,
            ),
        ],
    ),
    ResourceOrigin(
        "whales",
        Resource.GOLD,
        [GatheringMethod(lambda economy: economy.can_hunt_whales(pays_for_need=False), _BOATS)],
    ),
    ResourceOrigin(
        "quarry",
        Resource.STONE,
        [GatheringMethod(lambda economy: economy.can_quarry_some(), Need.one_of(*STONE_DROPSITES))],
    ),
    ResourceOrigin(
        "relics",
        Resource.GOLD,
        [GatheringMethod(lambda economy: economy.can_collect_relics(pays_for_need=False), _MONKS)],
        per_relic=True,
    ),
]
