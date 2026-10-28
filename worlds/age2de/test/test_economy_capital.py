from rule_builder.rules import Has, Rule

from . import bases
from ..Options import ExistingTechs, PartnerTrade
from ..items.Items import Age2ItemData, Resource
from ..locations.Scenarios import Age2ScenarioData
from ..logic.custom_logic.EconomyRoutes import Strength

TRADE_AND_RELICS = ("Trade Cogs", "Trade Carts", "Relics", "Fish Traps")
STARTED_IN = (", started in Feudal", ", started in Castle")


class EconomyCapitalBase(bases.Age2RuleTestBase):
    campaigns = ["Attila the Hun"]
    starting_campaigns = ["Attila the Hun"]

    def needs(self, scenario: Age2ScenarioData) -> dict[str, dict[Resource, Strength]]:
        routes = self.world.rules.logic.for_scenario(scenario).routes
        return {route.name: dict(route.needs) for route in routes.economy_routes().routes}

    def possible(self, scenario: Age2ScenarioData) -> set[str]:
        economy = self.world.rules.logic.for_scenario(scenario).economy
        resolved = economy.has_economy_routes().resolve(self.world)
        return {resolved.routes[index].name for index in resolved.possible}

    def started_in(self, scenario: Age2ScenarioData) -> dict[str, dict[Resource, Strength]]:
        return {name: needs for name, needs in self.needs(scenario).items()
                if name.startswith(TRADE_AND_RELICS) and name.endswith(STARTED_IN)}


class TestACastleStartPaysNoAgeInsideTheEconomy(EconomyCapitalBase):

    def test_trade_and_relics_started_in_the_age_need_no_food(self):
        self.build(partner_trade=PartnerTrade.option_allies_and_enemies)
        routes = self.started_in(Age2ScenarioData.AP_ATTILA_3)
        self.assertIn("Trade Cogs, started in Feudal", routes)
        self.assertIn("Relics at a built Monastery, started in Castle", routes)
        self.assertEqual({}, {name: needs for name, needs in routes.items()
                              if Resource.FOOD in needs})

    def test_a_castle_start_can_run_them(self):
        self.build(partner_trade=PartnerTrade.option_allies_and_enemies)
        possible = self.possible(Age2ScenarioData.AP_ATTILA_3)
        self.assertIn("Trade Cogs, started in Feudal", possible)
        self.assertIn("Relics at a built Monastery, started in Castle", possible)


class TestUnderStartInDarkAgeRelicsPayTheCastlePrice(EconomyCapitalBase):

    def test_the_advanced_relic_routes_need_food_at_scale_and_some_gold(self):
        self.build(existing_techs=ExistingTechs.option_start_in_dark_age)
        relics = {name: needs for name, needs in self.needs(Age2ScenarioData.AP_ATTILA_3).items()
                  if name.startswith("Relics") and name.endswith(", advanced to Castle")}
        self.assertEqual(
            {
                "Relics at a standing Monastery, advanced to Castle": {
                    Resource.WOOD: Strength.SOME,
                    Resource.FOOD: Strength.AT_SCALE,
                    Resource.GOLD: Strength.SOME,
                },
                "Relics at a built Monastery, advanced to Castle": {
                    Resource.WOOD: Strength.SOME,
                    Resource.FOOD: Strength.AT_SCALE,
                    Resource.GOLD: Strength.SOME,
                },
            },
            relics,
        )

    def test_nothing_started_in_the_age_can_run(self):
        self.build(existing_techs=ExistingTechs.option_start_in_dark_age)
        possible = self.possible(Age2ScenarioData.AP_ATTILA_3)
        self.assertEqual([], sorted(name for name in possible if name.endswith(STARTED_IN)))


class TestAtScaleVillagersPayForTheirCamp(EconomyCapitalBase):

    VILLAGERS = {Resource.FOOD: Strength.SOME}
    VILLAGERS_AND_A_CAMP = {Resource.FOOD: Strength.SOME, Resource.WOOD: Strength.SOME}

    def test_a_built_mining_camp_needs_some_wood_and_a_standing_one_nothing(self):
        self.build()
        needs = self.needs(Age2ScenarioData.AP_ATTILA_1)
        for route in ("Villagers gathering gold with a Base", "Villagers gathering stone with a Base"):
            with self.subTest(route=route):
                self.assertEqual(self.VILLAGERS_AND_A_CAMP, needs[f"{route} at a built Mining Camp"])
                self.assertEqual(self.VILLAGERS, needs[f"{route} at a standing Mining Camp"])

    def test_a_built_mill_needs_some_wood_and_a_standing_one_nothing(self):
        self.build()
        needs = self.needs(Age2ScenarioData.AP_ATTILA_1)
        route = "Villagers gathering food with a Base"
        self.assertEqual(self.VILLAGERS_AND_A_CAMP, needs[f"{route} at a built Mill"])
        self.assertEqual(self.VILLAGERS, needs[f"{route} at a standing Mill"])

    def test_a_seeded_mule_cart_needs_nothing_for_the_camp(self):
        self.build()
        needs = self.needs(Age2ScenarioData.AP_ATTILA_1)
        self.assertEqual(self.VILLAGERS, needs["Villagers gathering gold with a Base at a Mule Cart"])


