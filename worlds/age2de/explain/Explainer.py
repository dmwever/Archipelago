"""The root view: each route to a location, and per campaign, where along it each chapter stands."""
from __future__ import annotations

import enum
import functools
import re
from typing import TYPE_CHECKING, Callable

from BaseClasses import CollectionState
from NetUtils import JSONMessagePart
from rule_builder.rules import And, Has, HasAll, HasAllCounts, HasAny, Or, Rule

from ..generation.pools.BudgetPool import SAMPLED_RESOURCES
from ..items.Items import Age2ItemData, Campaign, Resource
from ..logic.budget.BudgetItem import for_location
from ..logic.budget.BudgetTotal import BudgetTotal
from ..locations.Campaigns import Age2CampaignData
from ..locations.Scenarios import Age2ScenarioData
from ..logic.custom_logic.AgeUpRequirement import AgeUpRequirement
from ..logic.custom_logic.ScenarioQuestions import ScenarioQuestion
from ..logic.custom_logic.SufficientRawResources import SufficientRawResources
from .Costs import Costs, budget_label
from .Layout import BUDGETED_ITEMS, INDENT, WIDTH, Lines, _ranges, colored, text, truth
from .Lookup import _BY_NAME, find
from .Routes import Route, age_name, any_building_item, building_names, routes_for

if TYPE_CHECKING:
    from .. import Age2World
    from ..logic.ScenarioLogic import ScenarioLogic


_EASY_SOURCE = re.compile(r"easy (wood|food|gold|stone)(?: source)?")
"""What /explain takes for an easy source rather than a location."""

_AREAS = {"base": "in base", "open": "in the open", "ally": "with an ally", "enemy": "in enemy territory"}
"""How each map area reads after an amount: "3900 food (in base) from"."""

_SOURCE_NAMES = {
    "hunt_count": "Hunting", "herd_count": "Herding", "bush_count": "Foraging",
    "shore_fish_count": "Shore Fishing", "deep_fish_count": "Deep-Sea Fishing",
    "gold_count": "Gold Mining", "oyster_count": "Oyster Gathering", "whale_count": "Whaling",
    "stone_count": "Stone Quarrying",
}
"""What a source that is more than one question is called, by the map count it gathers."""

OPENED = 1
"""How deep a breakdown opens in place: the question being explained, with every question beneath
it - "Can build a Mill", "Has reached the Feudal Age" - one line with its marker."""

LOOPED = 50
"""The depth a question asked inside itself counts as where the loop closes: deeper than any tree."""

_GROUPS = (And.Resolved, Or.Resolved, SufficientRawResources.Resolved, AgeUpRequirement.Resolved)
"""The rules drawn as a group of parts beneath them; anything else is one line."""


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


def _says(held: bool) -> list[JSONMessagePart]:
    """How every line that states something ends: "-> True" or "-> False"."""
    return [text(" -> "), truth(held)]


