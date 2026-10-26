import contextlib
import unittest
from unittest import mock

from BaseClasses import CollectionState
from rule_builder.rules import False_, Has, True_

from . import bases
from ..Options import MarketTrade
from ..items.Items import Resource
from ..locations.Buildings import Age2BuildingData as B
from ..locations.connections.ScenarioResources import (
    COUNT_FIELDS,
    ScenarioResourceCount,
    ScenarioResourceDemand,
    Tier,
)
from ..locations.Scenarios import Age2ScenarioData
from ..locations.UnitLines import Age2UnitLineData as Line
from ..locations.Units import Age2UnitData as U
from ..locations.VillagerJobs import Age2VillagerJobData as Job

BASE = "switch: base"
VILLAGERS = "switch: villagers"
MORE_TCS = "switch: more Town Centers"
SHORELINE_HELD = "switch: shoreline held"
FORTIFIED = "switch: fortified"
ENEMY_CAMP_TAKEN = "switch: enemy camp taken"
SCENARIO_WOOD = "switch: scenario wood"

DEMAND = ScenarioResourceDemand(gold=1000, stone=1000, food=1000)


def building(which: B) -> str:
    """This building is P1's to put up - the buildable half of "standing or buildable"."""
    return f"switch: building {which.name}"


def standing(which: B) -> str:
    """This building is on the map at the start. A defence standing opens no gate, so the two
    halves are separate switches here."""
    return f"switch: standing {which.name}"


def navy(which: Line) -> str:
    return f"switch: navy {which.line_name}"


def job(which: Job) -> str:
    return f"switch: job {which.name}"


def unit(which: U) -> str:
    return f"switch: unit {which.name}"


def partner(which: B) -> str:
    return f"switch: partner {which.name}"


NAVY = navy(Line.GALLEY_LINE)


def tier(**counts: int) -> ScenarioResourceCount:
    return ScenarioResourceCount(**{
        name: counts[name] if name in counts else 0
        for name in COUNT_FIELDS
    })


BASE_SWITCHES = (BASE, building(B.TOWN_CENTER))
LUMBERJACKS = (VILLAGERS, job(Job.LUMBERJACK_MALE), building(B.LUMBER_CAMP))
GOLD_MINERS = (VILLAGERS, job(Job.GOLD_MINER_MALE), building(B.MINING_CAMP))
TRADE_COGS = (unit(U.TRADE_COG), partner(B.DOCK), building(B.DOCK))
TRADE_CARTS = (unit(U.TRADE_CART), partner(B.MARKET), building(B.MARKET))
FISHING_SHIPS = (unit(U.FISHING_SHIP), building(B.DOCK))
RELICS = (building(B.MONASTERY), unit(U.MONK))


