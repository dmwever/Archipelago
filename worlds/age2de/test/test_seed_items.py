import unittest

from . import bases
from ..Options import MarketTrade, PartnerTrade
from ..items import Items
from ..items.Items import Resource
from ..locations.Buildings import Age2BuildingData
from ..locations.connections.ScenarioResources import Tier
from ..locations.Units import Age2UnitData
from ..locations.VillagerJobs import Age2VillagerJobData
from .test_economy_catalog import (
    BASE_SWITCHES,
    DOCK_SEED,
    GOLD_MINERS,
    LUMBER_CAMP_SEED,
    LUMBERJACKS,
    MARKET_SEED,
    MULE_CART_SEED,
    RELICS,
    SCENARIO_WOOD,
    TRADE_COGS,
    VILLAGERS,
    ToyScenarioBase,
    building,
    job,
    partner,
    standing,
    tier,
    unit,
)

TOWN_CENTER_WOOD = "Starting Town Center Wood"
LUMBERJACK = job(Age2VillagerJobData.LUMBERJACK_MALE)
CAMPS_WITH_NO_TOWN_CENTER = (
    VILLAGERS,
    LUMBERJACK,
    building(Age2BuildingData.LUMBER_CAMP),
    building(Age2BuildingData.MULE_CART),
)

class TestWoodWithNoTownCenterNeedsASeedItem(ToyScenarioBase):

    def test_no_seed_item_yields_no_wood_at_any_strength(self):
        self.toy({})
        state = self.state(*CAMPS_WITH_NO_TOWN_CENTER, food=50)
        self.assertFalse(self.some(Resource.WOOD, state))
        self.assertFalse(self.easy(Resource.WOOD, state))

    def test_either_seed_item_yields_some_wood(self):
        for seed in (LUMBER_CAMP_SEED, MULE_CART_SEED):
            with self.subTest(seed=seed):
                self.toy({})
                state = self.state(*CAMPS_WITH_NO_TOWN_CENTER, seed, food=50)
                self.assertTrue(self.some(Resource.WOOD, state))

class TestAMiningCampIsFundedBySomeWood(ToyScenarioBase):
    MAP = {Tier.BASE: tier(gold_count=500)}

    def test_some_gold_once_another_route_yields_some_wood(self):
        self.toy(self.MAP)
        self.assertTrue(self.some(Resource.GOLD, self.state(*GOLD_MINERS, *LUMBERJACKS)))

    def test_no_gold_with_no_wood_route_running(self):
        self.toy(self.MAP)
        self.assertFalse(self.some(Resource.GOLD, self.state(*GOLD_MINERS)))

class TestTheTownCenterVariantChargesNothing(ToyScenarioBase):
    GATHERERS = (
        (Age2VillagerJobData.GOLD_MINER_MALE, "gold_count", Resource.GOLD),
        (Age2VillagerJobData.STONE_MINER_MALE, "stone_count", Resource.STONE),
        (Age2VillagerJobData.HUNTER_MALE, "hunt_count", Resource.FOOD),
        (Age2VillagerJobData.SHEPHERD_MALE, "herd_count", Resource.FOOD),
        (Age2VillagerJobData.FORAGER_MALE, "bush_count", Resource.FOOD),
        (Age2VillagerJobData.FISHERMAN_MALE, "shore_fish_count", Resource.FOOD),
        (Age2VillagerJobData.OYSTER_GATHERER_MALE, "oyster_count", Resource.GOLD),
    )
    TOWN_CENTER = building(Age2BuildingData.TOWN_CENTER)

    def test_every_gatherer_yields_some_at_a_town_center_with_no_seed_and_no_wood(self):
        for gatherer, field, resource in self.GATHERERS:
            with self.subTest(gatherer=gatherer.name):
                self.toy({Tier.BASE: tier(**{field: 500})})
                state = self.state(VILLAGERS, self.TOWN_CENTER, job(gatherer))
                self.assertFalse(self.some(Resource.WOOD, state))
                self.assertTrue(self.some(resource, state))

    def test_lumberjacks_yield_some_wood_at_a_town_center_with_no_seed(self):
        self.toy({})
        state = self.state(VILLAGERS, self.TOWN_CENTER, LUMBERJACK)
        self.assertTrue(self.some(Resource.WOOD, state))

