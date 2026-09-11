"""Local Start — place the items needed for a playable opening in the player's own world.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from BaseClasses import CollectionState, Location
from Fill import sweep_from_pool
from rule_builder.rules import Rule

from ..locations.Campaigns import NAME_TO_CAMPAIGN
from ..locations.Locations import VICTORY_SCENARIO_LOCATIONS
from ..locations.Scenarios import CAMPAIGN_TO_SCENARIOS, Age2ScenarioData

if TYPE_CHECKING:
    from .. import Age2World

# What the solver can aim at: a location the player must be able to reach, or a
# resolved rule fragment that must evaluate true.
Target = Location | Rule.Resolved

def choose_start_scenario(world: 'Age2World') -> Age2ScenarioData | None:
    starting_campaigns = sorted(world.options.starting_campaigns.value)
    if not starting_campaigns:
        return None
    campaign = NAME_TO_CAMPAIGN[world.random.choice(starting_campaigns)]
    scenarios = CAMPAIGN_TO_SCENARIOS[campaign]
    if not scenarios:
        return None
    return scenarios[0]


def resolve(world: 'Age2World', rule: Rule) -> Rule.Resolved:
    resolved = rule.resolve(world)
    world.register_rule_dependencies(resolved)
    return resolved


def satisfied(target: Target, state: CollectionState) -> bool:
    """Whether the target is met in the given state."""
    if isinstance(target, Location):
        return target.can_reach(state)
    return target(state)


def state_with(world: 'Age2World', base_state: CollectionState, item_names: list[str]) -> CollectionState:
    """base_state plus the named items, swept so events and follow-on access come with it."""
    return sweep_from_pool(base_state, [world.create_item(name) for name in item_names])


def solve(
    world: 'Age2World',
    target: Target,
    base_state: CollectionState,
    candidates: list[str],
) -> list[str] | None:
    """A small set of item names that satisfies `target` on top of `base_state`."""
    if satisfied(target, base_state):
        return []
    if not satisfied(target, state_with(world, base_state, candidates)):
        return None

    chosen = list(candidates)
    world.random.shuffle(chosen)
    for name in list(chosen):
        trial = list(chosen)
        trial.remove(name)  # one copy, so counts shrink one at a time
        if satisfied(target, state_with(world, base_state, trial)):
            chosen = trial
    return chosen


def own_itempool_names(world: 'Age2World') -> list[str]:
    """Every item this player still has in the pool, as the solver's candidates."""
    return [item.name for item in world.multiworld.itempool if item.player == world.player]


def victory_location(world: 'Age2World', scenario: Age2ScenarioData) -> Location | None:
    """The scenario's victory location, or None when it is not in this playthrough."""
    location_data = VICTORY_SCENARIO_LOCATIONS.get(scenario.scenario_name)
    if location_data is None:
        return None
    try:
        return world.get_location(location_data.global_name())
    except KeyError:
        return None


def win_items(world: 'Age2World', scenario: Age2ScenarioData) -> list[str] | None:
    """Items that make `scenario` beatable from turn one."""
    victory = victory_location(world, scenario)
    if victory is None:
        return None
    return solve(world, victory, world.multiworld.state, own_itempool_names(world))