class ToyScenarioBase(bases.Age2RuleTestBase):
    campaigns = ["Attila the Hun"]
    starting_campaigns = ["Attila the Hun"]
    SCENARIO = Age2ScenarioData.AP_ATTILA_6
    NAVY_LINES: dict[Line, set[Resource]] = {Line.GALLEY_LINE: {Resource.WOOD, Resource.GOLD}}
    """The navy lines this toy can field, and what each one costs to keep coming. One line by
    default, so `NAVY` is the single switch that puts warships on the water."""

    def toy(self, resources: dict[Tier, ScenarioResourceCount], **options) -> None:
        self.build(**options)
        scenario = self.world.rules.logic.for_scenario(self.SCENARIO)
        self.scenario = scenario
        economy = scenario.economy
        starting_state = scenario.starting_state
        stack = contextlib.ExitStack()
        self.addCleanup(stack.close)
        self.addCleanup(self.world.rules.logic.scenario_answers.clear)

        def switch(target, name, answer):
            stack.enter_context(mock.patch.object(target, name, side_effect=answer))

        switch(scenario, "has_base", lambda: Has(BASE))
        switch(scenario, "has_vils", lambda: Has(VILLAGERS))
        switch(scenario, "has_building_structurally",
               lambda which: Has(building(which)) | Has(standing(which)))
        switch(scenario, "obtains_unit", lambda which: False_())
        switch(scenario, "has_water_access", lambda: True_())
        switch(scenario.buildings, "can_build_structurally", lambda which: Has(building(which)))
        switch(scenario.buildings, "can_build_tc", lambda: Has(building(B.TOWN_CENTER)))
        switch(scenario.ages, "has_reached", lambda age: True_())
        switch(scenario.player_logic, "can_reach_partner", lambda which: Has(partner(which)))
        switch(scenario.units, "can_field_structurally",
               lambda line: Has(navy(line)) if line in self.NAVY_LINES else False_())
        switch(scenario.units, "resources_to_sustain",
               lambda line: self.NAVY_LINES.get(line, set()))
        switch(economy, "has_job", lambda which: Has(job(which)))
        self.switch_defences(switch)
        switch(scenario.logic.units, "has_unit_items", lambda which: Has(unit(which)))
        stack.enter_context(mock.patch.object(
            starting_state,
            "must_steal_base",
            Has(ENEMY_CAMP_TAKEN),
        ))
        stack.enter_context(mock.patch.object(
            starting_state,
            "easy_resource_sources",
            {
                resource: Has(SCENARIO_WOOD) if resource is Resource.WOOD else False_()
                for resource in Resource
            },
        ))
        stack.enter_context(mock.patch.object(
            starting_state,
            "some_resource_sources",
            {resource: False_() for resource in Resource},
        ))
        stack.enter_context(mock.patch.dict(self.SCENARIO.resources, resources, clear=True))
        stack.enter_context(mock.patch.object(self.SCENARIO, "demand", DEMAND))
        stack.enter_context(mock.patch.object(economy, "demand", DEMAND))
        stack.enter_context(mock.patch.object(
            economy,
            "counts",
            ScenarioResourceCount(**{
                name: sum(getattr(counts, name) for counts in resources.values())
                for name in COUNT_FIELDS
            }),
        ))
        self.world.rules.logic.scenario_answers.clear()

    def switch_defences(self, switch) -> None:
        """The defence layer as three switches, so a test about gathering says what it holds
        without building anything. `test_defence_pays.py` leaves these real: there the defences
        themselves are what is under test."""
        switch(self.scenario.buildings, "can_build_multiple_tc", lambda: Has(MORE_TCS))
        switch(self.scenario.buildings, "can_hold_a_shoreline", lambda: Has(SHORELINE_HELD))
        switch(self.scenario.buildings, "_fortified", lambda: Has(FORTIFIED))

    def state(self, *switches: str, wood: int = 0, gold: int = 0) -> CollectionState:
        state = CollectionState(self.multiworld)
        held = state.prog_items[self.world.player]
        for name in switches:
            held[name] = 1
        held["+50 Starting Wood"] += wood // 50
        held["+50 Starting Gold"] += gold // 50
        return state

    def easy(self, resource: Resource, state: CollectionState) -> bool:
        return bool(self.scenario.economy.has_easy_source(resource).resolve(self.world)(state))

    def some(self, resource: Resource, state: CollectionState) -> bool:
        return bool(self.scenario.economy.has_some_source(resource).resolve(self.world)(state))

    def running(self, state: CollectionState) -> set[str]:
        economy = self.scenario.economy.has_economy_routes().resolve(self.world)
        return {economy.routes[index].name for index in economy.running(state)}


class TestLumberjacksStartAnEconomyWithNoBase(ToyScenarioBase):
    CHAIN = (*LUMBERJACKS, *TRADE_COGS, *FISHING_SHIPS)
    MAP = {Tier.BASE: tier(gold_count=500, deep_fish_count=2000)}

    def assert_chain(self, *seed: str, gold: int = 0) -> None:
        with_lumberjacks = self.state(*self.CHAIN, *seed, gold=gold)
        for resource in (Resource.WOOD, Resource.GOLD, Resource.FOOD):
            with self.subTest(resource=resource.name, lumberjacks=True):
                self.assertTrue(self.easy(resource, with_lumberjacks))
        without = [name for name in (*self.CHAIN, *seed) if name != job(Job.LUMBERJACK_MALE)]
        without_lumberjacks = self.state(*without, gold=gold)
        for resource in (Resource.WOOD, Resource.GOLD, Resource.FOOD):
            with self.subTest(resource=resource.name, lumberjacks=False):
                self.assertFalse(self.easy(resource, without_lumberjacks))

    def test_banked_gold_seeds_the_cogs(self):
        self.toy(self.MAP)
        self.assertTrue(self.world.pool.resources.totals[Resource.GOLD] >= 100)
        self.assert_chain(gold=100)

    def test_villagers_mining_some_gold_seed_the_cogs(self):
        self.toy(self.MAP)
        self.assert_chain(*GOLD_MINERS)


