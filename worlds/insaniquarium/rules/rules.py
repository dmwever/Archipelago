from __future__ import annotations

from typing import TYPE_CHECKING

from ..items.items import VICTORY_ITEM_NAME
from ..locations.locations import InsaniquariumLocationData, VICTORY_LOCATION_NAME
from ..logic.logic import InsaniquariumLogic

if TYPE_CHECKING:
    from .. import InsaniquariumWorld


class InsaniquariumRules:
    """Applies logic from logic/ to this world's locations and completion condition."""

    def __init__(self, world: InsaniquariumWorld) -> None:
        self.world = world
        self.logic = InsaniquariumLogic(world)

    def set_rules(self) -> None:
        world = self.world
        world.set_rule(world.get_location(InsaniquariumLocationData.MOCK_LOCATION.location_name),
                       self.logic.can_reach_mock_location())
        world.set_rule(world.get_location(VICTORY_LOCATION_NAME), self.logic.can_win())
        world.set_completion_rule(self.logic.has(VICTORY_ITEM_NAME))