class TestTheCogWoodBankExcludesTheDockSeed(ToyScenarioBase):

    def wood_bank(self, amount: int):
        bank = self.world.rules.logic.resources.has_amount(Resource.WOOD, amount)
        return bank.resolve(self.world)

    def test_the_dock_seed_and_one_more_wood_item_do_not_run_cogs(self):
        self.toy({})
        state = self.state(*TRADE_COGS, TOWN_CENTER_WOOD, gold=100)
        self.assertTrue(self.wood_bank(400)(state))
        self.assertFalse(self.easy(Resource.WOOD, state))

    def test_the_same_wood_as_starting_wood_does(self):
        self.toy({})
        state = self.state(*TRADE_COGS, TOWN_CENTER_WOOD, wood=150, gold=100)
        self.assertTrue(self.easy(Resource.WOOD, state))

    def test_the_same_wood_as_another_seed_item_does(self):
        self.toy({})
        state = self.state(*TRADE_COGS, TOWN_CENTER_WOOD, MARKET_SEED, gold=100)
        self.assertTrue(self.easy(Resource.WOOD, state))

class TestRelicsAreFundedBySomeWood(ToyScenarioBase):
    MAP = {Tier.OPEN: tier(relic_count=5)}

    def test_relics_yield_no_gold_with_no_wood_route(self):
        self.toy(self.MAP)
        self.assertFalse(self.some(Resource.GOLD, self.state(*RELICS)))

    def test_relics_yield_some_gold_beside_another_routes_wood_with_nothing_banked(self):
        self.toy(self.MAP)
        self.assertTrue(self.some(Resource.GOLD, self.state(*RELICS, *LUMBERJACKS)))

    def test_without_the_monk_unit_item_they_do_not(self):
        self.toy(self.MAP)
        state = self.state(building(Age2BuildingData.MONASTERY), *LUMBERJACKS)
        self.assertFalse(self.some(Resource.GOLD, state))

class TestTheMonkHasNoSeedItem(unittest.TestCase):

    def test_no_seed_item_funds_the_monastery(self):
        self.assertIsNone(Age2BuildingData.MONASTERY.seed_item)
        seeded = [item.type.seeds for item in Items.CATEGORY_TO_ITEMS[Items.SeedResources]]
        self.assertNotIn(Age2BuildingData.MONASTERY, seeded)

class TestTheMuleCartSeedsItsWoodAndBanksItsFood(ToyScenarioBase):
    MULE_CART = (
        VILLAGERS,
        LUMBERJACK,
        building(Age2BuildingData.MULE_CART),
        MULE_CART_SEED,
    )

    def test_the_seed_item_counts_as_its_wood_only(self):
        seed = Items.NAME_TO_ITEM[MULE_CART_SEED].type
        cost = Age2BuildingData.MULE_CART.cost
        self.assertEqual((Resource.WOOD, cost[Resource.WOOD]), (seed.type, seed.amount))
        self.assertGreater(cost[Resource.FOOD], 0)

    def test_the_seed_item_with_no_food_at_all_is_no_mule_cart(self):
        self.toy({})
        self.assertFalse(self.some(Resource.WOOD, self.state(*self.MULE_CART)))

    def test_banked_food_pays_the_rest(self):
        self.toy({})
        self.assertTrue(self.some(Resource.WOOD, self.state(*self.MULE_CART, food=50)))

