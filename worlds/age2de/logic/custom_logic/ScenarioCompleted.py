from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar, override

from BaseClasses import CollectionState

from rule_builder.rules import Rule

from ...locations.Scenarios import Age2ScenarioData

if TYPE_CHECKING:
    from ... import Age2World


def _label(scenario: Age2ScenarioData) -> str:
    return f"{scenario.scenario_name} completed"


@dataclass
class ScenarioCompleted(Rule["Age2World"], game="Age Of Empires II: Definitive Edition"):
    scenario: Age2ScenarioData | None = None

    @override
    def _instantiate(self, world: "Age2World") -> Rule.Resolved:
        return self.Resolved(self.scenario, player=world.player,
                             caching_enabled=getattr(world, "rule_caching_enabled", False))

    @override
    def __str__(self) -> str:
        return _label(self.scenario)

    class Resolved(Rule.Resolved):
        scenario: Age2ScenarioData

        force_recalculate: ClassVar[bool] = True

        @override
        def _evaluate(self, state: CollectionState) -> bool:
            world: Age2World = state.multiworld.worlds[self.player]
            return self.scenario in world.completed_scenarios

        @override
        def __str__(self) -> str:
            return _label(self.scenario)
