"""The root view: each route to a location, and per campaign, where along it each chapter stands."""
from __future__ import annotations

import enum
import functools
from typing import TYPE_CHECKING, Callable

from BaseClasses import CollectionState
from NetUtils import JSONMessagePart
from rule_builder.rules import And, Has, HasAll, HasAllCounts, HasAny, Or, Rule

from ..generation.pools.BudgetPool import SAMPLED_RESOURCES
from ..logic.budget.BudgetItem import for_location
from ..logic.budget.BudgetTotal import BudgetTotal
from ..locations.Campaigns import Age2CampaignData
from ..locations.Scenarios import Age2ScenarioData
from ..logic.custom_logic.AgeUpRequirement import AgeUpRequirement
from ..logic.custom_logic.ScenarioQuestions import ScenarioQuestion
from ..logic.custom_logic.SufficientRawResources import SufficientRawResources
from .Costs import Costs, budget_label
from .Layout import BUDGETED_ITEMS, Lines, _ranges, colored, text, truth
from .Lookup import _BY_NAME, find
from .Routes import Route, age_name, any_building_item, building_names, routes_for

if TYPE_CHECKING:
    from .. import Age2World
    from ..logic.ScenarioLogic import ScenarioLogic


OPENED = 2
"""How many scenario questions deep a failing chapter's breakdown opens."""


def _distinct(children: tuple[Rule.Resolved, ...]) -> list[Rule.Resolved]:
    """The children, each once: the same rule asked twice side by side is one line."""
    seen: set = set()
    kept = []
    for child in children:
        key = child.explain_str()
        if key not in seen:
            seen.add(key)
            kept.append(child)
    return kept


def _signature(lines: Lines) -> tuple:
    """What a block shows, markers aside: two chapters showing the same are one."""
    return tuple((depth, tuple((part["text"], part.get("color")) for part in parts
                               if not part["text"].startswith("  [/explain_more")))
                 for depth, parts in lines._lines)


