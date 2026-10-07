from __future__ import annotations

from typing import TYPE_CHECKING

from rule_builder.rules import False_, Or, Rule

from ..locations.FillerLocations import Age2FillerLocationData, FillerKind
from ..locations.connections.ScenarioMilestones import MilestoneCapability, capability

if TYPE_CHECKING:
    from .Logic import Logic


KIND_TO_FIELD: dict[FillerKind, str] = {
    FillerKind.EXPLORE: "explore",
    FillerKind.KILL_UNITS: "kill",
    FillerKind.RAZE_BUILDINGS: "raze",
    FillerKind.OWN_UNITS: "own",
    FillerKind.CONVERT_UNITS: "convert",
}


class FillerLogic:
    def __init__(self, logic: 'Logic') -> None:
        self.logic = logic

    def affords(self, filler: Age2FillerLocationData,
                afforded: MilestoneCapability) -> bool:
        if filler.kind not in KIND_TO_FIELD:
            return False
        return getattr(afforded, KIND_TO_FIELD[filler.kind]) >= filler.threshold

    def can_earn_anywhere(self, filler: Age2FillerLocationData) -> Rule:
        ways = [scenario.is_unlocked() for scenario in self.logic.scenarios
                if self.affords(filler, capability(scenario.scenario))]
        if not ways:
            return False_()
        return Or(*ways)

    def is_earnable(self, filler: Age2FillerLocationData) -> bool:
        return any(self.affords(filler, capability(scenario.scenario))
                   for scenario in self.logic.scenarios)
