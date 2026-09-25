from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .. import InsaniquariumWorld

# Keys the WinFish client reads from slot_data.
WORLD_VERSION = "world_version"


def build(world: InsaniquariumWorld) -> dict[str, Any]:
    return {
        WORLD_VERSION: world.world_version.as_simple_string(),
    }
