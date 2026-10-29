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
from ..locations.Units import Age2UnitData
from ..locations.connections.ScenarioCavemanExemptions import SCENARIO_TO_CAVEMAN_EXEMPTIONS
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


TRANSPORTS = Age2UnitLineData.TRANSPORT_SHIP_LINE.item.item_name
TRADE_CART_LINE = Age2UnitLineData.TRADE_CART_LINE.item.item_name
BOMBARDS = Age2UnitLineData.BOMBARD_CANNON_LINE.item.item_name
TREBUCHETS = Age2UnitLineData.TREBUCHET_LINE.item.item_name
RAMS = Age2UnitLineData.BATTERING_RAM_LINE.item.item_name

CAVEMAN_ON = dict(caveman=Caveman.option_true, **UNITSANITY)
CAVEMAN_OFF = dict(caveman=Caveman.option_false, **UNITSANITY)

JOAN_1_TRANSPORT = Age2ItemData.AP_JOAN_1_TRANSPORT.item_name
JOAN_1_CROSSING = [location.global_name() for location in
                   (L.JOAN1_RECRUITS, L.JOAN1_RIVER_BURGUNDIANS,
                    L.JOAN1_RIVER_HIGHWAYMEN, L.JOAN1_VICTORY)]
JOAN_1_CROSSING.append("Complete " + L.JOAN1_VICTORY.scenario.scenario_name)

JOAN_2_CROSSING = [L.JOAN2_BRING_JOAN_TO_ORLEANS.global_name(),
                   L.JOAN2_FIND_FARMING_VILLAGE.global_name(), BRIDGE]

JOAN_5_SIEGE = [location.global_name() for location in
                (L.JOAN5_REFUGEE_1, L.JOAN5_REFUGEE_10, L.JOAN5_LOYALISTS,
                 L.JOAN5_RENDEZVOUS, L.JOAN5_ESCORT_JOAN, L.JOAN5_ESCORT_REFUGEES,
                 L.JOAN5_VICTORY)]
JOAN_5_SIEGE.append("Complete " + L.JOAN5_VICTORY.scenario.scenario_name)

GENGHIS_3_TRANSPORT = Age2ItemData.AP_GENGHIS_3_TRANSPORT.item_name
GENGHIS_3_FINDS = [L.GEN3_FIND_ENGINEERS.global_name(), L.GEN3_FIND_BOMBARDS.global_name()]


class TestJoan1Transports(Age2RuleTestBase):
    """The transports Joan 1 hands over are the only way across the river, and caveman turns
    them into a Militia that cannot swim."""

    campaigns = ["Joan of Arc"]
    starting_campaigns = ["Joan of Arc"]

    def test_caveman_asks_for_the_transport_line_on_top_of_the_item(self):
        self.build(**CAVEMAN_ON)
        stranded = self.state_without(TRANSPORTS)
        for name in JOAN_1_CROSSING:
            with self.subTest(location=name):
                self.assertFalse(self.can_reach(name, stranded))
                self.assertTrue(self.can_reach(name))

    def test_the_gate_still_wants_the_scenario_item(self):
        self.build(**CAVEMAN_ON)
        without_ships = self.state_without(JOAN_1_TRANSPORT)
        for name in JOAN_1_CROSSING:
            with self.subTest(location=name):
                self.assertFalse(self.can_reach(name, without_ships))

    def test_without_caveman_the_item_is_the_whole_requirement(self):
        self.build(**CAVEMAN_OFF)
        for name in JOAN_1_CROSSING:
            with self.subTest(location=name):
                self.assertEqual(self.item_requirements(name), {JOAN_1_TRANSPORT})

    def test_caveman_without_unitsanity_leaves_the_transports_alone(self):
        self.build(caveman=Caveman.option_true, unitsanity=Unitsanity.option_none)
        for name in JOAN_1_CROSSING:
            with self.subTest(location=name):
                self.assertEqual(self.item_requirements(name), {JOAN_1_TRANSPORT})


