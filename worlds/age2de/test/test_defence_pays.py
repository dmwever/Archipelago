"""Playtest #23: only ground worked at scale has to be held, and a defence pays for itself.

The toy scenario of `test_economy_catalog.py`, with the defence layer left real. There every leaf
fact is a switch and the defences are three more switches; here `_fortified`,
`can_hold_a_shoreline`, `can_build_multiple_tc` and `can_guard_boats` are what is under test, so
only the leaves beneath them are switched.
"""
import inspect
import unittest

from . import bases
from ..items.Items import Resource
from ..locations.Buildings import Age2BuildingData as B
from ..locations.connections.ScenarioResources import Tier
from ..locations.UnitLines import Age2UnitLineData as Line
from ..locations.Units import Age2UnitData as U
from ..locations.VillagerJobs import Age2VillagerJobData as Job
from ..logic.scenarios.ScenarioResourceLogic import ScenarioResourceLogic
from .test_economy_catalog import (
    BASE,
    BASE_SWITCHES,
    SCENARIO_WOOD,
    VILLAGERS,
    ToyScenarioBase,
    building,
    job,
    navy,
    standing,
    tier,
    unit,
)

WOOD_OF_SOME = job(Job.LUMBERJACK_MALE)
"""A lumberjack and the base's Town Center to drop at: the cheapest *some* on the map."""
STONE_OF_SOME = job(Job.STONE_MINER_MALE)


class DefenceToyBase(ToyScenarioBase):

    def switch_defences(self, switch) -> None:
        """Nothing: the defences are the subject here, not a switch under it."""


class TestOpenGroundIsFreeOfSomeAndHeldAtScale(DefenceToyBase):
    """A route of *some* walks a few villagers out, takes what it needs and comes home, so the
    ground costs it nothing. A route at scale stays there, so it has to hold it."""

    MINERS = (VILLAGERS, job(Job.GOLD_MINER_MALE), building(B.MINING_CAMP))
    CHURCH = building(B.FORTIFIED_CHURCH)
    """A strongpoint costing only wood, so this map needs no stone to pay for its defence."""

    def test_villagers_mine_open_gold_of_some_with_no_base_and_no_defence(self):
        self.toy({Tier.OPEN: tier(gold_count=500)})
        self.assertTrue(self.some(Resource.GOLD, self.state(*self.MINERS)))

    def test_the_same_ground_at_scale_yields_nothing_until_it_is_held(self):
        self.toy({Tier.OPEN: tier(gold_count=2000)})
        working = (*BASE_SWITCHES, *self.MINERS, WOOD_OF_SOME)
        self.assertFalse(self.easy(Resource.GOLD, self.state(*working)))
        self.assertTrue(self.easy(Resource.GOLD, self.state(*working, self.CHURCH)))

    def test_a_defence_it_cannot_pay_for_holds_nothing(self):
        self.toy({Tier.OPEN: tier(gold_count=2000)})
        unpaid = (*BASE_SWITCHES, *self.MINERS, self.CHURCH)
        self.assertFalse(self.easy(Resource.GOLD, self.state(*unpaid)))

    def test_ground_held_without_a_base_is_still_no_easy_source(self):
        self.toy({Tier.OPEN: tier(gold_count=2000)})
        held = (building(B.TOWN_CENTER), *self.MINERS, WOOD_OF_SOME, self.CHURCH)
        self.assertNotIn(BASE, held)
        self.assertFalse(self.easy(Resource.GOLD, self.state(*held)))


class TestAResourcePaysForItsOwnDefence(DefenceToyBase):
    """The cycle the first design of #23 could not break: stone only on open ground, every land
    defence costing stone, and no route seeding itself, so nothing could pay for the first wall.
    Strength is what breaks it - *some* stone off free open ground buys the Castle that then
    holds the same ground at scale."""

    QUARRY = (*BASE_SWITCHES, VILLAGERS, STONE_OF_SOME, building(B.MINING_CAMP))
    MAP = {Tier.OPEN: tier(stone_count=2000)}

    def test_the_only_stone_on_the_map_is_some_stone(self):
        self.toy(self.MAP)
        self.assertTrue(self.some(Resource.STONE, self.state(*self.QUARRY)))
        self.assertFalse(self.easy(Resource.STONE, self.state(*self.QUARRY)))

    def test_and_it_buys_the_castle_that_holds_the_rest(self):
        self.toy(self.MAP)
        self.assertTrue(self.easy(Resource.STONE, self.state(*self.QUARRY, building(B.CASTLE))))


class TestAStandingDefenceOpensNoGate(DefenceToyBase):
    """What a Castle on the map at the start guards is already the base's ground, summed into
    `Tier.BASE`. The gates ask only for defences P1 puts up and pays for."""

    MAP = {Tier.OPEN: tier(gold_count=2000), Tier.BASE: tier(stone_count=100)}
    MINERS = (*BASE_SWITCHES, VILLAGERS, job(Job.GOLD_MINER_MALE), STONE_OF_SOME,
              building(B.MINING_CAMP))

    def test_a_castle_standing_at_the_start_holds_no_open_ground(self):
        self.toy(self.MAP)
        standing_only = self.state(*self.MINERS, standing(B.CASTLE))
        self.assertFalse(self.easy(Resource.GOLD, standing_only))
        self.assertTrue(self.some(Resource.GOLD, standing_only))

    def test_one_p1_builds_and_pays_for_does(self):
        self.toy(self.MAP)
        self.assertTrue(self.easy(Resource.GOLD, self.state(*self.MINERS, building(B.CASTLE))))


