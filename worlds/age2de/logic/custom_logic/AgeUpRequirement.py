from __future__ import annotations

import dataclasses
from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable, override

from NetUtils import JSONMessagePart
from BaseClasses import CollectionState

from rule_builder.rules import NestedRule, Rule

from ...locations.Ages import Age2AgeData
from ...locations.Buildings import Age2BuildingData


if TYPE_CHECKING:
    from ... import Age2World


@dataclass
class AgeUpRequirement(NestedRule["Age2World"], game="Age Of Empires II: Definitive Edition"):
    """A rule that checks that a player has at least two of the needed buildings to age up, or the
    single building that counts for both.

    It also carries which buildings those are, so the budget can price leaving an age from the
    same place the rule is built."""

    buildings: tuple[Age2BuildingData, ...] = ()
    """The buildings, two of which leave the age: the children, in order. A tuple, as a rule's
    fields are."""
    single_building: Age2BuildingData | None = None
    """One that counts for two on its own - a Castle - and the last child when there is one."""
    into_age: Age2AgeData | None = None
    """The age these buildings climb into."""

    @classmethod
    def from_buildings(
        cls,
        has_building: Callable[[Age2BuildingData], Rule],
        into_age: Age2AgeData,
        buildings: list[Age2BuildingData],
        single_building: Age2BuildingData | None = None,
    ) -> AgeUpRequirement:
        """The rule, its children asked of `has_building` for each building."""
        children = [has_building(building) for building in buildings]
        if single_building is not None:
            children.append(has_building(single_building))
        return cls(
            children,
            buildings=tuple(buildings),
            single_building=single_building,
            into_age=into_age,
        )

    def narrowed_by_scenario(
        self,
        could_have: Callable[[Age2BuildingData], bool],
        choice_order: Callable[[Age2BuildingData], int],
    ) -> AgeUpRequirement:
        """The same rule, less the buildings that could never stand, the rest in choice order.
        Those children are always false, so two of the rest is the same answer."""
        kept = sorted(
            (
                (building, child) for building, child in zip(self.buildings, self.children)
                    if could_have(building)
            ),
            key=lambda pair: choice_order(pair[0]),
        )
        children = [child for _, child in kept]

        single_building = self.single_building
        if single_building is not None and could_have(single_building):
            children.append(self.children[-1])
        else:
            single_building = None

        return dataclasses.replace(
            self,
            children=children,
            buildings=tuple(building for building, _ in kept),
            single_building=single_building,
        )

    @override
    def _instantiate(self, world: Age2World) -> Rule.Resolved:
        return self.Resolved(
            tuple(child.resolve(world) for child in self.children),
            self.single_building is not None,
            player=world.player,
            caching_enabled=getattr(world, "rule_caching_enabled", False),
        )

    class Resolved(NestedRule.Resolved):
        has_single: bool = False
        """Whether the last child is the single building that counts for both."""
        num_needed: int = 2

        @property
        def pairs(self) -> tuple[Rule.Resolved, ...]:
            return self.children[:-1] if self.has_single else self.children

        @override
        def _evaluate(self, state: CollectionState) -> bool:
            if self.has_single and self.children[-1](state):
                return True
            count_reached: int = 0
            for rule in self.pairs:
                if rule(state):
                    count_reached += 1
            return count_reached >= self.num_needed

        @override
        def explain_json(self, state: CollectionState | None = None) -> list[JSONMessagePart]:
            # this method can be overridden to display custom explanations
            messages: list[JSONMessagePart] = [{"type": "text", "text": f"Need {self.num_needed} of"}]
            for i, child in enumerate(self.pairs):
                if i > 0:
                    messages.append({"type": "color",
                                     "color": "green" if state and self(state) else "salmon",
                                     "text": " | "})
                messages.extend(child.explain_json(state))
            messages.append({"type": "text", "text": " Buildings"})
            if self.has_single:
                messages.append({"type": "text", "text": ", or "})
                messages.extend(self.children[-1].explain_json(state))
            return messages

        @override
        def explain_str(self, state: CollectionState | None = None) -> str:
            clauses = " | ".join(child.explain_str(state) for child in self.pairs)
            text = f"Need {self.num_needed} of ({clauses}) Buildings"
            if self.has_single:
                text += f", or {self.children[-1].explain_str(state)}"
            return text
