from __future__ import annotations

from typing import TYPE_CHECKING

from rule_builder.rules import Rule, True_

from ..locations.FillerLocations import Age2FillerLocationData
from ..logic.filler_logic import KIND_TO_FIELD

if TYPE_CHECKING:
    from .Rules import Rules


class FillerRules:
    def __init__(self, rules: 'Rules') -> None:
        self.world = rules.world
        self.logic = rules.logic

    def set_rules(self) -> None:
        for filler in self.world.pool.filler.locations:
            rule = self.rule_for(filler)
            if isinstance(rule, True_):
                continue
            self.world.set_rule(self.world.get_location(filler.location_name), rule)

    def rule_for(self, filler: Age2FillerLocationData) -> Rule:
        if filler.kind not in KIND_TO_FIELD:
            raise NotImplementedError(
                f"{filler.kind.name} has no rule yet, so {filler.location_name} cannot be a "
                "location. FillerPool should not have selected it.")
        return self.logic.filler.can_earn_anywhere(filler)