def _campaign_item(campaign: Age2CampaignData) -> str:
    """The item that opens a campaign: "Attila the Hun Campaign"."""
    return next(item.item_name for item in Age2ItemData
                if isinstance(item.type, Campaign) and item.type.vanilla_campaign is campaign)


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
        """What the last explanation's [/explain_more N] markers open, by N - 1."""
        self._opened: set[str] = set()
        """The questions already opened in the block being drawn: a later mention is one line."""
        self._depths: dict[int, int] = {}
        """Each resolved part's depth, by identity: resolved rules live as long as the world."""
        self._dry = False
        """While set, markers are drawn but nothing is kept: a block rendered only to compare it."""

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
        easy = _EASY_SOURCE.fullmatch(rest.lower())
        if campaign is None and not costs and easy is None:
            return None
        if campaign is not None and campaign not in self.world.pool.campaigns.enabled:
            return lambda state: [text(f"{campaign.campaign_name} isn't in this seed.")]
        if scenario is not None and scenario not in self.world.pool.scenarios.included:
            return lambda state: [text(f"{scenario.scenario_name} isn't in this seed.")]
        if easy is not None:
            resource = Resource[easy.group(1).upper()]

            def eased(state: CollectionState) -> list[JSONMessagePart]:
                self._entries = []
                return self._easy_view(resource, campaign, scenario, state).parts()
            return eased
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

    # -- easy sources ---------------------------------------------------------------------------

    def _easy_view(self, resource: Resource, campaign, scenario, state: CollectionState,
                   chapters: tuple[int, ...] | None = None) -> Lines:
        """An easy source of the resource, laid out like a location: each campaign's item, then
        every chapter, True where it has one, each opening that scenario's easy source - or, for one
        scenario, that view straight away."""
        noun = f"Easy {resource.name.title()} Source"
        if scenario is not None:
            sl = self.world.rules.logic.for_scenario(scenario)
            return self._question_drill(self._resolved(sl.economy.has_easy_source(resource)), sl, state)
        lines = Lines()
        lines.add(0, text(noun))
        for each in self.world.pool.campaigns.enabled:
            if campaign is not None and each is not campaign:
                continue
            item = _campaign_item(each)
            held = state.has(item, self.world.player)
            lines.add(1, colored(f"Has {item}", held), *_says(held))
            for one in self.world.pool.scenarios.in_campaign(each):
                if chapters is not None and one.chapter not in chapters:
                    continue
                sl = self.world.rules.logic.for_scenario(one)
                question = self._resolved(sl.economy.has_easy_source(resource))
                has = question(state)
                lines.add(2, colored(f"{one.chapter}. {one.scenario_name}", has), *_says(has),
                          self._entry(f"{noun} in {one.scenario_name}",
                                      lambda st, question=question, sl=sl: self._question_drill(question, sl, st)))
        return lines

    def _question_body(self, question: ScenarioQuestion.Resolved, sl: ScenarioLogic,
                       state: CollectionState, depth: int = 1) -> Lines:
        lines = Lines()
        self._opened = {question.description}
        # The question itself is the level that opens: its answer is drawn, questions in it are not.
        self._breakdown(lines, question.answer, depth, sl, state, OPENED - 1)
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

        self._add_wrapped(lines, 1, [*self._label(route, state), *_says(
            any(status is Status.AVAILABLE for _, chapters in campaigns for _, status in chapters))])
        required = self._requirements(route.requires, state)
        costs = Costs(self.world, route, offering) if route.price is not None else None
        if costs is not None and not costs.cost:
            costs = None   # free
        if required or costs is not None:
            lines.add(2, text("Requires"))
            for nested, line in required:
                lines.add(3 + nested, *line)
                if route.upgrade is not None and line[0]["text"] == f"Has {route.upgrade.item.item_name}":
                    self._started_researched(lines, route, campaigns)
            if costs is not None:
                priced = costs.line(state, unlocked)
                lines.add(3, *priced, *_says(all(part.get("color") == "green" for part in priced
                                                  if part["type"] == "color")),
                          self._entry(f"what {name} costs",
                                      lambda st: costs.drill(name, st, self._entry)))
        for campaign, chapters in campaigns:
            item = _campaign_item(campaign)
            held = state.has(item, self.world.player)
            lines.add(2, colored(f"Has {item}", held), *_says(held))
            for chapter, status in chapters:
                sl = self.world.rules.logic.for_scenario(self._scenario(campaign, chapter))
                available = status is Status.AVAILABLE
                lines.add(3, colored(f"{chapter}. {sl.scenario.scenario_name}", available), *_says(available),
                          self._entry(f"{name}: {route.label} in {sl.scenario.scenario_name}",
                                      lambda st, route=route, sl=sl: self._scenario_route(name, route, sl, st)))

    # -- one campaign on one route -----------------------------------------------------------------

    def _scenario_route(self, name: str, route: Route, sl: ScenarioLogic, state: CollectionState) -> Lines:
        """One chapter on one route: the scenario level."""
        scenario = sl.scenario
        lines = Lines()
        lines.add(0, text(f"{name} in "), colored(f"{scenario.scenario_name} ({scenario.campaign.campaign_name} "
                                                  f"{scenario.chapter})", self._holds(sl.is_unlocked(), state)))
        self._chapter(lines, name, route, scenario, self._label(route, state), state)
        return lines

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
            lines.add(1, *head, *_says(status is Status.AVAILABLE))
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
        self._opened = set()
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
        lines.add(1, *head, *_says(status is Status.AVAILABLE))
        if status is Status.LOCKED:
            self._breakdown(lines, sl.is_unlocked(), 2, sl, state, OPENED)
        lines.extend(self._body(name, route, sl, [sl], state))

    def _breakdown(self, lines: Lines, rule: Rule | Rule.Resolved, depth: int, sl: ScenarioLogic,
                   state: CollectionState, opening: int, choice: bool = False) -> None:
        """The rule a part a line, each ending in whether it holds, shallowest parts first. Every
        "or" is an "Any of" and every "and" an "All of", a part a line beneath it - except the
        parts straight under a question or chapter, which are all asked by that line already. A
        scenario question opens into its own parts `opening` levels deep, held or not, so the
        player sees why it holds as well as why it doesn't; deeper ones, and one already opened in
        this block, get a marker instead."""
        resolved = rule if isinstance(rule, Rule.Resolved) else self._resolved(rule)
        if resolved.always_true:
            return
        held = resolved(state)
        own = f"{sl.scenario.scenario_name}: "
        if isinstance(resolved, ScenarioQuestion.Resolved):
            if opening and resolved.description not in self._opened:
                self._opened.add(resolved.description)
                lines.add(depth, colored(self._asks(resolved, sl), held), *_says(held))
                self._breakdown(lines, resolved.answer, depth + 1, sl, state, opening - 1)
            else:
                lines.add(depth, colored(self._asks(resolved, sl), held), *_says(held),
                          self._question_entry(resolved, sl))
            return
        items = self._items(resolved, own, state)
        if items is not None:
            every, each = items
            if len(each) == 1:
                lines.add(depth, text("Has "), *each[0][0], *_says(each[0][1]))
                return
            if every and not choice:
                for parts, has in each:
                    lines.add(depth, text("Has "), *parts, *_says(has))
                return
            lines.add(depth, colored("All of" if every else "Any of", held), *_says(held))
            for parts, has in each:
                lines.add(depth + 1, text("Has "), *parts, *_says(has))
            return
        if isinstance(resolved, And.Resolved):
            if choice:
                lines.add(depth, colored("All of", held), *_says(held))
                depth += 1
            for child in self._shallowest_first(_distinct(resolved.children)):
                self._breakdown(lines, child, depth, sl, state, opening)
            return
        if isinstance(resolved, Or.Resolved):
            lines.add(depth, colored("Any of", held), *_says(held))
            for _, item, child in self._choices(resolved, own, state):
                if item is not None:
                    lines.add(depth + 1, text("Has "), *item[0], *_says(item[1]))
                else:
                    self._breakdown(lines, child, depth + 1, sl, state, opening, choice=True)
            return
        if isinstance(resolved, BudgetTotal.Resolved):
            lines.add(depth, colored(f"Budget for {budget_label(resolved.location)}", held), *_says(held))
            return
        if isinstance(resolved, SufficientRawResources.Resolved):
            lines.add(depth, colored(f"Scenario expects {resolved.needed}", held), *_says(held))
            self._sources(lines, resolved, depth + 1, sl, state, opening)
            return
        if isinstance(resolved, AgeUpRequirement.Resolved):
            lines.add(depth, colored(f"Any {resolved.num_needed} of", held), *_says(held))
            for child in self._shallowest_first(list(resolved.pairs)):
                self._breakdown(lines, child, depth + 1, sl, state, opening, choice=True)
            if resolved.has_single:
                alone = resolved.children[-1](state)
                lines.add(depth, colored("Or by itself", alone), *_says(alone))
                self._breakdown(lines, resolved.children[-1], depth + 1, sl, state, opening, choice=True)
            return
        if resolved.always_false:
            lines.add(depth, colored("Never", False), *_says(False))
            return
        lines.add(depth, colored(resolved.explain_str(state), held), *_says(held))

    def _sources(self, lines: Lines, expects: SufficientRawResources.Resolved, depth: int,
                 sl: ScenarioLogic, state: CollectionState, opening: int) -> None:
        """Each gathering source once - its total, what of it counts now, and whether it can be
        worked - with the map areas holding it beneath: "6760 food (0 in logic) Can hunt", then
        "3900 food (in base)", and "2860 food (in the open) -> False" over what that area asks."""
        resource = f" {expects.resource}" if expects.resource else ""
        sources: dict[str, tuple[Rule.Resolved, list]] = {}
        kinds: dict[str, str] = {}
        for child, amount, area, kind in zip(expects.children, expects.amounts,
                                             expects.areas or ("",) * len(expects.amounts),
                                             expects.kinds or ("",) * len(expects.amounts)):
            if isinstance(child, And.Resolved) and len(child.children) >= 2:
                gathers, rest = child.children[0], child.children[1:]
                gate = rest[0] if len(rest) == 1 else And.Resolved(tuple(rest), player=child.player)
            else:
                gathers, gate = child, None
            entry = sources.setdefault(gathers.explain_str(), (gathers, []))
            kinds.setdefault(gathers.explain_str(), kind)
            entry[1].append((child, amount, area, gate))
        for gathers, areas in sources.values():
            total = sum(amount for _, amount, _, _ in areas)
            counted = sum(amount for child, amount, _, _ in areas if child(state))
            works = gathers(state)
            label = (self._asks(gathers, sl) if isinstance(gathers, ScenarioQuestion.Resolved)
                     else _SOURCE_NAMES.get(kinds[gathers.explain_str()], "Any of"))
            lines.add(depth, text(f"{total}{resource} ("), colored(f"{counted} in logic", counted > 0), text(") "),
                      colored(label, works), *_says(works))
            for child, amount, area, gate in areas:
                where = f" ({_AREAS.get(area, area)})" if area else ""
                what = f"{amount}{resource}{where}"
                counts = child(state)
                lines.add(depth + 1, colored(what, counts), *_says(counts),
                          self._entry(f"{sl.scenario.scenario_name}: {label}, {what}",
                                      lambda st, child=child, label=label, what=what:
                                          self._area_view(child, label, what, sl, st)))

    def _area_view(self, child: Rule.Resolved, label: str, what: str, sl: ScenarioLogic,
                   state: CollectionState) -> Lines:
        """What one map area's share of a source asks: the source, and whatever holding that
        area asks - each a line, its questions behind their markers."""
        lines = Lines()
        counts = child(state)
        lines.add(0, colored(sl.scenario.scenario_name, self._holds(sl.is_unlocked(), state)), text(": "),
                  colored(f"{label}, {what}", counts), *_says(counts))
        self._opened = set()
        self._breakdown(lines, child, 1, sl, state, 0)
        return lines

    def _choices(self, rule: Or.Resolved, own: str, state: CollectionState) -> list[tuple]:
        """An "or"'s choices with every "any of" inside it folded in - an any of an any is one
        choice among the rest - each once, shallowest first: (depth, item or None, rule or None)."""
        found: list[tuple] = []
        seen: set[str] = set()

        def gather(each: Rule.Resolved) -> None:
            if isinstance(each, Or.Resolved):
                for child in each.children:
                    gather(child)
                return
            items = self._items(each, own, state)
            if items is not None and (not items[0] or len(items[1]) == 1):
                for item in items[1]:
                    key = "".join(part["text"] for part in item[0])
                    if key not in seen:
                        seen.add(key)
                        found.append((0, item, None))
                return
            key = each.explain_str()
            if key not in seen:
                seen.add(key)
                found.append((self._depth(each), None, each))

        for child in rule.children:
            gather(child)
        return sorted(found, key=lambda choice: choice[0])

    def _shallowest_first(self, children: list[Rule.Resolved]) -> list[Rule.Resolved]:
        """Quick facts before what needs opening: stable, so equals keep the rule's order."""
        return sorted(children, key=self._depth)

    def _depth(self, rule: Rule.Resolved) -> int:
        """How deep a part's breakdown goes: an item or a budget 0, a group of items 1, a question
        one more than its answer, any other group one more than its deepest part."""
        return self._measure(rule, frozenset())[0]

    def _measure(self, rule: Rule.Resolved, path: frozenset[int]) -> tuple[int, bool]:
        """The depth, and whether it passed through a question asked inside itself. Such a loop
        counts as deep where it closes - it never bottoms out - so it sorts last; a depth that went
        through one depends on where it was entered, so only the others are kept - the order
        things are measured in can't change it."""
        known = self._depths.get(id(rule))
        if known is not None:
            return known, False
        if id(rule) in path:
            return LOOPED, True
        looped = False
        items = self._items(rule, "", None)
        if items is not None:
            depth = 0 if len(items[1]) == 1 else 1
        elif isinstance(rule, ScenarioQuestion.Resolved):
            inner, looped = self._measure(rule.answer, path | {id(rule)})
            depth = 1 + inner
        elif isinstance(rule, _GROUPS):
            depth = 0
            for child in rule.children:
                inner, loop = self._measure(child, path | {id(rule)})
                depth, looped = max(depth, inner), looped or loop
            depth += 1
        else:
            depth = 0
        if not looped:
            self._depths[id(rule)] = depth
        return depth, looped

    def _items(self, rule: Rule.Resolved, own: str, state: CollectionState | None
               ) -> tuple[bool, list[tuple[list[JSONMessagePart], bool]]] | None:
        """An item rule as its items, each with whether it is held: whether all are asked or any
        will do, and each one's parts - green where held, a counted one with how many are held,
        "Progressive Attila Scenario x2 Has x1". None for anything else. A scenario's own items
        lose its name."""
        def item(name: str, count: int = 1) -> tuple[list[JSONMessagePart], bool]:
            have = state.count(name, self.world.player) if state is not None else 0
            shown = (name.split(own, 1)[-1] if own else name) + (f" x{count}" if count > 1 else "")
            parts = [colored(shown, have >= count)]
            if count > 1:
                parts += [text(" "), colored(f"Has x{have}", have > 0)]
            return parts, have >= count
        if isinstance(rule, Has.Resolved):
            return True, [item(rule.item_name, rule.count)]
        if isinstance(rule, HasAll.Resolved):
            return True, [item(name) for name in rule.item_names]
        if isinstance(rule, HasAny.Resolved):
            return False, [item(name) for name in rule.item_names]
        if isinstance(rule, HasAllCounts.Resolved):
            return True, [item(name, count) for name, count in rule.item_counts]
        return None

    def _question_entry(self, question: ScenarioQuestion.Resolved, sl: ScenarioLogic) -> JSONMessagePart:
        """The marker that opens a scenario question not opened in place."""
        return self._entry(f"{sl.scenario.scenario_name}: {self._asks(question, sl)}",
                           lambda st: self._question_drill(question, sl, st))

    def _question_drill(self, question: ScenarioQuestion.Resolved, sl: ScenarioLogic,
                        state: CollectionState) -> Lines:
        """One scenario question broken down, as it is in place."""
        lines = Lines()
        lines.add(0, colored(sl.scenario.scenario_name, self._holds(sl.is_unlocked(), state)), text(": "),
                  colored(self._asks(question, sl), question(state)), *_says(question(state)))
        lines.extend(self._question_body(question, sl, state))
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
                lines.add(2, colored(f"{amount} {noun}", True), text(": an easy source"), *_says(True), *why)
                continue
            asked = dict(total.table.total(state).cost).get(resource, 0) if total is not None else None
            if asked is None or total.lowest(resource) > most[resource]:
                lines.add(2, colored(f"{amount} {noun}", False), text(": not in budget, and no easy source yet"),
                          *_says(False), *why)
                continue
            lines.add(2, colored(f"{amount} {noun}", pile[resource] >= asked),
                      text(f": budget {asked}, starting pile {pile[resource]}, no easy source yet"),
                      *_says(pile[resource] >= asked), *why)
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
                    lines.add(2, colored(f"{asked} {noun}", True), text(" in its budget: an easy source"),
                              *_says(True), *why)
                elif total.lowest(resource) > most[resource]:
                    lines.add(2, colored(f"{asked} {noun}", False),
                              text(" in its budget: more than any starting pile, no easy source yet"),
                              *_says(False), *why)
                else:
                    lines.add(2, colored(f"{asked} {noun}", pile[resource] >= asked),
                              text(f" in its budget: starting pile {pile[resource]}, no easy source yet"),
                              *_says(pile[resource] >= asked), *why)
            together = together or [sl]
            campaign = sl.scenario.campaign.campaign_name
            chapters = tuple(each.scenario.chapter for each in together)
            budgets = Costs(self.world, route, together)
            lines.add(2, colored("Its budget", total(state)), *_says(total(state)),
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

    @staticmethod
    def _add_wrapped(lines: Lines, depth: int, parts: list[JSONMessagePart]) -> None:
        """A route line, continued one level deeper from its age when it would run past WIDTH:
        the log loses the indentation of a line it wraps itself."""
        if len(INDENT * depth) + sum(len(part["text"]) for part in parts) <= WIDTH:
            lines.add(depth, *parts)
            return
        cut_at = next((index for index, part in enumerate(parts) if part["text"] == " in the "), None)
        if cut_at is None:
            lines.add(depth, *parts)
            return
        lines.add(depth, *parts[:cut_at])
        lines.add(depth + 1, text("in the "), *parts[cut_at + 1:])

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

    @staticmethod
    def _runs(chapters: list[tuple[int, Status]]) -> list[tuple[list[int], list[JSONMessagePart]]]:
        """The chapters where the route is open and where it isn't, a row each: "1, 3–5 -> True"."""
        by_held: dict[bool, list[int]] = {}
        for chapter, status in chapters:
            by_held.setdefault(status is Status.AVAILABLE, []).append(chapter)
        ordered = sorted(by_held.items(), key=lambda item: item[1][0])
        return [(numbers, [colored(_ranges(numbers), held), *_says(held)]) for held, numbers in ordered]

    # -- general requirements --------------------------------------------------------------------

    def _requirements(self, rules: tuple[Rule, ...],
                      state: CollectionState) -> list[tuple[int, list[JSONMessagePart]]]:
        """One line an item, "Has Militia Line -> True"; an "any of" as "Any of" with an item a
        line beneath it, each with how much deeper it sits. An item asked twice is listed once."""
        lines: list[tuple[int, list[JSONMessagePart]]] = []
        seen: set[str] = set()
        for rule in rules:
            resolved = self._resolved(rule)
            if resolved.always_true:
                continue
            names = sorted(set(resolved.item_dependencies()) - seen)
            if not names:
                continue
            seen.update(names)
            nested = 0
            if len(names) > 1 and type(resolved).__qualname__.startswith(("HasAny", "Or")):
                held = resolved(state)
                lines.append((0, [colored("Any of", held), text(" -> "), truth(held)]))
                nested = 1
            for name in names:
                held = state.has(name, self.world.player)
                lines.append((nested, [colored(f"Has {name}", held), text(" -> "), truth(held)]))
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
