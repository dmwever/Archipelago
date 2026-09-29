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

    def __init__(self, sources: Iterable[tuple[Rule, int]], needed: int, **kwargs) -> None:
        pairs = tuple(sources)
        super().__init__(*(rule for rule, _ in pairs), **kwargs)
        self.amounts = tuple(amount for _, amount in pairs)
        self.needed = needed

    @override
    def _instantiate(self, world: "Age2World") -> Rule.Resolved:
        resolved = [(rule.resolve(world), amount)
                    for rule, amount in zip(self.children, self.amounts)]
        live = [(rule, amount) for rule, amount in resolved if not rule.always_false and amount > 0]
        if sum(amount for _, amount in live) < self.needed:
            return False_().resolve(world)
        if sum(amount for rule, amount in live if rule.always_true) >= self.needed:
            return True_().resolve(world)
        return self.Resolved(
            tuple(rule for rule, _ in live),
            tuple(amount for _, amount in live),
            self.needed,
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
