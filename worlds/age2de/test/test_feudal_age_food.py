from . import bases
from .test_age_price import AgePriceTestBase
from ..Options import ExistingTechs, PartnerTrade, ShuffleVillager, Unitsanity
from ..items.Items import CATEGORY_TO_ITEMS, Age2ItemData, Resource, StartingResources
from ..locations.Ages import Age2AgeData
from ..locations.Scenarios import Age2ScenarioData

FEUDAL_AGE_FOOD = "Feudal Age Food"


class FeudalAgeFoodPoolBase(bases.Age2RuleTestBase):

    def pooled(self, campaign: str, **options) -> bool:
        self.campaigns = [campaign]
        self.starting_campaigns = [campaign]
        self.build(**options)
        return FEUDAL_AGE_FOOD in {item.name for item in self.multiworld.itempool}


class TestFeudalAgeFoodIsPooledOnlyWhereARouteWaitsOnFeudal(FeudalAgeFoodPoolBase):

    def test_attila_1_starts_in_the_dark_age_with_a_trade_partner(self):
        self.assertTrue(self.pooled(
            "Attila the Hun",
            partner_trade=PartnerTrade.option_allies_and_enemies,
        ))

    def test_attila_1_has_water_for_fish_traps_with_partner_trade_off(self):
        self.assertTrue(self.pooled("Attila the Hun", partner_trade=PartnerTrade.option_none))

    def test_genghis_2_has_neither_water_nor_partner_trade(self):
        self.assertFalse(self.pooled("Genghis Khan", partner_trade=PartnerTrade.option_none))

    def test_genghis_2_trades_with_the_kara_khitai_under_allies_and_enemies(self):
        self.assertTrue(self.pooled(
            "Genghis Khan",
            partner_trade=PartnerTrade.option_allies_and_enemies,
        ))

    def test_genghis_2_waits_on_feudal_for_market_trade(self):
        self.assertTrue(self.pooled(
            "Genghis Khan",
            partner_trade=PartnerTrade.option_none,
            market_trade=True,
        ))

    def test_genghis_2_has_nothing_waiting_on_feudal_with_market_trade_off(self):
        self.assertFalse(self.pooled(
            "Genghis Khan",
            partner_trade=PartnerTrade.option_none,
            market_trade=False,
        ))

    def test_every_joan_scenario_starts_in_feudal_or_later(self):
        self.assertFalse(self.pooled(
            "Joan of Arc",
            partner_trade=PartnerTrade.option_allies_and_enemies,
        ))

    def test_under_start_in_dark_age_joan_starts_below_feudal(self):
        self.assertTrue(self.pooled(
            "Joan of Arc",
            partner_trade=PartnerTrade.option_none,
            existing_techs=ExistingTechs.option_start_in_dark_age,
        ))

    def test_one_per_world(self):
        self.pooled("Attila the Hun", partner_trade=PartnerTrade.option_allies_and_enemies)
        names = [item.name for item in self.multiworld.itempool]
        self.assertEqual(1, names.count(FEUDAL_AGE_FOOD))


class TestTheFeudalPriceTakesFeudalAgeFood(AgePriceTestBase):

    def feudal_price_holds(self, state) -> bool:
        scourge = self.scenario_logic(Age2ScenarioData.AP_ATTILA_1)
        return self.holds(scourge.ages.can_pay_for(Age2AgeData.FEUDAL), state)

    def test_with_no_food_route_feudal_age_food_pays_it(self):
        self.build_starving(easy=(Resource.FOOD,), some=(Resource.FOOD,),
                            partner_trade=PartnerTrade.option_allies_and_enemies)
        self.assertTrue(self.feudal_price_holds(self.state_with(FEUDAL_AGE_FOOD)))

    def test_with_no_food_route_and_no_feudal_age_food_nothing_pays_it(self):
        self.build_starving(easy=(Resource.FOOD,), some=(Resource.FOOD,),
                            partner_trade=PartnerTrade.option_allies_and_enemies)
        self.assertFalse(self.feudal_price_holds(self.state_without(FEUDAL_AGE_FOOD)))


