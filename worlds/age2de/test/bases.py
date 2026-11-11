import unittest
import logging
import sys

from BaseClasses import CollectionState

from test.bases import WorldTestBase
from test.general import setup_solo_multiworld

from .. import Age2World, AGE2_DE
from ..items.Items import Resource
from ..logic.custom_logic.EconomyRoutes import EconomyRoutesYield, Strength


def own_easy_source(scenario_logic, resource: Resource):
    routes = scenario_logic.routes
    return EconomyRoutesYield(
        economy=routes.economy_routes(),
        resource=resource,
        strength=Strength.AT_SCALE,
        among=frozenset(route.name for route in routes.scenario_specific_routes()),
    )


class Age2TestBase(WorldTestBase):
    game = AGE2_DE
    world: Age2World

    def setUp(self) -> None:
        self._root_log_level = logging.root.level
        logging.root.setLevel(logging.WARNING)
        super().setUp()

    def tearDown(self) -> None:
        kivy_logger = sys.modules.get("kivy.logger")
        if kivy_logger is not None:
            kivy_logger.LoggerHistory.clear_history()
        super().tearDown()
        logging.root.setLevel(getattr(self, "_root_log_level", logging.WARNING))


class Age2RuleTestBase(unittest.TestCase):
    """For tests that assert on access rules rather than on the pool.

    Two things here are load bearing. Rules only exist after set_rules, so all
    four steps have to run -- pool tests get away with create_regions alone.
    And a state has to sweep, or every scenario past the first reports itself
    locked and the assertions pass without testing anything.
    """

    campaigns = ["Attila the Hun", "Joan of Arc"]
    starting_campaigns = ["Attila the Hun"]

    def build(self, **options) -> Age2World:
        # No steps here: generate_early is what reads enabled_campaigns, so running it before these
        # writes would pin the world to the default campaign and ignore every option below.
        world = setup_solo_multiworld(Age2World, ()).worlds[1]
        world.options.enabled_campaigns.value = set(self.campaigns)
        world.options.starting_campaigns.value = set(self.starting_campaigns)
        for name, value in options.items():
            getattr(world.options, name).value = value
        for step in ("generate_early", "create_regions", "create_items", "set_rules"):
            getattr(world, step)()
        self.world = world
        self.multiworld = world.multiworld
        return world

    def state_without(self, *item_names: str) -> CollectionState:
        state = CollectionState(self.multiworld)
        for item in self.multiworld.itempool:
            if item.name not in item_names:
                state.collect(item, prevent_sweep=True)
        state.sweep_for_advancements()
        return state

    def state_with(self, *item_names: str) -> CollectionState:
        """The opposite of state_without: the precollected items and nothing but the ones named.
        A name repeated collects that many copies, for progressive items. It does not sweep -
        this is for asking what one short state reaches, not what a playthrough does.

        A scenario unlock is an event item sitting on the previous chapter's victory rather than
        anything in the pool, so the events count as available too."""
        state = CollectionState(self.multiworld)
        wanted = list(item_names)
        events = [location.item for location
                  in self.multiworld.get_filled_locations(self.world.player)]
        for item in list(self.multiworld.itempool) + events:
            if item.name in wanted:
                wanted.remove(item.name)
                state.collect(item, prevent_sweep=True)
        if wanted:
            raise AssertionError(f"no such item to collect: {wanted}")
        return state

    def can_reach(self, location_name: str, state: CollectionState = None) -> bool:
        if state is None:
            state = self.state_without()
        return state.can_reach_location(location_name, self.world.player)

    def location_names(self) -> set[str]:
        return {location.name for location in self.multiworld.get_locations(self.world.player)}

    def access_rule(self, location_name: str):
        """A location's resolved rule, to ask on its own. `can_reach` answers for the whole
        route to it, which hides what the location itself asks."""
        return self.multiworld.get_location(location_name, self.world.player).access_rule

    def item_requirements(self, location_name: str) -> set[str]:
        """The item names a location's resolved rule asks for.

        Introspection alone is not enough to trust: Has() never validates a name,
        so a typo yields a rule nothing can satisfy and an empty-looking set. The
        tests that matter pair this with a real reachability check.
        """
        rule = self.multiworld.get_location(location_name, self.world.player).access_rule
        dependencies = getattr(rule, "item_dependencies", None)
        return set(dependencies()) if dependencies else set()
