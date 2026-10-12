"""What a location costs, whether any scenario can pay for it, and how: its budget or an easy
source of each resource."""
from __future__ import annotations

import itertools
from typing import TYPE_CHECKING, Callable

from BaseClasses import CollectionState
from NetUtils import JSONMessagePart
from rule_builder.rules import Has, Rule

from ..generation.pools.BudgetPool import SAMPLED_RESOURCES, VILLAGER
from ..items.Items import Age2ItemData, Resource
from ..locations.Ages import Age2AgeData
from ..locations.Buildings import BUILDING_PREREQUISITE, Age2BuildingData
from ..logic.budget.BudgetTotal import BudgetTotal, _label
from ..locations.Techs import Age2TechData
from ..locations.UnitLines import Age2UnitLineData
from ..locations.Units import Age2UnitData
from ..logic.budget.Need import Cost, Need
from ..logic.budget.CostTable import CostTable
from ..logic.custom_logic.ResourceAmount import contributors
from .Layout import BUDGETED_ITEMS, Lines, _ranges, colored, text

if TYPE_CHECKING:
    from .. import Age2World
    from ..logic.ScenarioLogic import ScenarioLogic
    from .Routes import Route


MOST_WAIVER_ITEMS = 8
"""Past this many items behind a scenario's waivers, its possibilities are the waivers' own
combinations instead of the items'."""

type Entry = Callable[[str, Callable[[CollectionState], Lines]], JSONMessagePart]
"""Keeps a drill-down and gives back the marker that opens it."""