class TestNoBaseAndNoPartnerDockIsNoEconomy(ToyScenarioBase):

    def test_no_easy_source_holds(self):
        self.toy({Tier.BASE: tier(gold_count=500, deep_fish_count=2000)})
        everything = [
            name for name in (*LUMBERJACKS, *GOLD_MINERS, *TRADE_COGS, *FISHING_SHIPS, *TRADE_CARTS)
            if name != partner(B.DOCK)
        ]
        state = self.state(*everything, wood=400, gold=100)
        for resource in Resource:
            with self.subTest(resource=resource.name):
                self.assertFalse(self.easy(resource, state))


class TestTradeCartsRunOnCogWood(ToyScenarioBase):

    def test_trade_carts_run_with_no_base(self):
        self.toy({})
        state = self.state(*TRADE_COGS, *TRADE_CARTS, wood=400, gold=100)
        self.assertIn("Trade Carts", self.running(state))


class TestFishingShipsNeedWoodAtScale(ToyScenarioBase):
    MAP = {Tier.BASE: tier(deep_fish_count=2000)}

    def test_banked_wood_no_longer_crews_fishing_ships(self):
        self.toy(self.MAP)
        state = self.state(*BASE_SWITCHES, *FISHING_SHIPS, VILLAGERS, wood=100)
        self.assertFalse(self.easy(Resource.FOOD, state))

    def test_wood_at_scale_crews_them(self):
        self.toy(self.MAP)
        state = self.state(*FISHING_SHIPS, SCENARIO_WOOD)
        self.assertTrue(self.easy(Resource.FOOD, state))


class TestFarmingNeedsABase(ToyScenarioBase):
    FARMS = (building(B.FARM), job(Job.FARMER_MALE), building(B.MILL), VILLAGERS)

    def test_farming_without_a_base_is_not_easy_food(self):
        self.toy({})
        state = self.state(*self.FARMS, *TRADE_COGS, wood=400, gold=100)
        self.assertTrue(self.easy(Resource.WOOD, state))
        self.assertFalse(self.easy(Resource.FOOD, state))

    def test_farming_with_a_base_and_wood_at_scale_is(self):
        self.toy({})
        state = self.state(*self.FARMS, *BASE_SWITCHES, *TRADE_COGS, wood=400, gold=100)
        self.assertTrue(self.easy(Resource.FOOD, state))


class TestMarketTradeSeededByWoodAtScale(ToyScenarioBase):
    MAP = {Tier.BASE: tier(gold_count=2000, hunt_count=2000)}
    FINITE_SOURCES = (*BASE_SWITCHES, *GOLD_MINERS, job(Job.HUNTER_MALE), building(B.MILL))

    def test_wood_at_scale_seeds_market_trade(self):
        self.toy(self.MAP, market_trade=MarketTrade.option_true)
        state = self.state(SCENARIO_WOOD, building(B.MARKET))
        self.assertTrue(self.easy(Resource.STONE, state))

    def test_easy_gold_and_raw_food_alone_do_not(self):
        self.toy(self.MAP, market_trade=MarketTrade.option_true)
        state = self.state(*self.FINITE_SOURCES, building(B.MARKET))
        self.assertTrue(self.easy(Resource.GOLD, state))
        self.assertTrue(self.easy(Resource.FOOD, state))
        self.assertFalse(self.easy(Resource.STONE, state))


class TestFishingShipGold(ToyScenarioBase):

    def test_boats_bring_easy_gold_with_no_base_and_no_mining_camp(self):
        for field in ("oyster_count", "whale_count"):
            with self.subTest(field=field):
                self.toy({Tier.BASE: tier(**{field: 2000})})
                state = self.state(*FISHING_SHIPS, SCENARIO_WOOD)
                self.assertTrue(self.easy(Resource.GOLD, state))
                self.assertFalse(self.easy(Resource.GOLD, self.state(*FISHING_SHIPS)))

    def test_the_maps_amount_must_clear_demand(self):
        for field in ("oyster_count", "whale_count"):
            with self.subTest(field=field):
                self.toy({Tier.BASE: tier(**{field: 500})})
                state = self.state(*FISHING_SHIPS, SCENARIO_WOOD)
                self.assertFalse(self.easy(Resource.GOLD, state))


