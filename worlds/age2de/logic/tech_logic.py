from __future__ import annotations

from typing import TYPE_CHECKING

from rule_builder.rules import Has, Rule, True_

from ..Options import LockTechs
from ..locations.Techs import Age2TechData


if TYPE_CHECKING:
    from .. import Age2World
    from .Logic import Logic


class TechLogic:
    def __init__(self, logic: 'Logic', world: Age2World):
        self.logic = logic
        self.world = world

    def has_tech_item(self, tech: Age2TechData) -> Rule:
        if self.world.options.lock_techs == LockTechs.option_effects:
            return True_()
        return Has(tech.item.item_name)
