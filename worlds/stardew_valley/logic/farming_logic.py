from typing import Union

from .base_logic import BaseLogicMixin, BaseLogic
from .has_logic import HasLogicMixin
from .skill_logic import SkillLogicMixin
from ..stardew_rule import StardewRule, True_
from ..strings.fertilizer_names import Fertilizer


class FarmingLogicMixin(BaseLogicMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.farming = FarmingLogic(*args, **kwargs)


class FarmingLogic(BaseLogic[Union[HasLogicMixin, SkillLogicMixin, FarmingLogicMixin]]):
    def has_fertilizer(self, tier: int) -> StardewRule:
        if tier <= 0:
            return True_()
        if tier == 1:
            return self.logic.has(Fertilizer.basic)
        if tier == 2:
            return self.logic.has(Fertilizer.quality)
        if tier >= 3:
            return self.logic.has(Fertilizer.deluxe)

    def can_grow_crop_quality(self, quality: int) -> StardewRule:
        if quality <= 0:
            return True_()
        if quality == 1:
            return self.logic.skill.has_farming_level(5) | (self.logic.farming.has_fertilizer(1) & self.logic.skill.has_farming_level(2)) | (
                    self.logic.farming.has_fertilizer(2) & self.logic.skill.has_farming_level(1)) | self.logic.farming.has_fertilizer(3)
        if quality == 2:
            return self.logic.skill.has_farming_level(10) | (
                    self.logic.farming.has_fertilizer(1) & self.logic.skill.has_farming_level(5)) | (
                    self.logic.farming.has_fertilizer(2) & self.logic.skill.has_farming_level(3)) | (
                    self.logic.farming.has_fertilizer(3) & self.logic.skill.has_farming_level(2))
        if quality >= 3:
            return self.logic.farming.has_fertilizer(3) & self.logic.skill.has_farming_level(4)
