from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, override

from NetUtils import JSONMessagePart
from BaseClasses import CollectionState

from rule_builder.rules import NestedRule


if TYPE_CHECKING:
    from ... import Age2World


@dataclass
class TwoBuildingsRequirement(NestedRule["Age2World"], game="Age Of Empires II: Definitive Edition"):
    """A rule that checks that a player has at least two of the needed buildings to age up"""

    class Resolved(NestedRule.Resolved):
        num_needed: int = 2

        @override
        def _evaluate(self, state: CollectionState) -> bool:
            count_reached: int = 0
            
            for rule in self.children:
                if rule(state):
                    count_reached += 1
            return count_reached >= self.num_needed


        @override
        def explain_json(self, state: CollectionState | None = None) -> list[JSONMessagePart]:
            # this method can be overridden to display custom explanations
            messages: list[JSONMessagePart] = [{"type": "text", "text": f"Need {self.num_needed} of"}]
            for i, child in enumerate(self.children):
                if i > 0:
                    messages.append({"type": "color",
                                     "color": "green" if state and self(state) else "salmon",
                                     "text": " | "})
                messages.extend(child.explain_json(state))
            messages.append({"type": "text", "text": " Buildings"})
            
            return messages