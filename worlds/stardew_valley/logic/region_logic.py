from functools import lru_cache
from typing import Tuple

from .cached_logic import CachedLogic, CachedRules
from ..stardew_rule import StardewRule, And, Or, Reach, Count


class RegionLogic(CachedLogic):

    def __init__(self, player: int, cached_rules: CachedRules):
        super().__init__(player, cached_rules)

    @lru_cache(maxsize=None)
    def can_reach(self, region_name: str) -> StardewRule:
        return Reach(region_name, "Region", self.player)

    @lru_cache(maxsize=None)
    def can_reach_any(self, region_names: Tuple[str, ...]) -> StardewRule:
        return Or(self.can_reach(spot) for spot in region_names)

    @lru_cache(maxsize=None)
    def can_reach_all(self, region_names: Tuple[str, ...]) -> StardewRule:
        return And(self.can_reach(spot) for spot in region_names)

    @lru_cache(maxsize=None)
    def can_reach_all_except_one(self, region_names: Tuple[str, ...]) -> StardewRule:
        region_names = list(region_names)
        num_required = len(region_names) - 1
        if num_required <= 0:
            num_required = len(region_names)
        return Count(num_required, [self.can_reach(spot) for spot in region_names])

    @lru_cache(maxsize=None)
    def can_reach_location(self, location_names: str) -> StardewRule:
        return Reach(location_names, "Location", self.player)

    @lru_cache(maxsize=None)
    def can_reach_entrance(self, entrance_name: str) -> StardewRule:
        return Reach(entrance_name, "Entrance", self.player)
