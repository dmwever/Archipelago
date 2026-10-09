from typing import TYPE_CHECKING

from rule_builder.rules import False_, Has, Rule, True_
from ...locations.Locations import Age2ScenarioLocationData
from ...items.Items import Age2ItemData

from ..ScenarioLogic import ScenarioStartingState


if TYPE_CHECKING:
    from ..Logic import Logic

class Genghis4StartingState(ScenarioStartingState):

    def __init__(self, logic: 'Logic'):
        super().__init__()
        self.logic = logic
        self.is_unlocked = Has(Age2ScenarioLocationData.GEN3_VICTORY.scenario.scenario_name + ": Unlock Next Scenario") & Has("Progressive Genghis Khan Scenario", 3)
        # Every scrap of this chapter's stone is scanned into the ENEMY tier, and that tier is
        # gated on must_steal_base. Without this the chapter has no reachable stone at all.
        # See the TODO in ScenarioResources: six quarries are still untiered, and re-tiering
        # them may make this unnecessary.
        self.must_steal_base = True_()