class TestJoan2Dock(Age2RuleTestBase):
    """The Dock half of Joan 2's crossing is a Transport Ship. The Trade Cart half is not
    gated: Joan 2 exempts its carts from caveman."""

    campaigns = ["Joan of Arc"]
    starting_campaigns = ["Joan of Arc"]

    def test_caveman_sinks_the_dock_route_without_the_transport_line(self):
        self.build(**CAVEMAN_ON)
        for name in JOAN_2_CROSSING:
            crossing = self.access_rule(name)
            with self.subTest(location=name):
                self.assertFalse(crossing(self.state_with(DOCK)))
                self.assertTrue(crossing(self.state_with(DOCK, TRANSPORTS)))

    def test_the_carts_cross_without_the_transport_line(self):
        """Joan 2 exempts its Trade Carts from caveman, so the cart half asks nothing more."""
        self.build(**CAVEMAN_ON)
        for name in JOAN_2_CROSSING:
            with self.subTest(location=name):
                self.assertTrue(self.access_rule(name)(self.state_with(CARTS)))

    def test_bringing_the_carts_to_orleans_is_still_the_item_alone(self):
        self.build(**CAVEMAN_ON)
        name = L.JOAN2_BRING_CARTS_TO_ORLEANS.global_name()
        self.assertEqual(self.item_requirements(name), {CARTS})
        self.assertTrue(self.access_rule(name)(self.state_with(CARTS)))

    def test_without_caveman_the_dock_alone_is_a_crossing(self):
        self.build(**CAVEMAN_OFF)
        for name in JOAN_2_CROSSING:
            with self.subTest(location=name):
                self.assertTrue(self.access_rule(name)(self.state_with(DOCK)))


class TestJoan3Boats(Age2RuleTestBase):
    """Joan 3's base sits across the water, and the boats that get there are a scenario item."""

    campaigns = ["Joan of Arc"]
    starting_campaigns = ["Joan of Arc"]

    def base_rule(self):
        joan_3 = self.world.rules.logic.for_scenario(Age2ScenarioData.AP_JOAN_3)
        return joan_3.has_base().resolve(self.world)

    def test_caveman_takes_the_base_away_without_the_transport_line(self):
        self.build(**CAVEMAN_ON)
        has_base = self.base_rule()
        self.assertTrue(has_base(self.state_without()))
        self.assertFalse(has_base(self.state_without(TRANSPORTS)))

    def test_without_caveman_the_scenario_item_is_enough(self):
        self.build(**CAVEMAN_OFF)
        has_base = self.base_rule()
        self.assertTrue(has_base(self.state_without(TRANSPORTS)))


class TestJoan5Siege(Age2RuleTestBase):
    """Joan 5 is a fixed force. Its refugees sit behind English lines and the army only opens a
    way through while it still has the siege it arrived with."""

    campaigns = ["Joan of Arc"]
    starting_campaigns = ["Joan of Arc"]

    def test_caveman_asks_for_a_siege_line_that_can_be_restored(self):
        self.build(**CAVEMAN_ON)
        unarmed = self.state_without(BOMBARDS, TREBUCHETS)
        for name in JOAN_5_SIEGE:
            with self.subTest(location=name):
                self.assertFalse(self.can_reach(name, unarmed))
                self.assertTrue(self.can_reach(name, self.state_without(BOMBARDS)))
                self.assertTrue(self.can_reach(name, self.state_without(TREBUCHETS)))

    def test_without_caveman_the_siege_lines_are_not_asked(self):
        self.build(**CAVEMAN_OFF)
        for name in JOAN_5_SIEGE:
            with self.subTest(location=name):
                asked = self.item_requirements(name)
                self.assertNotIn(BOMBARDS, asked)
                self.assertNotIn(TREBUCHETS, asked)


