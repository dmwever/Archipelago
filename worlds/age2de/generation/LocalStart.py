"""Local Start — place the items needed for a playable opening in the player's own world.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import logging
from collections import Counter

from BaseClasses import CollectionState, Item, Location
from Fill import fill_restrictive, sweep_from_pool
from rule_builder.rules import And, Rule

from ..Options import LocalStart
from ..items.Items import NAME_TO_ITEM, Campaign, ProgressiveScenario
from ..locations.Campaigns import NAME_TO_CAMPAIGN
from ..locations.Locations import VICTORY_SCENARIO_LOCATIONS
from ..locations.Scenarios import CAMPAIGN_TO_SCENARIOS, Age2ScenarioData

if TYPE_CHECKING:
    from .. import Age2World

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


def probe_state(world: 'Age2World', base_state: CollectionState) -> CollectionState:
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
        function(state, base_state.multiworld)
    for function in CollectionState.additional_copy_functions:
        state = function(base_state, state)
    return state


def state_with(world: 'Age2World', base_state: CollectionState, item_names: list[str]) -> CollectionState:
    """base_state plus the named items, swept so events and follow-on access come with it."""
    state = probe_state(world, base_state)
    for name in item_names:
        state.collect(world.create_item(name), True)
    state.sweep_for_advancements(locations=world.multiworld.get_locations(world.player))
    return state


def relevant_candidates(target: Target, candidates: list[str]) -> list[str]:
    rule = target if isinstance(target, Rule.Resolved) else getattr(target, "access_rule", None)
    if not isinstance(rule, Rule.Resolved):
        return candidates
    depends_on = rule.item_dependencies().keys()
    return [name for name in candidates if name in depends_on]


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

    narrowed = relevant_candidates(target, chosen)
    if len(narrowed) < len(chosen) and satisfied(target, state_with(world, base_state, narrowed)):
        chosen = narrowed
    elif not satisfied(target, state_with(world, base_state, chosen)):
        return None

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
    return world.get_location(VICTORY_SCENARIO_LOCATIONS[scenario.scenario_name])


def win_items(world: 'Age2World', scenario: Age2ScenarioData) -> list[str] | None:
    """Items that make `scenario` beatable from turn one."""
    victory = victory_location(world, scenario)
    if victory is None:
        return None
    return solve(world, victory, world.multiworld.state, own_itempool_names(world))


def base_candidate_names(world: 'Age2World') -> list[str]:
    """Candidates for the Base solve: the itempool minus campaign progression."""
    excluded = (ProgressiveScenario, Campaign)
    return [
        name for name in own_itempool_names(world)
        if not isinstance(NAME_TO_ITEM[name].type, excluded)
    ]


def conjuncts(rule: Rule) -> list[Rule]:
    """Flatten a conjunction into the parts that must each hold on their own."""
    if isinstance(rule, And) and not rule.options:
        flattened: list[Rule] = []
        for child in rule.children:
            flattened.extend(conjuncts(child))
        return flattened
    return [rule]


def scenario_base_rule(world: 'Age2World', scenario: Age2ScenarioData) -> Rule | None:
    """The scenario's own has_base, or None when it can never hold."""
    starting_state = scenario.logic(world.rules.logic)
    has_base = starting_state.has_base
    if resolve(world, has_base).always_false:
        return None
    return has_base


