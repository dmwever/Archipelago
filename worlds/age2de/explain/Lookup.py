"""From what a player typed to the location it means, and the data behind it."""
from __future__ import annotations

from typing import TYPE_CHECKING

from Utils import get_intended_text

from ..locations.Ages import Age2AgeData
from ..locations.Buildings import Age2BuildingData
from ..locations.Locations import Age2ScenarioLocationData
from ..locations.Techs import Age2TechData
from ..locations.UnitLocations import UNIT_LOCATION_TYPES, UnitLocation

if TYPE_CHECKING:
    from .. import Age2World

type Explained = UnitLocation | Age2BuildingData | Age2TechData | Age2AgeData | Age2ScenarioLocationData

_BY_NAME: dict[str, Explained] = {
    **{data.location_name: data
        for kind in (*UNIT_LOCATION_TYPES, Age2BuildingData, Age2TechData, Age2AgeData)
            for data in kind},
    **{objective.global_name(): objective for objective in Age2ScenarioLocationData},
}
"""Every location an explanation knows how to describe, by its location name."""


def find(world: Age2World, typed: str) -> tuple[str, Explained] | None:
    """The location the player meant and its data, or None for a name this seed doesn't have or
    an explanation doesn't cover - UT then falls back to its own."""
    names = [location.name for location in world.multiworld.get_locations(world.player)
             if location.address is not None and location.name in _BY_NAME]
    name, usable, _ = get_intended_text(typed, names)
    if not usable:
        return None
    return name, _BY_NAME[name]


def find_objective(world: Age2World, scenario, typed: str) -> tuple[str, Age2ScenarioLocationData] | None:
    """One of the scenario's own locations, typed without the scenario: "Victory". Exact, so a
    unit or building typed after a scenario is never taken for one."""
    wanted = f"{scenario.scenario_name}: {typed.strip()}".lower()
    for location in world.multiworld.get_locations(world.player):
        if location.address is not None and location.name.lower() == wanted:
            return location.name, _BY_NAME[location.name]
    return None