class Costs:
    """One route's price, asked of the scenarios that offer the route."""

    def __init__(self, world: Age2World, route: Route, offering: list[ScenarioLogic]) -> None:
        self.world = world
        self.priced, cost = route.price
        self.cost = [(resource, amount) for resource, amount in cost.items() if amount > 0]
        self.offering = offering
        """Scenarios offering the route, in campaign order."""
        self._states: dict[tuple[str, ...], CollectionState] = {}

    # -- the line under Requires ------------------------------------------------------------------

    def line(self, state: CollectionState, unlocked: list[ScenarioLogic]) -> list[JSONMessagePart]:
        """"Costs 60 food, 20 gold", each amount green if a scenario open to the player can pay
        that resource - its budget, or an easy source of it."""
        parts: list[JSONMessagePart] = [text("Costs ")]
        for index, (resource, amount) in enumerate(self.cost):
            if index:
                parts.append(text(", "))
            paid = any(self._paid(sl, resource, state) for sl in unlocked)
            parts.append(colored(f"{amount} {resource.name.lower()}", paid))
        return parts

    def _paid(self, sl: ScenarioLogic, resource: Resource, state: CollectionState) -> bool:
        if self._easy(sl, resource, state):
            return True
        total = self._budget(sl)
        return total is not None and total.covers(state).get(resource, True)

    # -- the drill-down ---------------------------------------------------------------------------

    def drill(self, label: str, state: CollectionState, entry: Entry) -> Lines:
        lines = Lines()
        pile = self._pile(state)
        reached = self.world.multiworld.get_location(label, self.world.player).can_reach(state)
        unlocked = [sl for sl in self.offering if sl.is_unlocked().resolve(self.world)(state)]
        title = [text("Costs of "), colored(budget_label(self.priced), reached), text(": ")]
        lines.add(0, *title, *self.line(state, unlocked)[1:])
        lines.add(1, text("Starting pile: " + ", ".join(
            f"{pile[resource]} {resource.name.lower()}" for resource in SAMPLED_RESOURCES)))
        for resource, amount in self.cost:
            lines.add(1, text(f"{resource.name.title()} ({amount})"))
            self._budgeted(lines, label, resource, pile, state, entry)
            self._easy_sources(lines, resource, state)
        return lines

    def _budgeted(self, lines: Lines, label: str, resource: Resource, pile: dict[Resource, int],
                  state: CollectionState, entry: Entry) -> None:
        """Each scenario whose budget order holds it, with what its full running total asks of
        this resource, and under it what each waiver brings that down to: one run of chapters a
        line, each with its own budget to open. Campaigns and chapters are green where open to the
        player, amounts where the pile covers them, waivers where they hold."""
        by_campaign: dict[str, dict[tuple, list[int]]] = {}
        unbudgeted: dict[str, dict[bool, list[int]]] = {}
        open_campaign: dict[str, bool] = {}
        for sl in self.offering:
            total = self._budget(sl)
            name, opened = sl.scenario.campaign.campaign_name, self._open(sl, state)
            open_campaign[name] = open_campaign.get(name, False) or opened
            if total is None:
                # It offers the route but never budgets it: only an easy source pays there.
                unbudgeted.setdefault(name, {}).setdefault(opened, []).append(sl.scenario.chapter)
                continue
            table = total.table
            full = dict(table.totals_by_mask[0].cost).get(resource, 0)
            waived = []
            for mask, conditions in self._possible(table, state)[1:]:
                amount = dict(table.totals_by_mask[mask].cost).get(resource, 0)
                if amount < full and amount not in (seen for seen, _ in waived):
                    waived.append((amount, conditions))
            key = (full, tuple(waived), opened)
            by_campaign.setdefault(name, {}).setdefault(key, []).append(sl.scenario.chapter)
        if not by_campaign:
            lines.add(2, colored("Not in budget", False), text(f"  [/explain {BUDGETED_ITEMS}]"))
            return
        lines.add(2, text("Budgeted in"), text(f"  [/explain {BUDGETED_ITEMS}]"))
        noun = f"starting {resource.name.lower()}"
        for campaign in open_campaign:   # every campaign offering the route, in campaign order
            rows: list[tuple[int, list[JSONMessagePart], tuple]] = []
            for (full, waived, opened), chapters in by_campaign.get(campaign, {}).items():
                run = _ranges(chapters)
                marker = entry(f"{label}'s budget in {campaign} {run}",
                               lambda st, campaign=campaign, chapters=tuple(chapters):
                                   self.campaign_budget(label, campaign, st, chapters))
                rows.append((chapters[0], [colored(run, opened), text(" "),
                                           colored(f"(at {full} {noun})", pile[resource] >= full),
                                           marker], waived))
            for opened, chapters in unbudgeted.get(campaign, {}).items():
                rows.append((chapters[0], [colored(_ranges(chapters), opened), text(" "),
                                           colored("not in budget", False),
                                           text(f"  [/explain {BUDGETED_ITEMS}]")], ()))
            for index, (_, parts, waived) in enumerate(sorted(rows, key=lambda row: row[0])):
                if index:
                    lines.add(4, *parts)
                else:
                    lines.add(3, colored(campaign, open_campaign[campaign]), text(": "), *parts)
                for amount, conditions in waived:
                    parts = [colored(f"{amount}", pile[resource] >= amount), text(" with ")]
                    for index, (condition, held) in enumerate(conditions):
                        parts += [text(", ") if index else text(""), colored(condition, held)]
                    lines.add(5, *parts)

    def _easy_sources(self, lines: Lines, resource: Resource, state: CollectionState) -> None:
        by_campaign: dict[str, list[int]] = {}
        for sl in self.offering:
            if self._easy(sl, resource, state):
                by_campaign.setdefault(sl.scenario.campaign.campaign_name, []).append(sl.scenario.chapter)
        if not by_campaign:
            lines.add(2, colored("No easy source yet", False))
            return
        lines.add(2, text("Easy source in"))
        for campaign, chapters in by_campaign.items():
            lines.add(3, text(f"{campaign}: "), colored(_ranges(chapters), True))

    def campaign_budget(self, label: str, campaign: str, state: CollectionState,
                        chapters: tuple[int, ...] | None = None) -> Lines:
        """Every total the campaign's scenarios could charge for it: the full one, then each that
        waivers bring it down to, headed by the items that make it so, and listed in the order the
        budget expects things bought. Scenarios sharing a possibility share its block. Scenario
        names are green where open, items where held; an amount is green while the pile still
        covers everything bought before it."""
        pile = self._pile(state)
        blocks: dict[tuple, list[ScenarioLogic]] = {}
        for sl in self.offering:
            total = self._budget(sl)
            if sl.scenario.campaign.campaign_name != campaign or total is None:
                continue
            if chapters is not None and sl.scenario.chapter not in chapters:
                continue
            table = total.table
            for mask, conditions in self._possible(table, state):
                holding = [waiver for bit, waiver in enumerate(table.waivers) if mask >> bit & 1]
                running = table.totals_by_mask[mask]
                keys, charges = self._in_build_order(sl, running, holding)
                block = (conditions, running.cost, tuple((key, charges[key]) for key in keys))
                blocks.setdefault(block, []).append(sl)

        lines = Lines()
        if not blocks:
            lines.add(0, text(f"Nothing in {campaign} budgets it."))
            return lines
        for (conditions, cost, charged), scenarios in blocks.items():
            head = [*self._names(scenarios, state), text(": ")]
            for index, (condition, held) in enumerate(conditions):
                head += [text(", ") if index else text(""), colored(condition, held)]
            if conditions:
                head.append(text(": "))
            lines.add(0, *head, *(self._amounts(cost, pile) if cost else [colored("free", True)]))
            keys = tuple(key for key, _ in charged)
            colours = self._spend(keys, dict(charged), pile)
            for key, (name, each) in charged:
                lines.add(1, self._charge_name(key, name, state), text(" ("),
                          *self._amounts(each, pile, colours[key]), text(")"))
        return lines

    def _possible(self, table: CostTable,
                  state: CollectionState) -> list[tuple[int, tuple[tuple[str, bool], ...]]]:
        """Each total the items could bring about, with the fewest items that do: none first. Asked
        of the items rather than the waivers, since one item can switch several waivers - Bleda's
        Camp stands the Stable as well - and a waiver never holds without its items. Each comes as
        the waivers it switches on, and its items, held or not."""
        names = sorted({name for waiver in table.waivers for name in waiver.answer.item_dependencies()})
        if len(names) > MOST_WAIVER_ITEMS or any(
                not waiver.answer.item_dependencies() for waiver in table.waivers):
            return [(mask, self._conditions(
                [waiver for bit, waiver in enumerate(table.waivers) if mask >> bit & 1], state))
                for mask in _possibilities(table)]
        fewest: dict[Cost, tuple[int, tuple[str, ...]]] = {}
        for size in range(len(names) + 1):
            for held in itertools.combinations(names, size):
                mask = table.mask(self._holding(held))
                fewest.setdefault(table.totals_by_mask[mask].cost, (mask, held))
        return [(mask, tuple((f"Has {_short(name)}", state.has(name, self.world.player)) for name in held))
                for mask, held in fewest.values()]

    def _holding(self, names: tuple[str, ...]) -> CollectionState:
        """A state with just these items."""
        if names not in self._states:
            state = CollectionState(self.world.multiworld)
            for name in names:
                state.collect(self.world.create_item(name), prevent_sweep=True)
            self._states[names] = state
        return self._states[names]

    def _conditions(self, waivers: list, state: CollectionState) -> tuple[tuple[str, bool], ...]:
        """What makes the waivers hold, as items: "Has Attila's Camp", each held or not. "Has A or
        B" where any will do, unless one of them is asked for anyway; the waiver's own description
        where no item decides it. Item names lose their scenario: the block names it already."""
        required: list[tuple[str, bool]] = []
        anyof: list[tuple[tuple[str, ...], bool]] = []
        described: list[tuple[str, bool]] = []
        for waiver in waivers:
            answer = waiver.answer
            names = sorted(answer.item_dependencies())
            if not names:
                described.append((waiver.description, bool(waiver(state))))
            elif len(names) > 1 and type(answer).__qualname__.startswith(("HasAny", "Or")):
                anyof.append((tuple(names), bool(answer(state))))
            else:
                required += [(name, state.has(name, self.world.player)) for name in names]
        asked = {name for name, _ in required}
        return (
            *((f"Has {_short(name)}", held) for name, held in dict(required).items()),
            *(("Has " + " or ".join(map(_short, names)), held)
              for names, held in dict(anyof).items() if not asked & set(names)),
            *described,
        )

    def _in_build_order(self, sl: ScenarioLogic, running,
                        holding: list) -> tuple[tuple, dict[object, tuple[str, Cost]]]:
        """Every charge in the running total with these waivers holding, each at the first order
        entry whose prefix makes the total charge it. Exactly what the total charges, reordered."""
        order = sl.budget.order
        holding = [*sl.budget.always_waived, *holding]
        waived = frozenset(building for waiver in holding for building in waiver.buildings)
        needed = order.needed(frozenset(purchase for waiver in holding for purchase in waiver.purchases),
                              waived)
        entries = []
        for entry in order.order:
            if entry.location in needed or entry.location is self.priced:
                entries.append(entry)
            if entry.location is self.priced:
                break

        trained = {entry.location.line: entry.location for entry in entries
                   if isinstance(entry.location, Age2UnitData)}   # the last of a line wins
        charges = {key: (_trained_name(key, trained) or name, cost)
                   for key, (name, cost) in _charges(running.requirement).items()}
        first: dict[object, int] = {}
        for index in range(len(entries)):
            for key in _charges(order.requirement(entries[:index + 1], waived)):
                if key in charges:
                    first.setdefault(key, index)
            if len(first) == len(charges):
                break
        keys = tuple(sorted(charges, key=lambda key: (first.get(key, len(entries)), _within(key))))
        return keys, charges

    # -- colouring ---------------------------------------------------------------------------------

    def _open(self, sl: ScenarioLogic, state: CollectionState) -> bool:
        return sl.is_unlocked().resolve(self.world)(state)

    def _names(self, scenarios: list[ScenarioLogic], state: CollectionState) -> list[JSONMessagePart]:
        parts: list[JSONMessagePart] = []
        for index, sl in enumerate(scenarios):
            if index:
                parts.append(text(", "))
            parts.append(colored(sl.scenario.scenario_name, self._open(sl, state)))
        return parts

    @staticmethod
    def _amounts(cost: Cost, pile: dict[Resource, int],
                 colours: dict[Resource, bool] | None = None) -> list[JSONMessagePart]:
        """"275 wood, 100 stone", each green if covered - by `colours`, or else by the pile."""
        parts: list[JSONMessagePart] = []
        for index, (resource, amount) in enumerate(cost):
            if index:
                parts.append(text(", "))
            ok = colours[resource] if colours is not None else pile[resource] >= amount
            parts.append(colored(f"{amount} {resource.name.lower()}", ok))
        return parts

    @staticmethod
    def _spend(keys: tuple, charges: dict[object, tuple[str, Cost]],
               pile: dict[Resource, int]) -> dict[object, dict[Resource, bool]]:
        """Buying in order, whether the pile still covers each charge's amounts."""
        spent = dict.fromkeys(SAMPLED_RESOURCES, 0)
        colours: dict[object, dict[Resource, bool]] = {}
        for key in keys:
            colours[key] = {}
            for resource, amount in charges[key][1]:
                spent[resource] += amount
                colours[key][resource] = spent[resource] <= pile[resource]
        return colours

    def _charge_name(self, key, name: str, state: CollectionState) -> JSONMessagePart:
        """The charge, green where the item that unlocks it is held; plain where none does."""
        rule = self._unlocked_by(key)
        if rule is None:
            return text(name)
        return colored(name, rule.resolve(self.world)(state))

    def _unlocked_by(self, key) -> Rule | None:
        logic = self.world.rules.logic
        if isinstance(key, Age2BuildingData):
            return logic.buildings.has_building_item(key)
        if isinstance(key, Age2AgeData):
            return logic.ages.has_age(key)
        identity = key[1]
        if isinstance(identity, Age2UnitLineData):   # whatever trains the line: its item, tokens or building
            return logic.units.has_unit_items(identity.head)
        if identity == "villager":
            return logic.units.has_villager_item()
        if isinstance(identity, Age2TechData) and self.world.pool.techs.includes(identity):
            return Has(identity.item.item_name)
        return None

    # -- asking --------------------------------------------------------------------------------------

    def _budget(self, sl: ScenarioLogic) -> BudgetTotal.Resolved | None:
        """The scenario's budget total for it, or None if it isn't in that scenario's order."""
        resolved = BudgetTotal(scenario=sl.scenario, location=self.priced).resolve(self.world)
        return resolved if isinstance(resolved, BudgetTotal.Resolved) else None

    def _easy(self, sl: ScenarioLogic, resource: Resource, state: CollectionState) -> bool:
        return sl.economy.has_easy_source(resource).resolve(self.world)(state)

    def _pile(self, state: CollectionState) -> dict[Resource, int]:
        held = state.prog_items[self.world.player]
        return {resource: sum(held[name] * each for name, each in contributors(resource))
                for resource in SAMPLED_RESOURCES}