class TestAttila1CogsWaitOnFeudal(bases.Age2RuleTestBase):
    campaigns = ["Attila the Hun"]
    starting_campaigns = ["Attila the Hun"]

    FOOD_PROFESSIONS = (
        Age2ItemData.PROFESSION_FORAGER.item_name,
        Age2ItemData.PROFESSION_HUNTER.item_name,
        Age2ItemData.PROFESSION_SHEPHERD.item_name,
        Age2ItemData.PROFESSION_HERDER.item_name,
        Age2ItemData.PROFESSION_FISHERMAN.item_name,
        Age2ItemData.PROFESSION_FARMER.item_name,
    )

    def setUp(self) -> None:
        super().setUp()
        self.build(
            partner_trade=PartnerTrade.option_allies_and_enemies,
            shuffle_villager=ShuffleVillager.option_include_professions,
            unitsanity=Unitsanity.option_all,
        )
        scourge = self.world.rules.logic.for_scenario(Age2ScenarioData.AP_ATTILA_1)
        self.economy = scourge.economy.has_economy_routes().resolve(self.world)
        fishing_ships = scourge.economy.has_fishing_ships().resolve(self.world)
        banked_food = [item.item_name for item in CATEGORY_TO_ITEMS[StartingResources]
                       if item.type.type is Resource.FOOD]
        self.no_food = (*self.FOOD_PROFESSIONS, *fishing_ships.item_dependencies(), *banked_food,
                        FEUDAL_AGE_FOOD)

    def cogs_run(self, *given: str) -> bool:
        state = self.state_without(*[name for name in self.no_food if name not in given])
        return any(self.economy.routes[index].name.startswith("Trade Cogs")
                   for index in self.economy.running(state))

    def test_with_no_food_route_and_no_banked_food_no_cogs_run(self):
        self.assertFalse(self.cogs_run())

    def test_hunters_of_some_pay_the_feudal_price(self):
        self.assertTrue(self.cogs_run(Age2ItemData.PROFESSION_HUNTER.item_name))

    def test_foragers_of_some_pay_the_feudal_price(self):
        self.assertTrue(self.cogs_run(Age2ItemData.PROFESSION_FORAGER.item_name))

    def test_feudal_age_food_pays_the_feudal_price(self):
        self.assertTrue(self.cogs_run(FEUDAL_AGE_FOOD))


class TestAttila1MarketTradeWaitsOnFeudal(bases.Age2RuleTestBase):
    campaigns = ["Attila the Hun"]
    starting_campaigns = ["Attila the Hun"]

    FOOD_PROFESSIONS = (
        Age2ItemData.PROFESSION_FORAGER.item_name,
        Age2ItemData.PROFESSION_HUNTER.item_name,
        Age2ItemData.PROFESSION_SHEPHERD.item_name,
        Age2ItemData.PROFESSION_HERDER.item_name,
        Age2ItemData.PROFESSION_FISHERMAN.item_name,
        Age2ItemData.PROFESSION_FARMER.item_name,
    )

    def setUp(self) -> None:
        super().setUp()
        self.build(
            market_trade=True,
            partner_trade=PartnerTrade.option_allies_and_enemies,
            shuffle_villager=ShuffleVillager.option_include_professions,
            unitsanity=Unitsanity.option_all,
        )
        scourge = self.world.rules.logic.for_scenario(Age2ScenarioData.AP_ATTILA_1)
        self.economy = scourge.economy.has_economy_routes().resolve(self.world)
        fishing_ships = scourge.economy.has_fishing_ships().resolve(self.world)
        banked_food = [item.item_name for item in CATEGORY_TO_ITEMS[StartingResources]
                       if item.type.type is Resource.FOOD]
        self.no_food = (*self.FOOD_PROFESSIONS, *fishing_ships.item_dependencies(), *banked_food,
                        FEUDAL_AGE_FOOD)

    def market_trade_runs(self, *given: str) -> bool:
        state = self.state_without(*[name for name in self.no_food if name not in given])
        return any(self.economy.routes[index].name.startswith("Market Trade")
                   for index in self.economy.running(state))

    def test_with_no_food_route_and_no_feudal_age_food_market_trade_does_not_run(self):
        self.assertFalse(self.market_trade_runs())

    def test_hunters_of_some_pay_the_feudal_price(self):
        self.assertTrue(self.market_trade_runs(Age2ItemData.PROFESSION_HUNTER.item_name))

    def test_foragers_of_some_pay_the_feudal_price(self):
        self.assertTrue(self.market_trade_runs(Age2ItemData.PROFESSION_FORAGER.item_name))

    def test_feudal_age_food_pays_the_feudal_price(self):
        self.assertTrue(self.market_trade_runs(FEUDAL_AGE_FOOD))