class TestCogWoodBank(ToyScenarioBase):

    def test_fifty_banked_wood_does_not_seed_cogs_and_four_hundred_does(self):
        self.toy({})
        self.assertTrue(self.world.pool.resources.totals[Resource.WOOD] >= 400)
        self.assertFalse(self.easy(Resource.WOOD, self.state(*TRADE_COGS, wood=50, gold=100)))
        self.assertTrue(self.easy(Resource.WOOD, self.state(*TRADE_COGS, wood=400, gold=100)))


class TestRelics(ToyScenarioBase):

    def test_relics_alone_never_make_easy_gold(self):
        self.toy({Tier.BASE: tier(relic_count=50)})
        state = self.state(*RELICS, *BASE_SWITCHES, VILLAGERS, building(B.MINING_CAMP), FORTIFIED)
        self.assertFalse(self.easy(Resource.GOLD, state))

    def test_relics_yield_some_gold_with_no_villagers_or_gold_dropsite(self):
        """And none of a defence either: relics are a route of *some*, so the open ground they
        lie on is free."""
        self.toy({Tier.OPEN: tier(relic_count=5)})
        self.assertFalse(self.some(Resource.GOLD, self.state(building(B.MONASTERY))))
        self.assertTrue(self.some(Resource.GOLD, self.state(*RELICS)))


class TestNavalGuardOverDeepFish(ToyScenarioBase):
    MAP = {Tier.OPEN: tier(deep_fish_count=2000), Tier.BASE: tier(relic_count=1)}

    def test_navy_gold_of_some_guards_the_boats(self):
        self.toy(self.MAP)
        state = self.state(*FISHING_SHIPS, SCENARIO_WOOD, NAVY, *RELICS)
        self.assertFalse(self.easy(Resource.GOLD, state))
        self.assertTrue(self.easy(Resource.FOOD, state))

    def test_banked_gold_does_not_guard_them(self):
        self.toy(self.MAP)
        state = self.state(*FISHING_SHIPS, SCENARIO_WOOD, NAVY, gold=250)
        self.assertFalse(self.easy(Resource.FOOD, state))


class TestNavalGuardOverTheShoreline(ToyScenarioBase):
    FEW_LUMBERJACKS = (VILLAGERS, job(Job.LUMBERJACK_MALE))
    LITTLE_MINING = (VILLAGERS, job(Job.GOLD_MINER_MALE))

    def shore(self, field: str, gatherer: Job, resource: Resource) -> None:
        self.toy({Tier.OPEN: tier(**{field: 2000}), Tier.BASE: tier(gold_count=100)})
        workers = (*BASE_SWITCHES, VILLAGERS, job(gatherer), building(B.DOCK), NAVY)
        guarded = self.state(*workers, *self.FEW_LUMBERJACKS, *self.LITTLE_MINING)
        self.assertFalse(self.easy(Resource.WOOD, guarded))
        self.assertTrue(self.easy(resource, guarded))
        banked = self.state(*workers, wood=400, gold=250)
        self.assertFalse(self.easy(resource, banked))

    def test_navy_of_some_guards_villagers_fishing_the_shore(self):
        self.shore("shore_fish_count", Job.FISHERMAN_MALE, Resource.FOOD)

    def test_navy_of_some_guards_villagers_gathering_shore_oysters(self):
        self.shore("oyster_count", Job.OYSTER_GATHERER_MALE, Resource.GOLD)


class TestPerSourceCamps(ToyScenarioBase):
    HUNTERS = (*BASE_SWITCHES, VILLAGERS, job(Job.HUNTER_MALE))

    def test_hunt_without_a_camp_does_not_count(self):
        self.toy({Tier.BASE: tier(hunt_count=2000)})
        self.assertFalse(self.easy(Resource.FOOD, self.state(*self.HUNTERS)))

    def test_hunt_counts_with_each_of_its_camps(self):
        for camp in (building(B.MILL), building(B.FOLWARK), building(B.MULE_CART), MORE_TCS):
            with self.subTest(camp=camp):
                self.toy({Tier.BASE: tier(hunt_count=2000)})
                self.assertTrue(self.easy(Resource.FOOD, self.state(*self.HUNTERS, camp)))

    def test_herding_counts_with_the_bases_town_center_alone(self):
        self.toy({Tier.BASE: tier(herd_count=2000)})
        state = self.state(*BASE_SWITCHES, VILLAGERS, job(Job.SHEPHERD_MALE))
        self.assertTrue(self.easy(Resource.FOOD, state))

    def test_farms_ask_no_camp(self):
        self.toy({})
        farmers = (VILLAGERS, building(B.FARM), job(Job.FARMER_MALE))
        state = self.state(*BASE_SWITCHES, *farmers, SCENARIO_WOOD)
        self.assertTrue(self.easy(Resource.FOOD, state))