class TestJoan6Artillery(Age2RuleTestBase):
    """The French Artillery branch of besieging the Burgundian town counts siege the scenario
    hands over."""

    campaigns = ["Joan of Arc"]
    starting_campaigns = ["Joan of Arc"]

    def test_the_army_branch_names_a_restorable_siege_line_under_caveman(self):
        name = L.JOAN6_BURGUNDIAN_TOWN.global_name()
        self.build(**CAVEMAN_ON)
        asked = self.item_requirements(name)
        self.assertIn(BOMBARDS, asked)
        self.assertIn(TREBUCHETS, asked)
        self.build(**CAVEMAN_OFF)
        asked = self.item_requirements(name)
        self.assertNotIn(BOMBARDS, asked)
        self.assertNotIn(TREBUCHETS, asked)


class TestAttila2ScythianTroops(Age2RuleTestBase):
    """The Scythian Troops are rams, and a Militia does not knock the Roman walls down."""

    campaigns = ["Attila the Hun"]
    starting_campaigns = ["Attila the Hun"]

    def test_the_scythian_branch_names_the_ram_line_under_caveman(self):
        name = L.ATT2_BEAT_THE_ROMANS.global_name()
        self.build(**CAVEMAN_ON)
        self.assertIn(RAMS, self.item_requirements(name))
        self.build(**CAVEMAN_OFF)
        self.assertNotIn(RAMS, self.item_requirements(name))


class TestGenghis3Transport(Age2RuleTestBase):
    """Genghis 3's transport carries the engineers and the bombards off the far shore."""

    campaigns = ["Genghis Khan"]
    starting_campaigns = ["Genghis Khan"]

    def test_caveman_asks_for_the_transport_line_on_top_of_the_item(self):
        self.build(**CAVEMAN_ON)
        stranded = self.state_without(TRANSPORTS)
        for name in GENGHIS_3_FINDS:
            with self.subTest(location=name):
                self.assertFalse(self.can_reach(name, stranded))
                self.assertTrue(self.can_reach(name))

    def test_the_gate_still_wants_the_scenario_item(self):
        self.build(**CAVEMAN_ON)
        without_transport = self.state_without(GENGHIS_3_TRANSPORT)
        for name in GENGHIS_3_FINDS:
            with self.subTest(location=name):
                self.assertFalse(self.can_reach(name, without_transport))

    def test_without_caveman_the_item_is_the_whole_requirement(self):
        self.build(**CAVEMAN_OFF)
        for name in GENGHIS_3_FINDS:
            with self.subTest(location=name):
                self.assertEqual(self.item_requirements(name), {GENGHIS_3_TRANSPORT})


class TestScenarioCavemanExemptions(Age2RuleTestBase):
    """A scenario can name unit types caveman leaves alone there. Joan 2 and Genghis 4 name the
    Trade Cart, because a Militia cannot be driven to Orleans or past the Shah."""

    campaigns = ["Joan of Arc", "Genghis Khan"]
    starting_campaigns = ["Joan of Arc"]

    def granted(self, scenario, unit):
        logic = self.world.rules.logic.for_scenario(scenario)
        return logic.units.is_granted(unit).resolve(self.world)

    def test_every_scenario_names_its_exemptions(self):
        self.assertEqual(set(SCENARIO_TO_CAVEMAN_EXEMPTIONS), set(Age2ScenarioData))

    def test_an_exempt_cart_is_owned_the_moment_it_is_granted(self):
        self.build(**CAVEMAN_ON)
        without_carts = self.state_without(TRADE_CART_LINE)
        for scenario in (Age2ScenarioData.AP_JOAN_2, Age2ScenarioData.AP_GENGHIS_4):
            with self.subTest(scenario=scenario.scenario_name):
                is_granted = self.granted(scenario, Age2UnitData.TRADE_CART)
                self.assertTrue(is_granted(without_carts))

    def test_a_unit_the_scenario_does_not_exempt_still_asks_for_its_line(self):
        self.build(**CAVEMAN_ON)
        is_granted = self.granted(Age2ScenarioData.AP_JOAN_2, Age2UnitData.TRANSPORT_SHIP)
        self.assertTrue(is_granted(self.state_without()))
        self.assertFalse(is_granted(self.state_without(TRANSPORTS)))