class TestAStandingBuildingIsFree(ToyScenarioBase):
    COGS = (unit(Age2UnitData.TRADE_COG), partner(Age2BuildingData.DOCK))

    def test_a_standing_dock_runs_cogs_without_its_seed_item(self):
        self.toy({})
        state = self.state(*self.COGS, standing(Age2BuildingData.DOCK), wood=400, gold=100)
        self.assertTrue(self.easy(Resource.WOOD, state))

    def test_a_built_dock_asks_for_its_seed_item(self):
        self.toy({})
        dock = building(Age2BuildingData.DOCK)
        unseeded = self.state(*self.COGS, dock, wood=400, gold=100)
        self.assertFalse(self.easy(Resource.WOOD, unseeded))
        seeded = self.state(*self.COGS, dock, DOCK_SEED, wood=400, gold=100)
        self.assertTrue(self.easy(Resource.WOOD, seeded))

class TestWithNoPartnerTradeTheDockIsFundedLikeAMill(ToyScenarioBase):
    NO_PARTNER_TRADE = {"partner_trade": PartnerTrade.option_none}
    DOCK = building(Age2BuildingData.DOCK)
    FISHERMEN = (VILLAGERS, job(Age2VillagerJobData.FISHERMAN_MALE), DOCK)
    OYSTER_GATHERERS = (VILLAGERS, job(Age2VillagerJobData.OYSTER_GATHERER_MALE), DOCK)

    def test_fishermen_at_an_unseeded_dock_yield_some_food_beside_some_wood(self):
        self.toy({Tier.BASE: tier(shore_fish_count=500)}, **self.NO_PARTNER_TRADE)
        self.assertTrue(self.some(Resource.FOOD, self.state(*self.FISHERMEN, *LUMBERJACKS)))

    def test_fishermen_at_an_unseeded_dock_yield_nothing_with_no_wood_route(self):
        self.toy({Tier.BASE: tier(shore_fish_count=500)}, **self.NO_PARTNER_TRADE)
        self.assertFalse(self.some(Resource.FOOD, self.state(*self.FISHERMEN)))

    def test_oyster_gatherers_at_an_unseeded_dock_yield_some_gold_beside_some_wood(self):
        self.toy({Tier.BASE: tier(oyster_count=500)}, **self.NO_PARTNER_TRADE)
        state = self.state(*self.OYSTER_GATHERERS, *LUMBERJACKS)
        self.assertTrue(self.some(Resource.GOLD, state))

    def test_an_unseeded_dock_is_a_camp_at_scale(self):
        self.toy({Tier.BASE: tier(oyster_count=2000)}, **self.NO_PARTNER_TRADE)
        state = self.state(*BASE_SWITCHES, *self.OYSTER_GATHERERS, *LUMBERJACKS)
        self.assertTrue(self.easy(Resource.GOLD, state))

    def test_fishing_ships_drop_at_an_unseeded_dock(self):
        self.toy({Tier.BASE: tier(deep_fish_count=2000)}, **self.NO_PARTNER_TRADE)
        state = self.state(unit(Age2UnitData.FISHING_SHIP), self.DOCK, SCENARIO_WOOD)
        self.assertTrue(self.easy(Resource.FOOD, state))

    def test_with_partner_trade_fishermen_still_ask_for_the_dock_seed(self):
        self.toy({Tier.BASE: tier(shore_fish_count=500)})
        self.assertFalse(self.some(Resource.FOOD, self.state(*self.FISHERMEN, *LUMBERJACKS)))
        seeded = self.state(*self.FISHERMEN, *LUMBERJACKS, DOCK_SEED)
        self.assertTrue(self.some(Resource.FOOD, seeded))

class SeedPoolBase(bases.Age2RuleTestBase):
    campaigns = ["Attila the Hun"]
    starting_campaigns = ["Attila the Hun"]

    def pooled_seed_wood(self) -> dict[str, int]:
        seeds = {}
        held = [
            *self.multiworld.itempool,
            *self.multiworld.precollected_items[self.world.player],
        ]
        for item in held:
            payload = Items.NAME_TO_ITEM[item.name].type
            if isinstance(payload, Items.SeedResources) and payload.type is Resource.WOOD:
                seeds[item.name] = payload.amount
        return seeds

