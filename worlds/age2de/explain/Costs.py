"""What a location costs, and whether any scenario can pay for it: an easy source of each resource."""
from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from BaseClasses import CollectionState
from NetUtils import JSONMessagePart

from ..items.Items import Resource
from .Layout import Lines, _ranges, colored, text

if TYPE_CHECKING:
    from .. import Age2World
    from ..logic.ScenarioLogic import ScenarioLogic
    from .Routes import Route


type Entry = Callable[[str, Callable[[CollectionState], Lines]], JSONMessagePart]
"""Keeps a drill-down and gives back the marker that opens it."""


class Costs:
    """One route's price, asked of the scenarios that offer the route."""

    def __init__(self, world: Age2World, route: Route, offering: list[ScenarioLogic]) -> None:
        self.world = world
        self.cost = [(resource, amount) for resource, amount in route.price.items() if amount > 0]
        self.offering = offering
        """Scenarios offering the route, in campaign order."""

    # -- the line under Requires ------------------------------------------------------------------

    def line(self, state: CollectionState, unlocked: list[ScenarioLogic]) -> list[JSONMessagePart]:
        """"Costs 60 food, 20 gold", each amount green if a scenario open to the player has an easy
        source of that resource."""
        parts: list[JSONMessagePart] = [text("Costs ")]
        for index, (resource, amount) in enumerate(self.cost):
            if index:
                parts.append(text(", "))
            paid = any(self._easy(sl, resource, state) for sl in unlocked)
            parts.append(colored(f"{amount} {resource.name.lower()}", paid))
        return parts

    # -- the drill-down ---------------------------------------------------------------------------

    def drill(self, label: str, state: CollectionState, entry: Entry) -> Lines:
        """Each resource it costs, and every chapter with an easy source of it."""
        lines = Lines()
        reached = self.world.multiworld.get_location(label, self.world.player).can_reach(state)
        unlocked = [sl for sl in self.offering if sl.is_unlocked().resolve(self.world)(state)]
        title = [text("Costs of "), colored(label, reached), text(": ")]
        lines.add(0, *title, *self.line(state, unlocked)[1:])
        for resource, amount in self.cost:
            lines.add(1, text(f"{resource.name.title()} ({amount})"))
            self._easy_sources(lines, resource, state)
        return lines

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

    # -- asking --------------------------------------------------------------------------------------

    def _easy(self, sl: ScenarioLogic, resource: Resource, state: CollectionState) -> bool:
        return sl.economy.has_easy_source(resource).resolve(self.world)(state)