class TestTheSecondTownCenterPays(DefenceToyBase):
    """Three places ask for more Town Centers - the open-ground strongpoint, the shoreline, and a
    camp - and all three inherit the payment from `can_build_multiple_tc` with no parameter."""

    SITES = (
        ("the open-ground strongpoint",
         {Tier.OPEN: tier(gold_count=2000), Tier.BASE: tier(stone_count=100)},
         job(Job.GOLD_MINER_MALE), Resource.GOLD),
        ("the shoreline",
         {Tier.OPEN: tier(shore_fish_count=2000), Tier.BASE: tier(stone_count=100)},
         job(Job.FISHERMAN_MALE), Resource.FOOD),
        ("a camp",
         {Tier.BASE: tier(hunt_count=2000, stone_count=100)},
         job(Job.HUNTER_MALE), Resource.FOOD),
    )
    WORKERS = (*BASE_SWITCHES, VILLAGERS, building(B.MINING_CAMP))

    def test_each_of_them_holds_only_with_some_wood_and_some_stone(self):
        for site, resources, gatherer, resource in self.SITES:
            self.toy(resources)
            for paid, expected in (((WOOD_OF_SOME, STONE_OF_SOME), True),
                                   ((WOOD_OF_SOME,), False),
                                   ((STONE_OF_SOME,), False)):
                with self.subTest(site=site, paid=paid):
                    state = self.state(*self.WORKERS, gatherer, *paid)
                    self.assertEqual(expected, self.easy(resource, state))


class TestTheNavyPaysPerLine(DefenceToyBase):
    """A guard pays for the line it actually fields. The cost groups of #19 and #21 charged every
    guarded route the same bundle, so a cheap line was taxed at a dear one's price."""

    NAVY_LINES = {
        Line.GALLEY_LINE: {Resource.WOOD, Resource.GOLD},
        Line.FIRE_GALLEY_LINE: {Resource.WOOD},
    }
    MAP = {Tier.OPEN: tier(deep_fish_count=2000)}
    BOATS = (unit(U.FISHING_SHIP), building(B.DOCK), SCENARIO_WOOD)

    def test_a_line_costing_wood_and_gold_asks_for_both(self):
        self.toy(self.MAP)
        wood_alone = self.state(*self.BOATS, navy(Line.GALLEY_LINE))
        self.assertFalse(self.easy(Resource.FOOD, wood_alone))

    def test_a_line_costing_only_wood_is_not_taxed_for_gold(self):
        self.toy(self.MAP)
        wood_alone = self.state(*self.BOATS, navy(Line.FIRE_GALLEY_LINE))
        self.assertTrue(self.easy(Resource.FOOD, wood_alone))

    def test_the_dearer_line_guards_once_its_gold_is_in(self):
        self.toy({Tier.OPEN: tier(deep_fish_count=2000), Tier.BASE: tier(gold_count=100)})
        miners = (VILLAGERS, job(Job.GOLD_MINER_MALE), building(B.MINING_CAMP))
        with_gold = self.state(*self.BOATS, navy(Line.GALLEY_LINE), *miners)
        self.assertTrue(self.easy(Resource.FOOD, with_gold))


class TestTheGatesTakeNoGuard(unittest.TestCase):
    """#23 reversed the guard parameter #19 and #21 introduced. A defence pays where it is asked,
    so nothing is threaded down to the gates - and a parameter creeping back is how the first
    design of this ticket spread through fourteen signatures."""

    def test_tier_gates_takes_only_the_kind_of_ground(self):
        self.assertEqual(["self", "kind"],
                         list(inspect.signature(ScenarioResourceLogic.tier_gates).parameters))

    def test_the_gates_of_some_take_nothing(self):
        gates = ScenarioResourceLogic.open_resource_gates
        self.assertEqual(["self"], list(inspect.signature(gates).parameters))


class TestTheUngatedRoutesReachNoGate(bases.Age2RuleTestBase):
    """A gate asks the ungated routes to price a defence, so no route in that group may read a
    gate. One filed in the wrong group is reached while its own question is still open, and
    `ScenarioQuestion` raises. Nothing else catches it: the group is hand-listed, which ADR-0003
    allows in this one place."""

    campaigns = ["Attila the Hun", "Joan of Arc", "Genghis Khan"]
    starting_campaigns = ["Attila the Hun"]

    def test_every_scenario_answers_every_economy_question(self):
        self.build()
        logic = self.world.rules.logic
        state = self.state_without()
        for scenario in logic.scenarios:
            for resource in Resource:
                with self.subTest(scenario=scenario.scenario.name, resource=resource.name):
                    scenario.economy.has_some_source(resource).resolve(self.world)(state)
                    scenario.economy.has_easy_source(resource).resolve(self.world)(state)
        self.assertEqual(set(), logic.scenario_answers_open)

    def test_the_two_groups_partition_the_catalog(self):
        self.build()
        for scenario in self.world.rules.logic.scenarios:
            economy = scenario.economy
            ungated = [route.name for route in economy.ungated_routes()]
            gated = [route.name for route in economy.gated_routes()]
            with self.subTest(scenario.scenario.name):
                self.assertEqual([route.name for route in economy.economy_routes().routes],
                                 ungated + gated)
                self.assertEqual(set(), set(ungated) & set(gated))


if __name__ == "__main__":
    unittest.main()
