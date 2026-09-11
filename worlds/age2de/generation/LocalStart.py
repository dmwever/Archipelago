"""Local Start — place the items needed for a playable opening in the player's own world.

Phase 2: campaign/scenario selection only. Nothing here touches item placement.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..locations.Campaigns import NAME_TO_CAMPAIGN
from ..locations.Scenarios import CAMPAIGN_TO_SCENARIOS, Age2ScenarioData

if TYPE_CHECKING:
    from .. import Age2World

def choose_start_scenario(world: 'Age2World') -> Age2ScenarioData | None:
    starting_campaigns = sorted(world.options.starting_campaigns.value)
    if not starting_campaigns:
        return None
    campaign = NAME_TO_CAMPAIGN[world.random.choice(starting_campaigns)]
    scenarios = CAMPAIGN_TO_SCENARIOS[campaign]
    if not scenarios:
        return None
    return scenarios[0]