class TestACampGatesItsOwnTerm(ToyScenarioBase):
    OYSTER_GATHERERS = (*BASE_SWITCHES, VILLAGERS, job(Job.OYSTER_GATHERER_MALE))

    def test_a_mining_camp_does_not_let_shore_oysters_count(self):
        self.toy({Tier.BASE: tier(oyster_count=2000)})
        state = self.state(*self.OYSTER_GATHERERS, building(B.MINING_CAMP))
        self.assertFalse(self.easy(Resource.GOLD, state))

    def test_their_own_camp_does(self):
        self.toy({Tier.BASE: tier(oyster_count=2000)})
        state = self.state(*self.OYSTER_GATHERERS, building(B.DOCK))
        self.assertTrue(self.easy(Resource.GOLD, state))


class TestHerdGround(ToyScenarioBase):
    SHEPHERDS = (*BASE_SWITCHES, VILLAGERS, job(Job.SHEPHERD_MALE))

    def test_herd_counts_from_open_ground_with_no_fortification(self):
        self.toy({Tier.OPEN: tier(herd_count=2000)})
        self.assertTrue(self.easy(Resource.FOOD, self.state(*self.SHEPHERDS)))

    def test_herd_never_counts_from_ally_ground(self):
        self.toy({Tier.ALLY: tier(herd_count=2000)})
        state = self.state(*self.SHEPHERDS, FORTIFIED, ENEMY_CAMP_TAKEN)
        self.assertFalse(self.easy(Resource.FOOD, state))


class TestRoutesOfSomeStillWaitOnAnEnemyCamp(ToyScenarioBase):
    """Open ground is free to a route of *some*, but an enemy's camp is not: nobody walks in and
    takes what they need while it is still theirs."""

    def test_gold_inside_an_enemy_camp_waits_for_its_gate(self):
        self.toy({Tier.ENEMY: tier(gold_count=500)})
        self.assertFalse(self.some(Resource.GOLD, self.state(*GOLD_MINERS)))
        self.assertTrue(self.some(Resource.GOLD, self.state(*GOLD_MINERS, ENEMY_CAMP_TAKEN)))


class TestVillagersAndFishingShipsSumTogether(ToyScenarioBase):
    MAP = {Tier.BASE: tier(hunt_count=600, deep_fish_count=600)}
    WORKERS = (*BASE_SWITCHES, VILLAGERS, job(Job.HUNTER_MALE), building(B.MILL), *FISHING_SHIPS)

    def test_land_food_and_deep_fish_clear_demand_together(self):
        self.toy(self.MAP)
        self.assertTrue(self.easy(Resource.FOOD, self.state(*self.WORKERS, SCENARIO_WOOD)))

    def test_not_without_wood_at_scale(self):
        self.toy(self.MAP)
        self.assertFalse(self.easy(Resource.FOOD, self.state(*self.WORKERS)))


class TestTheShoreIsCountedOnce(ToyScenarioBase):

    def test_villagers_and_boats_on_one_shore_do_not_double_it(self):
        self.toy({Tier.BASE: tier(shore_fish_count=600)})
        fishermen = (*BASE_SWITCHES, VILLAGERS, job(Job.FISHERMAN_MALE), building(B.MILL))
        state = self.state(*fishermen, *FISHING_SHIPS, SCENARIO_WOOD)
        self.assertFalse(self.easy(Resource.FOOD, state))


class TestFishingShipsWorkShoreFish(ToyScenarioBase):

    def test_boats_bring_shore_fish_in(self):
        self.toy({Tier.BASE: tier(shore_fish_count=2000)})
        self.assertTrue(self.easy(Resource.FOOD, self.state(*FISHING_SHIPS, SCENARIO_WOOD)))


class TestFishTraps(ToyScenarioBase):

    def test_fish_traps_are_easy_food_with_no_fish_on_the_map(self):
        self.toy({})
        state = self.state(*FISHING_SHIPS, building(B.FISH_TRAP), SCENARIO_WOOD)
        self.assertTrue(self.easy(Resource.FOOD, state))
        without_wood = self.state(*FISHING_SHIPS, building(B.FISH_TRAP))
        self.assertFalse(self.easy(Resource.FOOD, without_wood))


if __name__ == "__main__":
    unittest.main()