class TestSeedItemsArePooledOnlyWhereTheyFundSomething(SeedPoolBase):

    def test_no_partner_trade_and_no_market_trade_pool_neither_trade_seed(self):
        self.build(
            partner_trade=PartnerTrade.option_none,
            market_trade=MarketTrade.option_false,
        )
        pooled = self.pooled_seed_wood()
        self.assertNotIn(DOCK_SEED, pooled)
        self.assertNotIn(MARKET_SEED, pooled)
        self.assertEqual(545, self.world.pool.resources.targets[Resource.WOOD])

class TestStartingWoodSumsToAThousand(SeedPoolBase):
    SEED_WOOD = {
        (MarketTrade.option_true, PartnerTrade.option_allies): 780,
        (MarketTrade.option_true, PartnerTrade.option_allies_and_enemies): 780,
        (MarketTrade.option_false, PartnerTrade.option_allies): 780,
        (MarketTrade.option_false, PartnerTrade.option_allies_and_enemies): 780,
        (MarketTrade.option_true, PartnerTrade.option_none): 630,
        (MarketTrade.option_false, PartnerTrade.option_none): 455,
    }

    def test_every_combination_of_market_and_partner_trade(self):
        for (market_trade, partner_trade), seed_wood in self.SEED_WOOD.items():
            with self.subTest(market_trade=market_trade, partner_trade=partner_trade):
                self.build(market_trade=market_trade, partner_trade=partner_trade)
                pooled = sum(self.pooled_seed_wood().values())
                target = self.world.pool.resources.targets[Resource.WOOD]
                self.assertEqual(seed_wood, pooled)
                self.assertEqual(1000, pooled + target)

class TestAStandingFundedCampIsFree(ToyScenarioBase):
    """A camp funded by *some* wood is charged only where P1 puts one up.

    ADR-0002 has said a standing building is free since #24, and the seeded buildings honour it.
    The camps funded by *some* wood went on asking for wood nobody spends (#30)."""

    CAMPS = (
        (Age2BuildingData.MINING_CAMP, Age2VillagerJobData.GOLD_MINER_MALE,
         "gold_count", Resource.GOLD),
        (Age2BuildingData.MINING_CAMP, Age2VillagerJobData.STONE_MINER_MALE,
         "stone_count", Resource.STONE),
        (Age2BuildingData.MILL, Age2VillagerJobData.HUNTER_MALE,
         "hunt_count", Resource.FOOD),
        (Age2BuildingData.MILL, Age2VillagerJobData.SHEPHERD_MALE,
         "herd_count", Resource.FOOD),
        (Age2BuildingData.FOLWARK, Age2VillagerJobData.FORAGER_MALE,
         "bush_count", Resource.FOOD),
    )

    def test_a_standing_camp_yields_some_with_no_wood_route_running(self):
        for camp, gatherer, field, resource in self.CAMPS:
            with self.subTest(camp=camp.name, gatherer=gatherer.name):
                self.toy({Tier.BASE: tier(**{field: 500})})
                state = self.state(VILLAGERS, job(gatherer), standing(camp))
                self.assertFalse(self.some(Resource.WOOD, state))
                self.assertTrue(self.some(resource, state))

    def test_a_built_camp_still_asks_for_some_wood(self):
        for camp, gatherer, field, resource in self.CAMPS:
            with self.subTest(camp=camp.name, gatherer=gatherer.name):
                self.toy({Tier.BASE: tier(**{field: 500})})
                state = self.state(VILLAGERS, job(gatherer), building(camp))
                self.assertFalse(self.some(resource, state))

    def test_a_standing_monastery_collects_relics_with_no_wood_route(self):
        self.toy({Tier.OPEN: tier(relic_count=5)})
        state = self.state(standing(Age2BuildingData.MONASTERY), unit(Age2UnitData.MONK))
        self.assertFalse(self.some(Resource.WOOD, state))
        self.assertTrue(self.some(Resource.GOLD, state))

if __name__ == "__main__":
    unittest.main()
