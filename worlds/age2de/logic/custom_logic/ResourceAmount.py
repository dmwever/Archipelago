from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar, override

from BaseClasses import CollectionState
from NetUtils import JSONMessagePart

from rule_builder.rules import False_, Rule, True_

from ...items.Items import Age2ItemData, Resource, StartingResources, TCResources


if TYPE_CHECKING:
    from ... import Age2World


def contributors(resource: Resource) -> tuple[tuple[str, int], ...]:
    """Every item that adds to the pile a scenario opens with, and what each one adds. The three
    town-centre items are the guaranteed floor: one of each is always pooled."""
    return tuple(sorted(
        (item.item_name, item.type.amount)
        for item in Age2ItemData
        if isinstance(item.type, (StartingResources, TCResources)) and item.type.type is resource
    ))


@dataclass
class HasResourceAmount(Rule["Age2World"], game="Age Of Empires II: Definitive Edition"):
    """Enough of one resource banked up front to pay a price.

    rule_builder has no summation primitive, so this is the one place payload amounts are added
    together. item_mapping cannot stand in for it: it never touches state.prog_items.
    """

    resource: Resource
    amount: int

    @override
    def _instantiate(self, world: "Age2World") -> Rule.Resolved:
        if self.amount <= 0:
            return True_().resolve(world)
        if world.starting_resource_totals[self.resource] < self.amount:
            return False_().resolve(world)
        return self.Resolved(
            contributors(self.resource),
            self.amount,
            self.resource,
            player=world.player,
            caching_enabled=getattr(world, "rule_caching_enabled", False),
        )

    @override
    def __str__(self) -> str:
        return f"HasResourceAmount({self.amount} {self.resource.name})"

    class Resolved(Rule.Resolved):
        item_amounts: tuple[tuple[str, int], ...]
        amount: int
        resource: Resource

        skip_cache: ClassVar[bool] = True
        """Cheaper to evaluate than to cache, and why item_dependencies hands back empty id sets
        the way Has.Resolved does."""

        @override
        def _evaluate(self, state: CollectionState) -> bool:
            held = state.prog_items[self.player]
            total = 0
            for item_name, each in self.item_amounts:
                total += held[item_name] * each
                if total >= self.amount:
                    return True
            return False

        @override
        def item_dependencies(self) -> dict[str, set[int]]:
            """Every name that can move the sum. LocalStart.solve narrows its candidates by this
            set, so a missing name means local start stops finding that resource."""
            return {item_name: set() for item_name, _ in self.item_amounts}

        @override
        def explain_json(self, state: CollectionState | None = None) -> list[JSONMessagePart]:
            colour = "green" if state and self(state) else "salmon"
            return [{"type": "color", "color": colour,
                     "text": f"{self.amount} starting {self.resource.name.lower()}"}]

        @override
        def explain_str(self, state: CollectionState | None = None) -> str:
            return f"Has {self.amount} starting {self.resource.name.lower()}"

        @override
        def __str__(self) -> str:
            return f"Has {self.amount} starting {self.resource.name.lower()}"
