"""Local Start — place the items needed for a playable opening in the player's own world.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import logging
from collections import Counter

from BaseClasses import CollectionState, Item, Location
from Fill import FillError, fill_restrictive, sweep_from_pool
from rule_builder.rules import And, Rule, True_

from ..Options import LocalStart
from ..items.Items import NAME_TO_ITEM, Campaign, ProgressiveScenario
from ..locations.Locations import VICTORY_SCENARIO_LOCATIONS
from ..locations.Scenarios import CAMPAIGN_TO_SCENARIOS, Age2ScenarioData

if TYPE_CHECKING:
    from .. import Age2World

Target = Location | Rule.Resolved

def choose_start_scenario(world: 'Age2World') -> Age2ScenarioData:
    campaign = world.random.choice(sorted(world.starting_campaigns, key=lambda c: c.campaign_name))
    return CAMPAIGN_TO_SCENARIOS[campaign][0]

def resolve(world: 'Age2World', rule: Rule) -> Rule.Resolved:
    resolved = rule.resolve(world)
    world.register_rule_dependencies(resolved)
    return resolved

def satisfied(target: Target, state: CollectionState) -> bool:
    return target.can_reach(state) if isinstance(target, Location) else target(state)

def state_with(world: 'Age2World', base_state: CollectionState, item_names: list[str]) -> CollectionState:
    player = world.player
    state = CollectionState.__new__(CollectionState)
    state.multiworld = base_state.multiworld
    state.prog_items = {player: base_state.prog_items[player].copy()}
    state.reachable_regions = {player: base_state.reachable_regions[player].copy()}
    state.blocked_connections = {player: base_state.blocked_connections[player].copy()}
    state.advancements = base_state.advancements.copy()
    state.path = base_state.path.copy()
    state.locations_checked = base_state.locations_checked.copy()
    state.stale = {player: True}
    state.allow_partial_entrances = base_state.allow_partial_entrances
    for function in CollectionState.additional_init_functions:
        function(state, state.multiworld)
    for function in CollectionState.additional_copy_functions:
        state = function(base_state, state)
    for name in item_names:
        state.collect(world.create_item(name), True)
    state.sweep_for_advancements(locations=world.multiworld.get_locations(player))
    return state

def solve(
    world: 'Age2World',
    target: Target,
    base_state: CollectionState,
    candidates: list[str],
) -> list[str] | None:
    """A small set of item names that satisfies `target` on top of `base_state`."""
    if satisfied(target, base_state):
        return []

    chosen = list(candidates)
    world.random.shuffle(chosen)

    rule = target if isinstance(target, Rule.Resolved) else getattr(target, "access_rule", None)
    depends_on = rule.item_dependencies().keys() if isinstance(rule, Rule.Resolved) else None
    narrowed = [name for name in chosen if name in depends_on] if depends_on is not None else chosen

    if len(narrowed) < len(chosen) and satisfied(target, state_with(world, base_state, narrowed)):
        chosen = narrowed
    elif not satisfied(target, state_with(world, base_state, chosen)):
        return None

    for name in list(chosen):
        trial = list(chosen)
        trial.remove(name)
        if satisfied(target, state_with(world, base_state, trial)):
            chosen = trial
    return chosen

def own_itempool_names(world: 'Age2World') -> list[str]:
    return [item.name for item in world.multiworld.itempool if item.player == world.player]

def base_candidate_names(world: 'Age2World') -> list[str]:
    return [name for name in own_itempool_names(world)
            if not isinstance(NAME_TO_ITEM[name].type, (ProgressiveScenario, Campaign))]

def win_items(world: 'Age2World', scenario: Age2ScenarioData) -> list[str] | None:
    """Items that make `scenario` beatable from turn one."""
    victory = world.get_location(VICTORY_SCENARIO_LOCATIONS[scenario.scenario_name].global_name())
    return solve(world, victory, world.multiworld.state, own_itempool_names(world))

def conjuncts(rule: Rule) -> list[Rule]:
    """Flatten a conjunction into the parts that must each hold on their own."""
    if isinstance(rule, And) and not rule.options:
        return [part for child in rule.children for part in conjuncts(child)]
    return [rule]

def scenario_base_rule(world: 'Age2World', scenario: Age2ScenarioData) -> Rule:
    has_base = scenario.logic(world.rules.logic).has_base
    return True_() if resolve(world, has_base).always_false else has_base

def base_items(
    world: 'Age2World',
    scenario: Age2ScenarioData,
    granted: list[str] | None = None,
) -> list[str]:
    """Items that let the player build a town centre, plus anything extra `scenario` asks for."""
    target = world.rules.logic.can_build_base() & scenario_base_rule(world, scenario)

    base_state = state_with(world, world.multiworld.state, granted) if granted else world.multiworld.state
    candidates = base_candidate_names(world)
    needed: Counter[str] = Counter()
    reachable: list[Rule] = []
    for conjunct in conjuncts(target):
        resolved = resolve(world, conjunct)
        if resolved.always_true:
            continue
        solved = solve(world, resolved, base_state, candidates)
        if solved is None:
            continue
        reachable.append(conjunct)
        for name, count in Counter(solved).items():
            needed[name] = max(needed[name], count)

    if not reachable:
        return []

    combined = reachable[0]
    for conjunct in reachable[1:]:
        combined = combined & conjunct
    trimmed = solve(world, resolve(world, combined), base_state, sorted(needed.elements()))
    return sorted(trimmed if trimmed is not None else needed.elements())

def take_from_itempool(world: 'Age2World', names: list[str]) -> list[Item]:
    wanted = Counter(names)
    taken: list[Item] = []
    for item in list(world.multiworld.itempool):
        if item.player == world.player and wanted[item.name] > 0:
            wanted[item.name] -= 1
            world.multiworld.itempool.remove(item)
            taken.append(item)
    if +wanted:
        logging.warning("Local Start: %s not in the itempool, skipping: %s",
                        world.player_name, dict(+wanted))
    return taken

def place_locally(world: 'Age2World', items: list[Item], base_state: CollectionState,
                  locations: list[Location], name: str) -> None:
    if not items:
        return
    attempted = list(items)
    try:
        fill_restrictive(world.multiworld, base_state, locations, items,
                         single_player_placement=True, lock=True, allow_partial=False, name=name)
    except FillError:
        returned = [item for item in attempted if item.location is None]
        world.multiworld.itempool.extend(returned)
        logging.warning("Local Start: %s could not place %s, returning them to the pool: %s",
                        world.player_name, name, sorted(item.name for item in returned))

def local_start_sets(world: 'Age2World') -> tuple[list[str], list[str]]:
    """(win set, base set) for the chosen option value. Either may be empty."""
    scenario = choose_start_scenario(world)
    option = world.options.local_start
    win_set: list[str] = []
    if option in (LocalStart.option_guarantee_win_first_scenario, LocalStart.option_both):
        win_set = win_items(world, scenario)
        if win_set is None:
            logging.warning("Local Start: %s cannot be made beatable locally for %s for this world.",
                            scenario.scenario_name, world.player_name)
            win_set = []

    base_set = base_items(world, scenario, win_set) \
        if option in (LocalStart.option_base, LocalStart.option_both) else []
    return win_set, base_set

def apply(world: 'Age2World') -> None:
    """Entry point from Age2World.pre_fill."""
    if world.options.local_start == LocalStart.option_no:
        return

    win_set, base_set = local_start_sets(world)
    if not win_set and not base_set:
        return

    base_only = list((Counter(base_set) - Counter(win_set)).elements())
    logging.info("Local Start: %s placing win=%s base=%s",
                 world.player_name, sorted(win_set), sorted(base_only))

    place_locally(world, take_from_itempool(world, win_set), world.multiworld.state,
                  world.multiworld.get_unfilled_locations(world.player),
                  "Age2 Local Start (win)")
    place_locally(world, take_from_itempool(world, base_only),
                  sweep_from_pool(world.multiworld.state, world.multiworld.itempool),
                  [location for location in world.multiworld.get_unfilled_locations(world.player)
                   if not location.can_reach(world.multiworld.state)],
                  "Age2 Local Start (base)")
