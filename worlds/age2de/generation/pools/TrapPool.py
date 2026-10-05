from __future__ import annotations

from typing import TYPE_CHECKING

from ...items import Items
from ...items.Items import Age2ItemData
from ...Options import TRAP_DEFAULT_WEIGHT

if TYPE_CHECKING:
    from ... import Age2World
    from ...Options import Age2Options


class TrapPool:
    def __init__(self, options: 'Age2Options', world: 'Age2World') -> None:
        self._difficulty = options.trap_difficulty
        self._percentage = options.trap_percentage
        self._distribution = options.trap_distribution
        self._world = world

    @property
    def enabled(self) -> bool:
        return self._difficulty.include_traps()

    def weighted(self) -> tuple[list[Age2ItemData], list[int]]:
        names: list[Age2ItemData] = []
        weights: list[int] = []
        for trap in Items.CATEGORY_TO_ITEMS[Items.Trap]:
            weight = (self._distribution[trap.item_name]
                      if trap.item_name in self._distribution else TRAP_DEFAULT_WEIGHT)
            if weight > 0:
                names.append(trap)
                weights.append(weight)
        return names, weights

    def share_of(self, spare: int) -> int:
        return int(spare * self._percentage.value / 100)

    def roll(self, spare: int) -> list[Age2ItemData]:
        if spare <= 0 or not self.enabled:
            return []
        names, weights = self.weighted()
        if not names:
            return []
        count = self.share_of(spare)
        if count <= 0:
            return []
        return self._world.random.choices(names, weights=weights, k=count)
