"""A part of a scenario's rules under the name a player knows it by: "The Scourge of God can hunt".
It holds exactly when the rule it wraps does, so naming a rule never changes logic - only how it
reads in /explain, where it is one line with the rule behind its marker.

Use it for rules cheap enough to build each time they are asked; a rule worth building once per
scenario is a ScenarioQuestion instead. Equal named rules still resolve to one shared object, and
CachedRuleBuilderWorld caches its result per state like any other rule."""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, override

from BaseClasses import CollectionState
from NetUtils import JSONMessagePart

from rule_builder.rules import Rule, WrapperRule

if TYPE_CHECKING:
    from ... import Age2World


@dataclass
class Named(WrapperRule["Age2World"], game="Age Of Empires II: Definitive Edition"):
    label: str = ""
    """What it asks, scenario first: "The Scourge of God can hunt"."""

    @override
    def _instantiate(self, world: "Age2World") -> Rule.Resolved:
        return self.Resolved(
            self.child.resolve(world),
            self.label,
            player=world.player,
            caching_enabled=getattr(world, "rule_caching_enabled", False),
        )

    @override
    def __str__(self) -> str:
        return f"{self.label}[{self.child}]"

    class Resolved(WrapperRule.Resolved):
        label: str

        @property
        def always_true(self) -> bool:
            return self.child.always_true

        @property
        def always_false(self) -> bool:
            return self.child.always_false

        @property
        def description(self) -> str:
            """The label, read the way a scenario question's description is."""
            return self.label

        @property
        def answer(self) -> Rule.Resolved:
            """The rule it names, read the way a scenario question's answer is."""
            return self.child

        @override
        def explain_json(self, state: CollectionState | None = None) -> list[JSONMessagePart]:
            return [{"type": "color", "color": "green" if state and self(state) else "salmon",
                     "text": self.label}]

        @override
        def explain_str(self, state: CollectionState | None = None) -> str:
            return self.label
