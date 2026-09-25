from __future__ import annotations

from typing import TYPE_CHECKING

from rule_builder.rules import Has, Rule, True_

from ..items.items import MOCK_ITEM

if TYPE_CHECKING:
    from .. import InsaniquariumWorld


class InsaniquariumLogic:
    """Building blocks for rules. Every method returns a rule-builder Rule; rules/ decides where they apply."""

    def __init__(self, world: InsaniquariumWorld) -> None:
        self.world = world

    def has(self, item_name: str, count: int = 1) -> Rule:
        return Has(item_name, count)

    def can_reach_mock_location(self) -> Rule:
        return True_()

    def can_win(self) -> Rule:
        return self.has(MOCK_ITEM)
