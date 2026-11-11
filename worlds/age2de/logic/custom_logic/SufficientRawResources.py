from __future__ import annotations

from typing import TYPE_CHECKING, Iterable, override

from BaseClasses import CollectionState
from NetUtils import JSONMessagePart

from rule_builder.rules import False_, NestedRule, Rule, True_

if TYPE_CHECKING:
    from ... import Age2World


class SufficientRawResources(NestedRule["Age2World"], game="Age Of Empires II: Definitive Edition"):
    """Whether the raw sources a player can actually work add up to enough.
    """

    def __init__(self, sources: Iterable[tuple[Rule, int] | tuple[Rule, int, str, str]], needed: int,
                 resource: str = "", **kwargs) -> None:
        pairs = tuple(sources)
        super().__init__(*(source[0] for source in pairs), **kwargs)
        self.amounts = tuple(source[1] for source in pairs)
        self.needed = needed
        self.resource = resource
        """What is counted - "food" - for the explanation only."""
        self.areas = tuple(source[2] if len(source) > 2 else "" for source in pairs)
        """Where each source lies - "base", "open" - for the explanation only."""
        self.kinds = tuple(source[3] if len(source) > 3 else "" for source in pairs)
        """Which map count each source is - "shore_fish_count" - for the explanation only."""

    @override
    def _instantiate(self, world: "Age2World") -> Rule.Resolved:
        resolved = [(rule.resolve(world), amount, area, kind)
                    for rule, amount, area, kind in zip(self.children, self.amounts, self.areas, self.kinds)]
        live = [source for source in resolved if not source[0].always_false and source[1] > 0]
        if sum(amount for _, amount, _, _ in live) < self.needed:
            return False_().resolve(world)
        if sum(amount for rule, amount, _, _ in live if rule.always_true) >= self.needed:
            return True_().resolve(world)
        return self.Resolved(
            tuple(rule for rule, _, _, _ in live),
            tuple(amount for _, amount, _, _ in live),
            self.needed,
            self.resource,
            tuple(area for _, _, area, _ in live),
            tuple(kind for _, _, _, kind in live),
            player=world.player,
            caching_enabled=getattr(world, "rule_caching_enabled", False),
        )

    @override
    def __str__(self) -> str:
        children = ", ".join(f"{rule}x{amount}"
                             for rule, amount in zip(self.children, self.amounts))
        return f"SufficientRawResources({self.needed} from {children})"

    class Resolved(NestedRule.Resolved):
        amounts: tuple[int, ...]
        needed: int
        resource: str = ""
        areas: tuple[str, ...] = ()
        kinds: tuple[str, ...] = ()

        @override
        def _evaluate(self, state: CollectionState) -> bool:
            total = 0
            for rule, amount in zip(self.children, self.amounts):
                if rule(state):
                    total += amount
                    if total >= self.needed:
                        return True
            return False

        @override
        def explain_json(self, state: CollectionState | None = None) -> list[JSONMessagePart]:
            colour = "green" if state and self(state) else "salmon"
            messages: list[JSONMessagePart] = [
                {"type": "color", "color": colour, "text": f"{self.needed} worth of "}]
            for index, child in enumerate(self.children):
                if index:
                    messages.append({"type": "text", "text": " + "})
                messages.extend(child.explain_json(state))
            return messages

        @override
        def explain_str(self, state: CollectionState | None = None) -> str:
            clauses = " + ".join(child.explain_str(state) for child in self.children)
            return f"{self.needed} worth of ({clauses})"

        @override
        def __str__(self) -> str:
            return f"{self.needed} worth of {len(self.children)} sources"