def budget_label(location) -> str:
    """A budget item as the budget words it: "Train Man-at-Arms", "Train Villager x3",
    "Research Feudal Age", "Build Mill"."""
    if location is VILLAGER:
        return _trained_name(("own", "villager"), {})
    if isinstance(location, Age2UnitData):
        return f"Train {location.location_name.removeprefix('Own ')}"
    if isinstance(location, Age2AgeData):
        return location.location_name.replace("Reach ", "Research ", 1)
    return location.location_name


def _trained_name(key, trained: dict[Age2UnitLineData, Age2UnitData]) -> str | None:
    """A unit price by what is trained: "Train Villager x3" for the villagers' food, "Train
    Man-at-Arms" for the Militia Line when the order trains Man-at-Arms. None for anything else."""
    if not isinstance(key, tuple):
        return None
    identity = key[1]
    if identity == "villager":
        food = Age2ItemData.STARTING_VILLAGER_FOOD.type
        return f"Train Villager x{food.amount // VILLAGER.cost[food.type]}"
    if identity in trained:
        return f"Train {trained[identity].location_name.removeprefix('Own ')}"
    return None


def _short(item_name: str) -> str:
    """"Attila, The Scourge of God: Bleda's Camp" -> "Bleda's Camp"."""
    return item_name.rsplit(": ", 1)[-1]


