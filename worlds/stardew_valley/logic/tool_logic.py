from typing import Union

from Utils import cache_self1
from .base_logic import BaseLogicMixin, BaseLogic
from .has_logic import HasLogicMixin
from .money_logic import MoneyLogicMixin
from .option_logic import OptionLogicMixin
from .received_logic import ReceivedLogicMixin
from .region_logic import RegionLogicMixin
from .season_logic import SeasonLogicMixin
from .. import options
from ..mods.logic.magic_logic import MagicLogicMixin
from ..options import ToolProgression
from ..stardew_rule import StardewRule, True_
from ..strings.region_names import Region
from ..strings.skill_names import ModSkill
from ..strings.spells import MagicSpell
from ..strings.tool_names import ToolMaterial, Tool

fishing_rod_price_by_tier = {2: 500, 3: 1800, 4: 7500}

tool_materials = {
    ToolMaterial.copper: 1,
    ToolMaterial.iron: 2,
    ToolMaterial.gold: 3,
    ToolMaterial.iridium: 4
}

tool_upgrade_prices = {
    ToolMaterial.copper: 2000,
    ToolMaterial.iron: 5000,
    ToolMaterial.gold: 10000,
    ToolMaterial.iridium: 25000
}


class ToolLogicMixin(BaseLogicMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tool = ToolLogic(*args, **kwargs)


class ToolLogic(BaseLogic[Union[ToolLogicMixin, HasLogicMixin, ReceivedLogicMixin, RegionLogicMixin, SeasonLogicMixin, MoneyLogicMixin, MagicLogicMixin,
OptionLogicMixin]]):
    # Should be cached
    def has_tool(self, tool: str, material: str = ToolMaterial.basic) -> StardewRule:
        if material == ToolMaterial.basic or tool == Tool.scythe:
            return True_()

        def create_rule(tool_progression):
            if tool_progression & options.ToolProgression.option_progressive:
                return self.logic.received(f"Progressive {tool}", tool_materials[material])

            return self.logic.has(f"{material} Bar") & self.logic.money.can_spend(tool_upgrade_prices[material])

        # For some reason, using a "bitwise_choice" here completely destroys performances
        return self.logic.option.custom_rule(options.ToolProgression, rule_factory=create_rule)

    @cache_self1
    def has_fishing_rod(self, level: int) -> StardewRule:
        assert level > 0, "Can't have a negative fishing rod level"

        progressive_tool_rule = self.logic.received(f"Progressive {Tool.fishing_rod}", level)
        if self.options.tool_progression & ToolProgression.option_progressive:
            return progressive_tool_rule

        if level == 1:
            return self.logic.option.bitwise_choice(options.ToolProgression,
                                                    value=options.ToolProgression.option_progressive,
                                                    match=progressive_tool_rule,
                                                    no_match=self.logic.region.can_reach(Region.beach))
        return self.logic.option.bitwise_choice(options.ToolProgression,
                                                value=options.ToolProgression.option_progressive,
                                                match=progressive_tool_rule,
                                                no_match=self.logic.money.can_spend_at(Region.fish_shop, fishing_rod_price_by_tier[min(level, 4)]))

    # Should be cached
    def can_forage(self, season: str, region: str = Region.forest, need_hoe: bool = False) -> StardewRule:
        season_rule = self.logic.season.has(season)
        region_rule = self.logic.region.can_reach(region)
        if need_hoe:
            return season_rule & region_rule & self.logic.tool.has_tool(Tool.hoe)
        return season_rule & region_rule

    @cache_self1
    def can_water(self, level: int) -> StardewRule:
        tool_rule = self.logic.tool.has_tool(Tool.watering_can, ToolMaterial.tiers[level])
        spell_rule = self.logic.received(MagicSpell.water) & self.logic.magic.can_use_altar() & self.logic.received(f"{ModSkill.magic} Level", level)
        return tool_rule | spell_rule
