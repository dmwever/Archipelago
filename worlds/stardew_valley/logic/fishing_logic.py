from typing import Union

from Utils import cache_self1
from .base_logic import BaseLogicMixin, BaseLogic
from .option_logic import OptionLogicMixin
from .received_logic import ReceivedLogicMixin
from .region_logic import RegionLogicMixin
from .season_logic import SeasonLogicMixin
from .skill_logic import SkillLogicMixin
from .tool_logic import ToolLogicMixin
from .. import options
from ..data import FishItem
from ..data.fish_data import legendary_fish
from ..stardew_rule import StardewRule, True_, False_, And
from ..strings.fish_names import SVEFish
from ..strings.quality_names import FishQuality
from ..strings.region_names import Region
from ..strings.skill_names import Skill


class FishingLogicMixin(BaseLogicMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fishing = FishingLogic(*args, **kwargs)


class FishingLogic(
    BaseLogic[Union[FishingLogicMixin, ReceivedLogicMixin, RegionLogicMixin, SeasonLogicMixin, ToolLogicMixin, SkillLogicMixin, OptionLogicMixin]]):
    def can_fish_in_freshwater(self) -> StardewRule:
        return self.logic.skill.can_fish() & self.logic.region.can_reach_any((Region.forest, Region.town, Region.mountain))

    def has_max_fishing(self) -> StardewRule:
        skill_rule = self.logic.skill.has_level(Skill.fishing, 10)
        return self.logic.tool.has_fishing_rod(4) & skill_rule

    def can_fish_chests(self) -> StardewRule:
        skill_rule = self.logic.skill.has_level(Skill.fishing, 6)
        return self.logic.tool.has_fishing_rod(4) & skill_rule

    def can_fish_at(self, region: str) -> StardewRule:
        return self.logic.skill.can_fish() & self.logic.region.can_reach(region)

    @cache_self1
    def can_catch_fish(self, fish: FishItem) -> StardewRule:
        quest_rule = True_()
        if fish.extended_family:
            quest_rule = self.logic.fishing.can_start_extended_family_quest()
        region_rule = self.logic.region.can_reach_any(fish.locations)
        season_rule = self.logic.season.has_any(fish.seasons)
        if fish.difficulty == -1:
            difficulty_rule = self.logic.skill.can_crab_pot
        else:
            difficulty_rule = self.logic.skill.can_fish(difficulty=(120 if fish.legendary else fish.difficulty))
        if fish.name == SVEFish.kittyfish:
            item_rule = self.logic.received("Kittyfish Spell")
        else:
            item_rule = True_()
        return quest_rule & region_rule & season_rule & difficulty_rule & item_rule

    def can_start_extended_family_quest(self) -> StardewRule:
        def create_rule(exclude_ginger_island, special_order_locations):
            if exclude_ginger_island == options.ExcludeGingerIsland.option_true:
                return False_()
            if special_order_locations != options.SpecialOrderLocations.option_board_qi:
                return False_()
            return self.logic.region.can_reach(Region.qi_walnut_room) & And(*(self.logic.fishing.can_catch_fish(fish) for fish in legendary_fish))

        return self.logic.option.custom_rule(options.ExcludeGingerIsland, options.SpecialOrderLocations,
                                             rule_factory=create_rule)

    def can_catch_quality_fish(self, fish_quality: str) -> StardewRule:
        if fish_quality == FishQuality.basic:
            return True_()
        rod_rule = self.logic.tool.has_fishing_rod(2)
        if fish_quality == FishQuality.silver:
            return rod_rule
        if fish_quality == FishQuality.gold:
            return rod_rule & self.logic.skill.has_level(Skill.fishing, 4)
        if fish_quality == FishQuality.iridium:
            return rod_rule & self.logic.skill.has_level(Skill.fishing, 10)
        return False_()
