"""From what a player typed to the location it means, and the data behind it."""
from __future__ import annotations

from typing import TYPE_CHECKING

from Utils import get_intended_text

from ..locations.Ages import Age2AgeData
from ..locations.Buildings import Age2BuildingData
from ..locations.Techs import Age2TechData
from ..locations.UnitLocations import UNIT_LOCATION_TYPES, UnitLocation

if TYPE_CHECKING:
    from .. import Age2World

type Explained = UnitLocation | Age2BuildingData | Age2TechData | Age2AgeData

_BY_NAME: dict[str, Explained] = {
    data.location_name: data
        for kind in (*UNIT_LOCATION_TYPES, Age2BuildingData, Age2TechData, Age2AgeData)
            for data in kind
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