class TestEveryRouteOnABaseTrainsVillagers(EconomyCapitalBase):

    ON_A_BASE = ("with a Base", "Farmers", "Villagers and Fishing Ships")

    def test_every_route_asking_for_a_base_needs_some_food(self):
        self.build()
        for scenario in (Age2ScenarioData.AP_ATTILA_1, Age2ScenarioData.AP_ATTILA_4):
            on_a_base = {name: needs for name, needs in self.needs(scenario).items()
                         if any(marker in name for marker in self.ON_A_BASE)}
            with self.subTest(scenario=scenario.name):
                self.assertGreater(len(on_a_base), 6)
                self.assertEqual([], [name for name, needs in on_a_base.items()
                                      if needs.get(Resource.FOOD, 0) < Strength.SOME])


class TestASecondTownCenterAsACampPaysThroughItsNeeds(EconomyCapitalBase):
    """#32 item 4: a second Town Center as a camp is its own route per at-scale route, paying
    *some* wood and stone for itself and, below Castle, the Castle price, all through its needs."""

    AT_SCALE = (
        "Lumberjacks with a Base",
        "Villagers gathering food with a Base",
        "Villagers gathering gold with a Base",
        "Villagers gathering stone with a Base",
        "Villagers and Fishing Ships gathering food",
        "Villagers and Fishing Ships gathering gold",
    )
    TOWN_CENTER = {Resource.WOOD: Strength.SOME, Resource.STONE: Strength.SOME}
    TOWN_CENTER_ITEMS = {
        Age2ItemData.TOWN_CENTER_WOOD.item_name,
        Age2ItemData.TOWN_CENTER_STONE.item_name,
    }
    EXISTING_TECHS = (ExistingTechs.option_vanilla, ExistingTechs.option_start_in_dark_age)

    @staticmethod
    def boats(route: str) -> dict[Resource, Strength]:
        if route.startswith("Villagers and Fishing Ships"):
            return {Resource.WOOD: Strength.AT_SCALE}
        return {}

    def camp_routes(self, ending: str) -> dict[str, dict[Resource, Strength]]:
        return {
            name: needs for name, needs in self.needs(Age2ScenarioData.AP_ATTILA_1).items()
                if "second Town Center" in name and name.endswith(ending)
        }

    def test_advanced_to_castle_it_needs_the_castle_price_and_some_wood_and_stone(self):
        self.build(existing_techs=ExistingTechs.option_start_in_dark_age)
        expected = {
            f"{route} at a second Town Center, advanced to Castle": {
                **self.TOWN_CENTER,
                **self.boats(route),
                Resource.FOOD: Strength.AT_SCALE,
                Resource.GOLD: Strength.SOME,
            }
            for route in self.AT_SCALE
        }
        self.assertEqual(expected, self.camp_routes(", advanced to Castle"))

    def test_started_in_castle_it_needs_some_wood_and_stone_and_the_villagers_food(self):
        self.build(existing_techs=ExistingTechs.option_start_in_dark_age)
        expected = {
            f"{route} at a second Town Center, started in Castle": {
                **self.TOWN_CENTER,
                **self.boats(route),
                Resource.FOOD: Strength.SOME,
            }
            for route in self.AT_SCALE
        }
        self.assertEqual(expected, self.camp_routes(", started in Castle"))

    def test_the_camp_never_asks_the_town_center_items(self):
        for existing_techs in self.EXISTING_TECHS:
            with self.subTest(existing_techs=existing_techs):
                self.build(existing_techs=existing_techs)
                for scenario in self.world.rules.logic.scenarios:
                    camp = scenario.buildings.can_build_tc_as_camp().resolve(self.world)
                    self.assertEqual(set(), self.TOWN_CENTER_ITEMS & self.items_asked(camp))

    def test_the_defence_never_asks_the_town_center_items(self):
        for existing_techs in self.EXISTING_TECHS:
            with self.subTest(existing_techs=existing_techs):
                self.build(existing_techs=existing_techs)
                for scenario in self.world.rules.logic.scenarios:
                    defence = scenario.buildings.can_build_tc_as_defence().resolve(self.world)
                    self.assertEqual(set(), self.TOWN_CENTER_ITEMS & self.items_asked(defence))

    def items_asked(self, rule: Rule.Resolved) -> set[str]:
        if isinstance(rule, Has.Resolved):
            return {rule.item_name}
        below = [
            getattr(rule, name) for name in ("child", "answer")
                if hasattr(rule, name)
        ]
        if hasattr(rule, "children"):
            below += list(rule.children)
        return set().union(*[self.items_asked(child) for child in below])