def _possibilities(table: CostTable) -> list[int]:
    """The waiver masks worth showing: none first, then for each other total the fewest waivers
    that bring it about."""
    fewest: dict[Cost, int] = {}
    for mask in sorted(range(len(table.totals_by_mask)), key=lambda mask: (mask.bit_count(), mask)):
        fewest.setdefault(table.totals_by_mask[mask].cost, mask)
    return list(fewest.values())


def _charges(requirement) -> dict[object, tuple[str, Cost]]:
    """What a requirement charges, keyed so two requirements can be compared: buildings, ages
    and own prices, each with its name and cost."""
    charges: dict[object, tuple[str, Cost]] = {}
    for building in (*requirement.need.entry_buildings, *requirement.buildings):
        charges[building] = (building.location_name, Need.as_cost(building.cost))
    for age in requirement.ages:
        charges[age] = (age.location_name.replace("Reach ", "Research ", 1), Need.as_cost(age.cost))
    for price in requirement.need.own_price:
        charges[("own", price.identity)] = (_label(price.identity), price.cost)
    return {key: charge for key, charge in charges.items() if charge[1]}


def _within(key) -> tuple[int, int, int]:
    """Within one entry: by age; a building's prerequisites before it; an age-up after the
    buildings of the age before it; the entry's own price last."""
    if isinstance(key, Age2BuildingData):
        depth, building = 0, key
        while (building := BUILDING_PREREQUISITE.get(building)) is not None:
            depth += 1
        return key.age.value, 0, depth
    if isinstance(key, Age2AgeData):
        return key.value - 1, 1, 0
    return 99, 2, 0
