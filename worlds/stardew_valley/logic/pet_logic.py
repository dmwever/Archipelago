import math

from typing import Union

from .cached_logic import CachedLogic
from .logic_cache import CachedRules
from .received_logic import ReceivedLogic
from .region_logic import RegionLogic
from .time_logic import TimeLogic
from .tool_logic import ToolLogic
from .. import options
from ..data.villagers_data import Villager
from ..options import Friendsanity, FriendsanityHeartSize
from ..stardew_rule import StardewRule, True_
from ..strings.region_names import Region
from ..strings.villager_names import NPC


class PetLogic(CachedLogic):
    friendsanity_option: Friendsanity
    heart_size_option: FriendsanityHeartSize
    received: ReceivedLogic
    region: RegionLogic
    time: TimeLogic
    tool: ToolLogic

    def __init__(self, player: int, cached_rules: CachedRules, friendsanity_option: Friendsanity, heart_size_option: FriendsanityHeartSize,
                 received_logic: ReceivedLogic, region: RegionLogic, time: TimeLogic, tool: ToolLogic):
        super().__init__(player, cached_rules)
        self.friendsanity_option = friendsanity_option
        self.heart_size_option = heart_size_option
        self.received = received_logic
        self.region = region
        self.time = time
        self.tool = tool

    def has_hearts(self, hearts: int = 1) -> StardewRule:
        if hearts <= 0:
            return True_()
        if self.friendsanity_option == Friendsanity.option_none or self.friendsanity_option == Friendsanity.option_bachelors:
            return self.can_befriend_pet(hearts)
        return self.received_hearts(NPC.pet, hearts)

    def received_hearts(self, npc: Union[str, Villager], hearts: int) -> StardewRule:
        if isinstance(npc, Villager):
            return self.received_hearts(npc.name, hearts)
        return self.received(self.heart(npc), math.ceil(hearts / self.heart_size_option))

    def can_befriend_pet(self, hearts: int):
        if hearts <= 0:
            return True_()
        points = hearts * 200
        points_per_month = 12 * 14
        points_per_water_month = 18 * 14
        farm_rule = self.region.can_reach(Region.farm)
        time_with_water_rule = self.tool.can_water(0) & self.time.has_lived_months(points // points_per_water_month)
        time_without_water_rule = self.time.has_lived_months(points // points_per_month)
        time_rule = time_with_water_rule | time_without_water_rule
        return farm_rule & time_rule

    def heart(self, npc: Union[str, Villager]) -> str:
        if isinstance(npc, str):
            return f"{npc} <3"
        return self.heart(npc.name)

