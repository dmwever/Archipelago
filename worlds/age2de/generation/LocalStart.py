"""Local Start — place the items needed for a playable opening in the player's own world.

Phases 2-3: scenario selection and the solver that works out which items a target
needs. Nothing here places anything yet.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from BaseClasses import CollectionState, Location
from Fill import sweep_from_pool
from rule_builder.rules import Rule

from ..locations.Campaigns import NAME_TO_CAMPAIGN
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
    """Resolve a rule fragment for use as a solver target.

    Rules resolved outside World.set_rule are not registered, so the caching layer
    never invalidates them and a cached False can go stale as the solver collects
    items. Registering the dependencies wires it into the same invalidation the
    world's own access rules get.
    """
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
    """A small set of item names that satisfies `target` on top of `base_state`.

    `candidates` may repeat a name to offer more than one copy, which is how a
    `Has(item, count=n)` requirement gets met.

    Returns an empty list when the target is already satisfied and needs nothing,
    or None when even the whole candidate pool cannot satisfy it — the caller
    decides whether that is fatal or a conjunct to skip.

    The result is minimal in the sense that dropping any single item from it breaks
    the target. It is not guaranteed to be the globally smallest such set; which
    minimal set comes out depends on the seeded shuffle, so it is stable per seed.
    """
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
