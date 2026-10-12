"""The root view: each route to a location, and per campaign, where along it each chapter stands."""
from __future__ import annotations

import enum
import functools
from typing import TYPE_CHECKING, Callable

from BaseClasses import CollectionState
from NetUtils import JSONMessagePart
from rule_builder.rules import Rule

from ..generation.pools.BudgetPool import SAMPLED_RESOURCES
from ..logic.budget.BudgetItem import for_location
from ..logic.budget.BudgetTotal import BudgetTotal
from .Costs import Costs, budget_label
from .Layout import BUDGETED_ITEMS, Lines, _ranges, colored, text, truth
from .Lookup import _BY_NAME, find
from .Routes import Route, age_name, any_building_item, building_names, routes_for

if TYPE_CHECKING:
    from .. import Age2World
    from ..logic.ScenarioLogic import ScenarioLogic


class Status(enum.IntEnum):
    """Where a chapter stands on a route, best first; the first part that fails decides it."""
    AVAILABLE = 0
    CANT_AFFORD = 1
    SHORT = 2
    """Missing items: something still to come would open it."""
    LOCKED = 3
    NEVER = 4
    """Not even every item in the pool opens it: "can't build" for good."""


class Explainer:
    def __init__(self, world: Age2World) -> None:
        self.world = world
        self._entries: list[tuple[str, Callable[[CollectionState], Lines]]] = []
        """What the last explanation's [/explain_more N] markers open, by N - 1."""

    def explain_rule(self, typed: str, state: CollectionState) -> list[JSONMessagePart] | None:
        if typed.strip().lower() == BUDGETED_ITEMS.lower():
            self._entries = []
            return self._budgeted_items(state).parts()
        found = find(self.world, typed)
        if found is None:
            return None
        name, data = found
        location = self.world.multiworld.get_location(name, self.world.player)
        self._entries = []

        lines = Lines()
        lines.add(0, text(f"{name} -> "), truth(location.can_reach(state)))
        for route in routes_for(self.world, data):
            self._route(lines, name, route, state)
        return lines.parts()

    def _budgeted_items(self, state: CollectionState) -> Lines:
        """The seed's sample in its one drawn order. Every scenario buys what it has of it age by
        age, in this order within an age, after its own purchases and its base. An age leads its
        own: every item of it asks the scenario to reach it, so its order puts the age-up first. An item no
        included scenario budgets is left out. Each reads as the budget words it, green where it
        is in logic, with its own price and its costs view to open."""
        budget = self.world.pool.budget
        ordered = sorted((location for location in budget.entries if self._budgeted_anywhere(location)),
                         key=lambda location: (for_location(location).age, location is not for_location(location).age,
                                                budget.rank[location]))
        lines = Lines()
        lines.add(0, text(f"{BUDGETED_ITEMS}: {len(ordered)}, bought age by age in this order"))
        age = None
        for number, location in enumerate(ordered, start=1):
            entry_age = for_location(location).age
            if entry_age is not age:
                age = entry_age
                lines.add(1, text(age_name(age)))
            name = location.location_name
            reached = self.world.multiworld.get_location(name, self.world.player).can_reach(state)
            route = self._priced_route(location)
            parts = [text(f"{number}. "), colored(budget_label(location), reached)]
            if route is not None:
                price = ", ".join(f"{route.price[1][resource]} {resource.name.lower()}"
                                  for resource in SAMPLED_RESOURCES if route.price[1].get(resource, 0) > 0)
                parts += [text(f" ({price})" if price else " (free)"),
                          self._entry(f"what {name} costs",
                                      lambda st, name=name, route=route: self._costs_view(name, route, st))]
            lines.add(2, *parts)
        return lines

    def _budgeted_anywhere(self, location) -> bool:
        route = self._priced_route(location)
        if route is None:
            return False
        easily = tuple(sorted((resource for resource, amount in route.price[1].items() if amount > 0),
                              key=lambda resource: resource.value))
        return any(isinstance(BudgetTotal(scenario=scenario, location=location, easily=easily).resolve(self.world),
                              BudgetTotal.Resolved)
                   for scenario in self.world.pool.scenarios.included)

    def _priced_route(self, location) -> Route | None:
        return next((route for route in routes_for(self.world, _BY_NAME[location.location_name])
                     if route.price is not None), None)

    def _costs_view(self, name: str, route: Route, state: CollectionState) -> Lines:
        """The same costs view as under the location's own /explain."""
        offering = [self.world.rules.logic.for_scenario(scenario)
                    for campaign in self.world.pool.campaigns.enabled
                    for scenario in self.world.pool.scenarios.in_campaign(campaign)
                    if self._status(route, scenario, state) is not None]
        return Costs(self.world, route, offering).drill(name, state, self._entry)

    def explain_more(self, argument: str, state: CollectionState) -> list[JSONMessagePart]:
        """The entry behind a [/explain_more N] marker of the last explanation."""
        if not self._entries:
            return [text("Nothing to explain more - run /explain on a location first.")]
        if argument.strip().isdigit() and 1 <= int(argument) <= len(self._entries):
            _, build = self._entries[int(argument) - 1]
            return build(state).parts()
        lines = Lines()
        lines.add(0, text("Explain more of the last /explain with:"))
        for index, (title, _) in enumerate(self._entries, start=1):
            lines.add(1, text(f"/explain_more {index} - {title}"))
        return lines.parts()

    def _entry(self, title: str, build: Callable[[CollectionState], Lines]) -> JSONMessagePart:
        """Keep a drill-down for the last explanation, and the marker that opens it. A drill-down
        opened twice keeps the numbers it gave its own drill-downs the first time."""
        for index, (kept, _) in enumerate(self._entries, start=1):
            if kept == title:
                return text(f"  [/explain_more {index}]")
        self._entries.append((title, build))
        return text(f"  [/explain_more {len(self._entries)}]")

    # -- one route ----------------------------------------------------------------------------

    def _route(self, lines: Lines, name: str, route: Route, state: CollectionState) -> None:
        campaigns = []
        offering: list[ScenarioLogic] = []
        unlocked: list[ScenarioLogic] = []
        for campaign in self.world.pool.campaigns.enabled:
            chapters = []
            for scenario in self.world.pool.scenarios.in_campaign(campaign):
                status = self._status(route, scenario, state)
                if status is None:
                    continue
                chapters.append((scenario.chapter, status))
                sl = self.world.rules.logic.for_scenario(scenario)
                offering.append(sl)
                if status is not Status.LOCKED:
                    unlocked.append(sl)
            if chapters:
                campaigns.append((campaign, chapters))
        if not campaigns:
            return   # no scenario offers it

        lines.add(1, *self._label(route, state))
        required = self._requirements(route.requires, state)
        costs = Costs(self.world, route, offering) if route.price is not None else None
        if costs is not None and not costs.cost:
            costs = None   # free
        if required or costs is not None:
            lines.add(2, text("Requires"))
            for line in required:
                lines.add(3, *line)
                if route.upgrade is not None and line[0]["text"] == f"Has {route.upgrade.item.item_name}":
                    self._started_researched(lines, route, campaigns)
            if costs is not None:
                lines.add(3, *costs.line(state, unlocked),
                          self._entry(f"what {name} costs",
                                      lambda st: costs.drill(name, st, self._entry)))
        for campaign, chapters in campaigns:
            every = len(self.world.pool.scenarios.in_campaign(campaign))
            lines.add_segments(2, f"{campaign.campaign_name}: ", self._runs(route, chapters, every))

    def _started_researched(self, lines: Lines, route: Route, campaigns: list) -> None:
        """The chapters that research the upgrade for themselves, so never ask for its item:
        "Attila the Hun 2–6: Starts Researched"."""
        for campaign, chapters in campaigns:
            started = [chapter for chapter, _ in chapters
                       if self.world.rules.logic.for_scenario(self._scenario(campaign, chapter))
                       .techs.researched_at_start(route.upgrade)]
            if started:
                lines.add(4, colored(f"{campaign.campaign_name} {_ranges(started)}: Starts Researched", False))

    def _scenario(self, campaign, chapter: int):
        return next(scenario for scenario in self.world.pool.scenarios.in_campaign(campaign)
                    if scenario.chapter == chapter)

    def _label(self, route: Route, state: CollectionState) -> list[JSONMessagePart]:
        """"Trains it at the Stable in the Feudal Age", the building and age green where their
        items are held."""
        parts = [text(route.action)]
        if route.at:
            held = self._holds(any_building_item(self.world, route.at), state)
            parts += [text(" at the "), colored(building_names(route.at), held)]
        if route.age is not None:
            held = self._holds(self.world.rules.logic.ages.has_age(route.age), state)
            parts += [text(" in the "), colored(age_name(route.age), held)]
        return parts

    def _status(self, route: Route, scenario, state: CollectionState) -> Status | None:
        """Where the scenario stands on the route, or None if it doesn't offer it."""
        sl = self.world.rules.logic.for_scenario(scenario)
        ways = [way for way in route.ways(sl)
                if way.structural is None or not self._resolved(way.structural).always_false]
        if not ways:
            return None
        if not self._ever(route, ways):
            return Status.NEVER
        if not self._holds(sl.is_unlocked(), state):
            return Status.LOCKED
        if not all(self._holds(rule, state) for rule in route.gates):
            return Status.SHORT   # item rules outside the scenario's own check
        best = Status.SHORT
        for way in ways:
            if way.structural is not None and not self._holds(way.structural, state):
                continue
            if way.payment is not None and not self._holds(way.payment, state):
                best = min(best, Status.CANT_AFFORD)
                continue
            return Status.AVAILABLE
        return best

    def _runs(self, route: Route, chapters: list[tuple[int, Status]],
              every: int) -> list[list[JSONMessagePart]]:
        """Each status once, with the chapters that have it as runs: "1, 3–5 locked". A campaign
        whose every chapter is on the route and locked is just "locked"."""
        if len(chapters) == every and all(status is Status.LOCKED for _, status in chapters):
            return [[text("locked")]]
        by_status: dict[Status, list[int]] = {}
        for chapter, status in chapters:
            by_status.setdefault(status, []).append(chapter)
        ordered = sorted(by_status.items(), key=lambda item: item[1][0])
        return [[text(f"{_ranges(numbers)} "), self._word(route, status)]
                for status, numbers in ordered]

    @staticmethod
    def _word(route: Route, status: Status) -> JSONMessagePart:
        if status is Status.AVAILABLE:
            return colored("available", True)
        if status is Status.CANT_AFFORD:
            return colored("can't afford", False)
        if status is Status.SHORT:
            return colored("missing items", False)
        if status is Status.NEVER:
            return colored(route.verb, False)
        return text("locked")

    # -- general requirements --------------------------------------------------------------------

    def _requirements(self, rules: tuple[Rule, ...],
                      state: CollectionState) -> list[list[JSONMessagePart]]:
        """One line an item, "Has Militia Line -> True"; an "any of" shares one line,
        "Has Castle or Krepost -> False". An item asked twice is listed once."""
        lines: list[list[JSONMessagePart]] = []
        seen: set[str] = set()
        for rule in rules:
            resolved = self._resolved(rule)
            if resolved.always_true:
                continue
            names = sorted(set(resolved.item_dependencies()) - seen)
            if not names:
                continue
            seen.update(names)
            if len(names) > 1 and type(resolved).__qualname__.startswith(("HasAny", "Or")):
                held = resolved(state)
                lines.append([colored("Has " + " or ".join(names), held), text(" -> "), truth(held)])
                continue
            for name in names:
                held = state.has(name, self.world.player)
                lines.append([colored(f"Has {name}", held), text(" -> "), truth(held)])
        return lines

    # -- evaluating -----------------------------------------------------------------------------

    @functools.cached_property
    def _everything(self) -> CollectionState:
        """Every item the pool holds: what no item still to come can add to."""
        return self.world.multiworld.get_all_state()

    def _ever(self, route: Route, ways: list) -> bool:
        """Whether every item in the pool would open one of the ways."""
        everything = self._everything
        return (all(self._holds(rule, everything) for rule in route.gates)
                and any(way.structural is None or self._holds(way.structural, everything)
                        for way in ways))

    def _resolved(self, rule: Rule) -> Rule.Resolved:
        return rule.resolve(self.world)

    def _holds(self, rule: Rule, state: CollectionState) -> bool:
        return self._resolved(rule)(state)
