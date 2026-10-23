"""Per-scenario rules - the ones a scenario's own objectives ask for.

Caveman lives here as well as in the unit logic: the global "Own X" locations already ask a
granted unit to be restorable, but a scenario objective that leans on units an item hands over
has to ask the same question for itself.
"""

from ..Options import Caveman, ScenarioBranching, Unitsanity, UnitsanityItems
from ..items.Items import Age2ItemData
from ..locations.Buildings import Age2BuildingData
from ..locations.Locations import Age2ScenarioLocationData as L
from ..locations.Scenarios import Age2ScenarioData
from ..locations.UnitLines import Age2UnitLineData
from .bases import Age2RuleTestBase

MONK_LINE = Age2UnitLineData.MONK_LINE.item.item_name
KEREYID = Age2ItemData.AP_GENGHIS_1_KEREYID_TRIBE.item_name

# What the Kereyid gate covers, per branching mode. Victory and the Complete event are gated in
# both: Victory wants four tribes joined, and the Ungirrads only join for a relic.
BRANCH_LOCATIONS = {
    ScenarioBranching.option_all: (L.GEN1_RELIC_RED_MONASTERY, L.GEN1_RELIC_WOLF,
                                   L.GEN1_RELIC_PALISADED, L.GEN1_RECRUIT_UNGIRRADS),
    ScenarioBranching.option_any: (L.GEN1_ANY_RELIC,),
}
ALWAYS_GATED = (L.GEN1_VICTORY,)
COMPLETE = "Complete " + L.GEN1_VICTORY.scenario.scenario_name

UNITSANITY = dict(unitsanity=Unitsanity.option_all,
                  unitsanity_items=UnitsanityItems.option_unit_line)

CARTS = Age2ItemData.AP_JOAN_2_TRADE_CARTS.item_name
DOCK = Age2ItemData.AP_JOAN_2_DOCK.item_name
ORLEANS = Age2ItemData.AP_JOAN_2_ORLEANS.item_name
BRIDGE = L.JOAN2_CONQUER_BRIDGE.global_name()
JOAN_2_VICTORY = L.JOAN2_VICTORY.global_name()
JOAN_2_COMPLETE = "Complete " + L.JOAN2_VICTORY.scenario.scenario_name


class TestGenghis1Relics(Age2RuleTestBase):
    """The Kereyid Tribe hands over the two monks that collect Genghis 1's relics. Under caveman
    the game knocks them down to Militia like any other unit a scenario trigger gives you, so the
    relics then want the Monk's unit items as well as the tribe."""

    campaigns = ["Genghis Khan"]
    starting_campaigns = ["Genghis Khan"]

    def gated_locations(self, branching: int) -> list[str]:
        covered = BRANCH_LOCATIONS[branching] + ALWAYS_GATED
        return [location.global_name() for location in covered] + [COMPLETE]

    def test_caveman_asks_for_the_monk_line_on_top_of_the_tribe(self):
        for branching, mode in ((ScenarioBranching.option_all, "all"),
                                (ScenarioBranching.option_any, "any")):
            self.build(caveman=Caveman.option_true, scenario_branching=branching, **UNITSANITY)
            without_monks = self.state_without(MONK_LINE)
            for name in self.gated_locations(branching):
                with self.subTest(branching=mode, location=name):
                    self.assertFalse(self.can_reach(name, without_monks))
                    self.assertTrue(self.can_reach(name))

    def test_the_gate_still_wants_the_tribe(self):
        """Restorable monks are not the whole answer - the tribe is what puts monks on the map."""
        self.build(caveman=Caveman.option_true,
                   scenario_branching=ScenarioBranching.option_any, **UNITSANITY)
        without_tribe = self.state_without(KEREYID)
        for name in self.gated_locations(ScenarioBranching.option_any):
            with self.subTest(location=name):
                self.assertFalse(self.can_reach(name, without_tribe))

    def test_without_caveman_the_tribe_is_enough(self):
        for branching, mode in ((ScenarioBranching.option_all, "all"),
                                (ScenarioBranching.option_any, "any")):
            self.build(caveman=Caveman.option_false, scenario_branching=branching, **UNITSANITY)
            without_monks = self.state_without(MONK_LINE)
            for name in self.gated_locations(branching):
                with self.subTest(branching=mode, location=name):
                    self.assertTrue(self.can_reach(name, without_monks))

    def test_caveman_without_unitsanity_leaves_the_monk_alone(self):
        """No unit table row means the game never knocks the monk down, so there is nothing to
        restore and nothing new to ask for."""
        self.build(caveman=Caveman.option_true, unitsanity=Unitsanity.option_none,
                   scenario_branching=ScenarioBranching.option_any)
        for name in self.gated_locations(ScenarioBranching.option_any):
            with self.subTest(location=name):
                self.assertEqual(self.item_requirements(name), {KEREYID})



class TestJoan2Crossing(Age2RuleTestBase):
    campaigns = ["Attila the Hun", "Joan of Arc"]
    starting_campaigns = ["Attila the Hun"]

    def setUp(self):
        self.build()

    def test_without_a_crossing_nothing_past_the_river_is_reachable(self):
        stranded = self.state_without(CARTS, DOCK)
        for name in (BRIDGE, JOAN_2_VICTORY, JOAN_2_COMPLETE):
            with self.subTest(location=name):
                self.assertFalse(self.can_reach(name, stranded))

    def test_orleans_hands_over_nothing_until_joan_crosses(self):
        joan_2 = self.world.rules.logic.for_scenario(Age2ScenarioData.AP_JOAN_2)
        orleans = {
            "town center": joan_2.has_building(Age2BuildingData.TOWN_CENTER),
            "villagers": joan_2.has_vils(),
        }
        for label, rule in orleans.items():
            resolved = rule.resolve(self.world)
            with self.subTest(granted=label):
                self.assertFalse(resolved(self.state_without(CARTS, DOCK)))
                self.assertTrue(resolved(self.state_without(CARTS)))
                self.assertTrue(resolved(self.state_without(DOCK)))

    def test_the_dock_alone_is_a_crossing(self):
        by_sea = self.state_without(CARTS)
        for name in (BRIDGE, JOAN_2_VICTORY):
            with self.subTest(location=name):
                self.assertTrue(self.can_reach(name, by_sea))

    def test_the_escort_takes_the_bridge_without_orleans(self):
        self.assertTrue(self.can_reach(BRIDGE, self.state_without(DOCK, ORLEANS)))

    def test_victory_still_wants_orleans(self):
        self.assertFalse(self.can_reach(JOAN_2_VICTORY, self.state_without(ORLEANS)))

    def test_the_full_pool_reaches_every_joan_2_location(self):
        present = self.location_names()
        joan_2 = [
            location.global_name() for location in L
            if location.scenario == Age2ScenarioData.AP_JOAN_2
            and location.global_name() in present
        ]
        self.assertTrue(joan_2)
        for name in joan_2 + [JOAN_2_COMPLETE]:
            with self.subTest(location=name):
                self.assertTrue(self.can_reach(name))

    def test_the_bridge_names_both_routes(self):
        self.assertTrue({CARTS, DOCK} <= self.item_requirements(BRIDGE))