def _joined(groups: list[list[JSONMessagePart]], word: str) -> list[JSONMessagePart]:
    """The groups of parts one after another, `word` between them."""
    parts: list[JSONMessagePart] = []
    for index, group in enumerate(groups):
        if index:
            parts.append(text(word))
        parts += group
    return parts


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
        self._dry = False
        """While set, markers are drawn but nothing is kept: a block rendered only to compare it."""
        """What the last explanation's [/explain_more N] markers open, by N - 1."""

    def explain_rule(self, typed: str, state: CollectionState) -> list[JSONMessagePart] | None:
        if typed.strip().lower() == BUDGETED_ITEMS.lower():
            self._entries = []
            return self._budgeted_items(state).parts()
        scoped = self._scoped(typed)
        if scoped is not None:
            return scoped(state)
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

    # -- moving straight to a branch ------------------------------------------------------------

    def _scopes(self) -> list[tuple[str, object, object]]:
        """What may lead a command, longest first: each campaign by name and by its first word,
        each scenario by name and as "<campaign word> <chapter>" - every one the game has, so one
        this seed left out is told so rather than handed to UT."""
        scopes: list[tuple[str, object, object]] = []
        for campaign in Age2CampaignData:
            word = campaign.campaign_name.split()[0]
            scopes += [(campaign.campaign_name.lower(), campaign, None), (word.lower(), campaign, None)]
            for scenario in (each for each in Age2ScenarioData if each.campaign is campaign):
                scopes += [(scenario.scenario_name.lower(), campaign, scenario),
                           (f"{word} {scenario.chapter}".lower(), campaign, scenario)]
        return sorted(scopes, key=lambda scope: -len(scope[0]))

    def _scoped(self, typed: str) -> Callable[[CollectionState], list[JSONMessagePart]] | None:
        """"[campaign or scenario] [Costs] <location>": None when it leads with neither, so the
        plain explanation - or UT's own - takes it. "The Scourge of God: Victory" is a scenario's
        own location, not a scope."""
        rest, campaign, scenario = typed.strip(), None, None
        for words, each_campaign, each_scenario in self._scopes():
            if rest.lower().startswith(words + " "):
                rest, campaign, scenario = rest[len(words):].strip(), each_campaign, each_scenario
                break
        costs = rest.lower().startswith("costs ")
        if costs:
            rest = rest[len("costs "):].strip()
        if campaign is None and not costs:
            return None
        if campaign is not None and campaign not in self.world.pool.campaigns.enabled:
            return lambda state: [text(f"{campaign.campaign_name} isn't in this seed.")]
        if scenario is not None and scenario not in self.world.pool.scenarios.included:
            return lambda state: [text(f"{scenario.scenario_name} isn't in this seed.")]
        found = find(self.world, rest)
        if found is None:
            return lambda state: [text(f"No location here matches \"{rest}\".")]
        name, data = found

        def explained(state: CollectionState) -> list[JSONMessagePart]:
            self._entries = []
            return self._branch(name, data, campaign, scenario, costs, state).parts()
        return explained

    def _branch(self, name: str, data, campaign, scenario, costs: bool, state: CollectionState) -> Lines:
        routes = routes_for(self.world, data)
        if costs:
            route = next((route for route in routes if route.price is not None), None)
            if route is None:
                lines = Lines()
                lines.add(0, text(f"{name} costs nothing."))
                return lines
            if campaign is None:
                return self._costs_view(name, route, state)
            offering = [self.world.rules.logic.for_scenario(each)
                        for each in self.world.pool.scenarios.in_campaign(campaign)
                        if self._status(route, each, state) is not None]
            chapters = (scenario.chapter,) if scenario is not None else None
            return Costs(self.world, route, offering).campaign_budget(name, campaign.campaign_name, state, chapters)
        lines = Lines()
        if scenario is None:
            for route in routes:
                if any(self._status(route, each, state) is not None
                       for each in self.world.pool.scenarios.in_campaign(campaign)):
                    lines.extend(self._campaign_drill(name, route, campaign, state))
        else:
            lines.add(0, text(f"{name} in "), colored(f"{scenario.scenario_name} ({campaign.campaign_name} "
                                                      f"{scenario.chapter})",
                                                      self._holds(self.world.rules.logic.for_scenario(scenario)
                                                                  .is_unlocked(), state)))
            for route in routes:
                self._chapter(lines, name, route, scenario, self._label(route, state), state)
        if not lines._lines:
            where = scenario.scenario_name if scenario is not None else campaign.campaign_name
            lines.add(0, text(f"Nothing in {where} offers {name}."))
        return lines

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
        if self._dry:
            return text("  [/explain_more]")
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
            for index, (numbers, parts) in enumerate(self._runs(route, chapters, every)):
                marker = self._entry(f"{name}: {route.label} in {campaign.campaign_name} {_ranges(numbers)}",
                                     lambda st, route=route, campaign=campaign, numbers=tuple(numbers):
                                         self._campaign_drill(name, route, campaign, st, numbers))
                if index:
                    lines.add(3, *parts, marker)
                else:
                    lines.add(2, text(f"{campaign.campaign_name}: "), *parts, marker)

    # -- one campaign on one route -----------------------------------------------------------------

    def _campaign_drill(self, name: str, route: Route, campaign, state: CollectionState,
                        chapters: tuple[int, ...] | None = None) -> Lines:
        """Each chapter offering the route - of `chapters`, where given - with its status and why."""
        lines = Lines()
        which = f" {_ranges(list(chapters))}" if chapters is not None else ""
        lines.add(0, text(f"{name}: "), *self._label(route, state), text(f" in {campaign.campaign_name}{which}"))
        groups: dict[tuple, list[ScenarioLogic]] = {}
        for scenario in self.world.pool.scenarios.in_campaign(campaign):
            if chapters is not None and scenario.chapter not in chapters:
                continue
            status = self._status(route, scenario, state)
            if status is None:
                continue
            sl = self.world.rules.logic.for_scenario(scenario)
            self._dry = True
            try:
                body = self._body(name, route, sl, [sl], state)
            finally:
                self._dry = False
            groups.setdefault((status, _signature(body)), []).append(sl)
        for (status, _), together in groups.items():
            head = _joined([[colored(f"{sl.scenario.chapter}. {sl.scenario.scenario_name}",
                                     self._holds(sl.is_unlocked(), state))] for sl in together], ", ")
            lines.add(1, *head, text(": "), self._word(route, status))
            if status is Status.LOCKED:
                for sl in together:   # each chapter is unlocked by its own items
                    start = len(lines._lines)
                    self._breakdown(lines, sl.is_unlocked(), 2, sl, state, OPENED)
                    if len(together) > 1 and len(lines._lines) > start:
                        depth, first = lines._lines[start]
                        lines._lines[start] = (depth, [text(f"{sl.scenario.chapter}: "), *first])
            lines.extend(self._body(name, route, together[0], together, state))
        return lines

    def _body(self, name: str, route: Route, sl: ScenarioLogic, together: list[ScenarioLogic],
              state: CollectionState) -> Lines:
        """What a chapter asks on the route, past its unlock: the route's items, then what pays each
        resource, with the budget of every chapter in `together`."""
        lines = Lines()
        ways = [way.structural for way in route.ways(sl) if way.structural is not None]
        for rule in (*route.gates, *(ways[:1] if len(ways) == 1 else [Or(*ways)] if ways else [])):
            self._breakdown(lines, rule, 2, sl, state, OPENED)
        self._short_of(lines, name, route, sl, state, together)
        return lines

    def _chapter(self, lines: Lines, name: str, route: Route, scenario, head: list[JSONMessagePart],
                 state: CollectionState) -> None:
        """One scenario on one route: its status, then everything it asks, green where held - the
        unlock while locked, the route's items, and what pays each resource. Nothing where the
        scenario doesn't offer the route."""
        status = self._status(route, scenario, state)
        if status is None:
            return
        sl = self.world.rules.logic.for_scenario(scenario)
        lines.add(1, *head, text(": "), self._word(route, status))
        if status is Status.LOCKED:
            self._breakdown(lines, sl.is_unlocked(), 2, sl, state, OPENED)
        lines.extend(self._body(name, route, sl, [sl], state))

    def _breakdown(self, lines: Lines, rule: Rule | Rule.Resolved, depth: int, sl: ScenarioLogic,
                   state: CollectionState, opening: int, choice: bool = False) -> None:
        """The rule a part a line, green where it holds: an "and" as its parts side by side, an "or"
        of items as one line and any other "or" as its choices under "Any of", a scenario question
        by what it asks - opened into its own parts `opening` levels deep, held or not, so the
        player sees why it holds as well as why it doesn't; deeper ones get a marker instead. An
        "and" that is one `choice` among others keeps its parts together under "All of"."""
        resolved = rule if isinstance(rule, Rule.Resolved) else self._resolved(rule)
        if resolved.always_true:
            return
        held = resolved(state)
        own = f"{sl.scenario.scenario_name}: "
        if isinstance(resolved, ScenarioQuestion.Resolved):
            if opening:
                lines.add(depth, colored(self._asks(resolved, sl), held))
                self._breakdown(lines, resolved.answer, depth + 1, sl, state, opening - 1)
            else:
                lines.add(depth, colored(self._asks(resolved, sl), held), self._question_entry(resolved, sl))
            return
        if isinstance(resolved, And.Resolved):
            if choice:
                lines.add(depth, colored("All of", held))
                depth += 1
            for child in _distinct(resolved.children):
                self._breakdown(lines, child, depth, sl, state, opening)
            return
        if isinstance(resolved, Or.Resolved):
            names = [self._item_parts(child, own, state) for child in resolved.children]
            if all(names):
                lines.add(depth, text("Has "), *_joined(names, " or "))
                return
            if all(name or isinstance(child, ScenarioQuestion.Resolved)
                   for child, name in zip(resolved.children, names)):
                parts: list[JSONMessagePart] = []
                for index, (child, name) in enumerate(zip(resolved.children, names)):
                    if index:
                        parts.append(text(", or "))
                    parts += [text("has "), *name] if name else [colored(self._asks(child, sl), child(state))]
                parts[0] = {**parts[0], "text": parts[0]["text"][:1].upper() + parts[0]["text"][1:]}
                lines.add(depth, *parts, *(self._question_entry(child, sl) for child in resolved.children
                                           if isinstance(child, ScenarioQuestion.Resolved)))
                return
            lines.add(depth, colored("Any of", held))
            for child in self._why(_distinct(resolved.children), held, lines, depth + 1, state):
                self._breakdown(lines, child, depth + 1, sl, state, opening, choice=True)
            return
        if isinstance(resolved, BudgetTotal.Resolved):
            lines.add(depth, colored(f"Budget for {budget_label(resolved.location)}", held))
            return
        if isinstance(resolved, SufficientRawResources.Resolved):
            lines.add(depth, colored(f"{resolved.needed} worth of", held))
            shown = self._why(list(resolved.children), held, lines, depth + 1, state)
            for child, amount in zip(resolved.children, resolved.amounts):
                if child not in shown:
                    continue
                start = len(lines._lines)
                self._breakdown(lines, child, depth + 1, sl, state, opening, choice=True)
                if len(lines._lines) > start:   # the source's first line carries what it is worth
                    first_depth, first = lines._lines[start]
                    lines._lines[start] = (first_depth, [text(f"{amount} from "), *first])
            return
        if isinstance(resolved, AgeUpRequirement.Resolved):
            lines.add(depth, colored(f"Any {resolved.num_needed} of", held))
            for child in self._why(list(resolved.pairs), held, lines, depth + 1, state):
                self._breakdown(lines, child, depth + 1, sl, state, opening, choice=True)
            if resolved.has_single:
                lines.add(depth, colored("Or by itself", held))
                self._breakdown(lines, resolved.children[-1], depth + 1, sl, state, opening, choice=True)
            return
        if resolved.always_false:
            lines.add(depth, colored("Never", False))
            return
        named = self._item_parts(resolved, own, state)
        if named:
            lines.add(depth, text("Has "), *named)
        else:
            lines.add(depth, colored(resolved.explain_str(state), held))

    def _item_parts(self, rule: Rule.Resolved, own: str,
                    state: CollectionState) -> list[JSONMessagePart] | None:
        """An item rule as its items, each green where held: "Builder and Castle", "Attila's Camp
        or Bleda's Camp"; a counted one says how many are held, "Progressive Attila Scenario x2
        Has x1". None for anything else. A scenario's own items lose its name."""
        def item(name: str, count: int = 1) -> list[JSONMessagePart]:
            held = state.count(name, self.world.player)
            shown = name.split(own, 1)[-1] + (f" x{count}" if count > 1 else "")
            parts = [colored(shown, held >= count)]
            if count > 1:
                parts += [text(" "), colored(f"Has x{held}", held > 0)]
            return parts
        if isinstance(rule, Has.Resolved):
            return item(rule.item_name, rule.count)
        if isinstance(rule, HasAll.Resolved):
            return _joined([item(name) for name in rule.item_names], " and ")
        if isinstance(rule, HasAny.Resolved):
            return _joined([item(name) for name in rule.item_names], " or ")
        if isinstance(rule, HasAllCounts.Resolved):
            return _joined([item(name, count) for name, count in rule.item_counts], " and ")
        return None

    @staticmethod
    def _why(choices: list[Rule.Resolved], held: bool, lines: Lines, depth: int,
             state: CollectionState) -> list[Rule.Resolved]:
        """The choices worth showing: where the whole holds, only those that hold - why it does -
        with a line for how many others there are; where it fails, every one, as any could open it."""
        if not held:
            return choices
        holding = [choice for choice in choices if choice(state)]
        others = len(choices) - len(holding)
        if others:
            lines.add(depth, text(f"({others} other way{'s' if others > 1 else ''} not held)"))
        return holding

    def _question_entry(self, question: ScenarioQuestion.Resolved, sl: ScenarioLogic) -> JSONMessagePart:
        """The marker that opens a scenario question not opened in place."""
        return self._entry(f"{sl.scenario.scenario_name}: {self._asks(question, sl)}",
                           lambda st: self._question_drill(question, sl, st))

    def _question_drill(self, question: ScenarioQuestion.Resolved, sl: ScenarioLogic,
                        state: CollectionState) -> Lines:
        """One scenario question broken down, as a failing one is in place."""
        lines = Lines()
        lines.add(0, colored(sl.scenario.scenario_name, self._holds(sl.is_unlocked(), state)), text(": "),
                  colored(self._asks(question, sl), question(state)))
        self._breakdown(lines, question.answer, 1, sl, state, OPENED)
        return lines

    @staticmethod
    def _asks(question: ScenarioQuestion.Resolved, sl: ScenarioLogic) -> str:
        """"Can build a Castle": the question without its scenario, which the chapter line names."""
        asks = question.description.removeprefix(f"{sl.scenario.scenario_name} ")
        return asks[:1].upper() + asks[1:]

    def _short_of(self, lines: Lines, name: str, route: Route, sl: ScenarioLogic,
                  state: CollectionState, together: list[ScenarioLogic] | None = None) -> None:
        """Each resource the price asks: paid by an easy source, by the budget, or by neither yet."""
        if route.price is None:
            return
        costs = Costs(self.world, route, [sl])
        pile, most = costs._pile(state), self.world.rules.logic.most_pile
        total = costs._budget(sl)
        for resource, amount in costs.cost:
            noun = resource.name.lower()
            easy = self._resolved(sl.economy.has_easy_source(resource))
            why = (self._question_entry(easy, sl),) if isinstance(easy, ScenarioQuestion.Resolved) else ()
            if easy(state):
                lines.add(2, colored(f"{amount} {noun}", True), text(": an easy source"), *why)
                continue
            asked = dict(total.table.total(state).cost).get(resource, 0) if total is not None else None
            if asked is None or total.lowest(resource) > most[resource]:
                lines.add(2, colored(f"{amount} {noun}", False), text(": not in budget, and no easy source yet"), *why)
                continue
            lines.add(2, colored(f"{amount} {noun}", pile[resource] >= asked),
                      text(f": budget {asked}, starting pile {pile[resource]}, no easy source yet"), *why)
        if total is not None:
            # The budget pays for what comes before it too, so it can fail on what it doesn't cost.
            own = {resource for resource, _ in costs.cost}
            for resource, asked in total.table.total(state).cost:
                if resource in own:
                    continue
                noun = resource.name.lower()
                easy = self._resolved(sl.economy.has_easy_source(resource))
                why = (self._question_entry(easy, sl),) if isinstance(easy, ScenarioQuestion.Resolved) else ()
                if easy(state):
                    lines.add(2, colored(f"{asked} {noun}", True), text(" in its budget: an easy source"), *why)
                elif total.lowest(resource) > most[resource]:
                    lines.add(2, colored(f"{asked} {noun}", False),
                              text(" in its budget: more than any starting pile, no easy source yet"), *why)
                else:
                    lines.add(2, colored(f"{asked} {noun}", pile[resource] >= asked),
                              text(f" in its budget: starting pile {pile[resource]}, no easy source yet"), *why)
            together = together or [sl]
            campaign = sl.scenario.campaign.campaign_name
            chapters = tuple(each.scenario.chapter for each in together)
            budgets = Costs(self.world, route, together)
            lines.add(2, text("Its budget"),
                      self._entry(f"{name}'s budget in {campaign} {_ranges(list(chapters))}",
                                  lambda st: budgets.campaign_budget(name, campaign, st, chapters)))

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
              every: int) -> list[tuple[list[int], list[JSONMessagePart]]]:
        """Each status once, a row each, with the chapters that have it as runs: "1, 3–5 locked".
        A campaign whose every chapter is on the route and locked is just "locked"."""
        if len(chapters) == every and all(status is Status.LOCKED for _, status in chapters):
            return [([chapter for chapter, _ in chapters], [text("locked")])]
        by_status: dict[Status, list[int]] = {}
        for chapter, status in chapters:
            by_status.setdefault(status, []).append(chapter)
        ordered = sorted(by_status.items(), key=lambda item: item[1][0])
        return [(numbers, [text(f"{_ranges(numbers)} "), self._word(route, status)])
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