def base_items(
    world: 'Age2World',
    scenario: Age2ScenarioData,
    granted: list[str] | None = None,
) -> list[str]:
    """Items that let the player build a town centre, plus anything extra `scenario` asks for."""
    logic = world.rules.logic
    target = logic.can_build_base()

    scenario_rule = scenario_base_rule(world, scenario)
    if scenario_rule is not None:
        target = target & scenario_rule

    base_state = state_with(world, world.multiworld.state, granted) if granted else world.multiworld.state
    candidates = base_candidate_names(world)
    needed: Counter[str] = Counter()
    reachable: list[Rule] = []
    for conjunct in conjuncts(target):
        resolved = resolve(world, conjunct)
        if resolved.always_true:
            # Asks for nothing, and leaving it out keeps the combined trim below small.
            # can_build_base() alone contributes four of these.
            continue
        solved = solve(world, resolved, base_state, candidates)
        if solved is None:
            continue
        reachable.append(conjunct)
        # Counts merge by the largest demand, not by summing across conjuncts.
        for name, count in Counter(solved).items():
            needed[name] = max(needed[name], count)

    if not reachable:
        return []

    # Conjuncts are solved apart, so each picks its own way to satisfy a shared
    # disjunction and the union ends up with redundant items. One pass over the
    # whole satisfiable target trims those back out.
    combined = reachable[0]
    for conjunct in reachable[1:]:
        combined = combined & conjunct
    trimmed = solve(world, resolve(world, combined), base_state, sorted(needed.elements()))
    return sorted(trimmed) if trimmed is not None else sorted(needed.elements())


def take_from_itempool(world: 'Age2World', names: list[str]) -> list[Item]:
    wanted = Counter(names)
    taken: list[Item] = []
    for item in list(world.multiworld.itempool):
        if item.player != world.player or wanted[item.name] <= 0:
            continue
        wanted[item.name] -= 1
        world.multiworld.itempool.remove(item)
        taken.append(item)
    missing = +wanted  # only the still-positive counts
    if missing:
        logging.warning("Local Start: %s not in the itempool, skipping: %s",
                        world.player_name, dict(missing))
    return taken


def place_locally(
    world: 'Age2World',
    items: list[Item],
    base_state: CollectionState,
    locations: list[Location],
    name: str,
) -> None:
    """Lock `items` into `locations`, reachable from `base_state`."""
    if not items:
        return
    fill_restrictive(
        world.multiworld, base_state, locations, items,
        single_player_placement=True, lock=True, allow_partial=False, name=name,
    )


def late_locations(world: 'Age2World') -> list[Location]:
    """This player's unfilled locations that are not reachable from turn one."""
    return [
        location for location in world.multiworld.get_unfilled_locations(world.player)
        if not location.can_reach(world.multiworld.state)
    ]


def remaining_pool_state(world: 'Age2World') -> CollectionState:
    """Everything else this multiworld still has to give."""
    return sweep_from_pool(world.multiworld.state, world.multiworld.itempool)


def local_start_sets(world: 'Age2World') -> tuple[list[str], list[str]]:
    """(win set, base set) for the chosen option value. Either may be empty."""
    option = world.options.local_start
    scenario = choose_start_scenario(world)
    if scenario is None:
        logging.warning("Local Start: %s has no starting campaign, nothing to place.",
                        world.player_name)
        return [], []

    win_set: list[str] = []
    if option in (LocalStart.option_guarantee_win_first_scenario, LocalStart.option_both):
        solved = win_items(world, scenario)
        if solved is None:
            logging.warning("Local Start: %s cannot be made beatable for %s from this pool.",
                            scenario.scenario_name, world.player_name)
        else:
            win_set = solved

    base_set: list[str] = []
    if option in (LocalStart.option_base, LocalStart.option_both):
        base_set = base_items(world, scenario, win_set)

    return win_set, base_set


def apply(world: 'Age2World') -> None:
    """Entry point from Age2World.pre_fill."""
    if world.options.local_start == LocalStart.option_no:
        return

    win_set, base_set = local_start_sets(world)
    if not win_set and not base_set:
        return

    # Both passes together, deduped: an item wanted by each is placed once, under the
    # stricter of the two reach requirements.
    base_only = list((Counter(base_set) - Counter(win_set)).elements())

    logging.info("Local Start: %s placing win=%s base=%s",
                 world.player_name, sorted(win_set), sorted(base_only))

    # Win first, against precollected only, so the set really is obtainable from turn one.
    place_locally(world, take_from_itempool(world, win_set), world.multiworld.state,
                  world.multiworld.get_unfilled_locations(world.player),
                  "Age2 Local Start (win)")
    # Then base: own slot, any valid position, but never sphere one.
    place_locally(world, take_from_itempool(world, base_only), remaining_pool_state(world),
                  late_locations(world),
                  "Age2 Local Start (base)")
