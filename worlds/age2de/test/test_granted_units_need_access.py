from ..Options import Caveman, Unitsanity
from ..items.Items import Age2ItemData as I
from ..items.Items import CATEGORY_TO_ITEMS, Mercenary
from ..locations.Buildings import Age2BuildingData as B
from ..locations.Campaigns import Age2CampaignData
from ..locations.Heroes import Age2HeroData as H
from ..locations.Scenarios import Age2ScenarioData as S
from ..locations.Units import Age2UnitData as U
from ..logic.ScenarioLogic import ScenarioStartingState
from .bases import Age2RuleTestBase

EVERY_CAMPAIGN = [campaign.campaign_name for campaign in Age2CampaignData]

GATED = (I.AP_JOAN_1_RECRUITS, I.AP_GENGHIS_1_UNGIRRAD_TRIBE, I.AP_GENGHIS_1_UIGHUR_TRIBE,
         I.AP_GENGHIS_3_ENGINEERS, I.AP_GENGHIS_3_BOMBARDS, I.AP_ATTILA_2_SCYTHIAN_TROOP)


class GrantTestBase(Age2RuleTestBase):
    campaigns = EVERY_CAMPAIGN
    starting_campaigns = EVERY_CAMPAIGN
    caveman = Caveman.option_false
    unitsanity = Unitsanity.option_all

    def build(self, **options):
        options.setdefault("caveman", self.caveman)
        options.setdefault("unitsanity", self.unitsanity)
        return super().build(**options)

    def hand_over(self, scenario, unit):
        logic = self.world.rules.logic.for_scenario(scenario)
        return logic.obtains_unit(unit).resolve(self.world)

    def standing(self, scenario, building):
        logic = self.world.rules.logic.for_scenario(scenario)
        return logic.starting_state.starts_with_building[building].resolve(self.world)

    def assert_needs(self, scenario, unit, *item_names: str):
        obtained = self.hand_over(scenario, unit)
        self.assertTrue(obtained(self.state_without()),
                        f"{unit.name} is never handed over in {scenario.scenario_name}")
        for name in item_names:
            self.assertFalse(obtained(self.state_without(name)),
                             f"{unit.name} reaches logic in {scenario.scenario_name} without "
                             f"{name}, which the hand-over needs")

    def assert_bare(self, scenario, unit, item_name: str):
        obtained = self.hand_over(scenario, unit)
        self.assertTrue(obtained(self.state_with(item_name)),
                        f"{item_name} alone does not hand {unit.name} over")
        self.assertFalse(obtained(self.state_without(item_name)),
                         f"{unit.name} is handed over in {scenario.scenario_name} without "
                         f"{item_name}")

    def assert_standing_with(self, scenario, building, item_name: str):
        stands = self.standing(scenario, building)
        self.assertTrue(stands(self.state_with(item_name)),
                        f"{item_name} does not leave a {building.building_name} standing")
        self.assertFalse(stands(self.state_without(item_name)),
                         f"a {building.building_name} stands in {scenario.scenario_name} "
                         f"without {item_name}")


class TestJoan1Recruits(GrantTestBase):

    def test_the_scorpions_wait_for_the_crossing(self):
        self.build()
        self.assert_needs(S.AP_JOAN_1, U.SCORPION,
                          I.AP_JOAN_1_RECRUITS.item_name, I.AP_JOAN_1_TRANSPORT.item_name)

    def test_the_crossbowmen_come_from_either_item(self):
        self.build()
        obtained = self.hand_over(S.AP_JOAN_1, U.CROSSBOWMAN)
        self.assertTrue(obtained(self.state_without(I.AP_JOAN_1_RECRUITS.item_name)))
        self.assertTrue(obtained(self.state_without(I.AP_JOAN_1_CROSSBOWMEN.item_name)))
        self.assertFalse(obtained(self.state_without(I.AP_JOAN_1_RECRUITS.item_name,
                                                     I.AP_JOAN_1_CROSSBOWMEN.item_name)))

    def test_the_ram_army_asks_only_for_itself(self):
        self.build()
        for unit in (U.PIKEMAN, U.CAPPED_RAM):
            with self.subTest(unit.name):
                self.assert_bare(S.AP_JOAN_1, unit, I.AP_JOAN_1_RAM.item_name)

    def test_the_men_at_arms_come_from_either_land_item(self):
        self.build()
        obtained = self.hand_over(S.AP_JOAN_1, U.MAN_AT_ARMS)
        self.assertTrue(obtained(self.state_with(I.AP_JOAN_1_RAM.item_name)))
        self.assertTrue(obtained(self.state_with(I.AP_JOAN_1_SWORDSMEN.item_name)))
        self.assertFalse(obtained(self.state_without(I.AP_JOAN_1_RAM.item_name,
                                                     I.AP_JOAN_1_SWORDSMEN.item_name)))


class TestGenghis1Tribes(GrantTestBase):
    caveman = Caveman.option_true

    def test_the_monks_come_from_the_kereyids(self):
        self.build()
        self.assert_bare(S.AP_GENGHIS_1, U.MONK, I.AP_GENGHIS_1_KEREYID_TRIBE.item_name)

    def test_the_ungirrad_mangudai_wait_for_a_monk(self):
        self.build()
        self.assert_needs(S.AP_GENGHIS_1, U.MANGUDAI,
                          I.AP_GENGHIS_1_UNGIRRAD_TRIBE.item_name,
                          I.AP_GENGHIS_1_KEREYID_TRIBE.item_name)

    def test_the_uighur_camels_wait_for_ornlu(self):
        self.build()
        self.assert_needs(S.AP_GENGHIS_1, U.CAMEL_RIDER,
                          I.AP_GENGHIS_1_UIGHUR_TRIBE.item_name,
                          I.AP_GENGHIS_1_KEREYID_TRIBE.item_name)

    def test_the_riders_the_scenario_opens_with_need_no_tribe(self):
        self.build()
        for unit in (U.CAVALRY_ARCHER, U.LIGHT_CAVALRY):
            with self.subTest(unit.name):
                self.assertTrue(self.hand_over(S.AP_GENGHIS_1, unit)(self.state_with()))


class TestGenghis3Siege(GrantTestBase):

    def test_the_engineers_and_what_they_bring_wait_for_the_transport(self):
        self.build()
        for unit in (U.VILLAGER_MALE, U.VILLAGER_FEMALE, U.BATTERING_RAM, U.ROCKET_CART):
            with self.subTest(unit.name):
                self.assert_needs(S.AP_GENGHIS_3, unit,
                                  I.AP_GENGHIS_3_ENGINEERS.item_name,
                                  I.AP_GENGHIS_3_TRANSPORT.item_name)

    def test_the_bombards_wait_for_the_transport(self):
        self.build()
        self.assert_needs(S.AP_GENGHIS_3, U.BOMBARD_CANNON,
                          I.AP_GENGHIS_3_BOMBARDS.item_name,
                          I.AP_GENGHIS_3_TRANSPORT.item_name)

    def test_the_siege_workshop_comes_with_either_and_waits_for_the_transport(self):
        self.build()
        stands = self.standing(S.AP_GENGHIS_3, B.SIEGE_WORKSHOP)
        self.assertTrue(stands(self.state_without(I.AP_GENGHIS_3_ENGINEERS.item_name)))
        self.assertTrue(stands(self.state_without(I.AP_GENGHIS_3_BOMBARDS.item_name)))
        self.assertFalse(stands(self.state_without(I.AP_GENGHIS_3_TRANSPORT.item_name)))


class TestAttila2Scythians(GrantTestBase):

    def test_the_troop_waits_for_the_villagers_it_is_traded_for(self):
        self.build()
        for unit in (U.MANGUDAI, U.CAPPED_RAM, U.ONAGER):
            with self.subTest(unit.name):
                self.assert_needs(S.AP_ATTILA_2, unit,
                                  I.AP_ATTILA_2_SCYTHIAN_TROOP.item_name,
                                  I.AP_ATTILA_2_VILLAGERS.item_name)

    def test_the_prisoners_are_freed_by_the_force_the_scenario_already_hands_over(self):
        self.build()
        for unit in (U.TARKAN, U.HUSSAR):
            with self.subTest(unit.name):
                self.assert_bare(S.AP_ATTILA_2, unit,
                                 I.AP_ATTILA_2_DYRRHACHIUMS_PRISONERS.item_name)


class TestCampsAndArmiesAreBare(GrantTestBase):

    def test_attila_1_mangudai(self):
        self.build()
        self.assert_bare(S.AP_ATTILA_1, U.MANGUDAI, I.AP_ATTILA_1_MANGUDAI.item_name)

    def test_joan_5_loyalists(self):
        self.build()
        for unit in (U.KNIGHT, U.MAN_AT_ARMS, U.HEAVY_SCORPION, U.THROWING_AXEMAN):
            with self.subTest(unit.name):
                self.assert_bare(S.AP_JOAN_5, unit, I.AP_JOAN_5_LOYALISTS.item_name)

    def test_joan_5_kings_troop(self):
        self.build()
        for unit in (U.SCOUT_CAVALRY, U.MILITIA):
            with self.subTest(unit.name):
                self.assert_bare(S.AP_JOAN_5, unit, I.AP_JOAN_5_KINGS_REINFORCEMENTS.item_name)

    def test_joan_6_artillery(self):
        self.build()
        for unit in (U.HAND_CANNONEER, U.BOMBARD_CANNON, H.JEAN_BUREAU):
            with self.subTest(unit.name):
                self.assert_bare(S.AP_JOAN_6, unit, I.AP_JOAN_6_ARTILLERY.item_name)

    def test_joan_6_champions_come_from_the_army_or_the_lone_swordsman(self):
        self.build()
        obtained = self.hand_over(S.AP_JOAN_6, U.CHAMPION)
        self.assertTrue(obtained(self.state_with(I.AP_JOAN_6_ARMY.item_name)))
        self.assertTrue(obtained(self.state_with(I.AP_JOAN_6_LONE_SWORDSMAN.item_name)))
        self.assertFalse(obtained(self.state_without(I.AP_JOAN_6_ARMY.item_name,
                                                     I.AP_JOAN_6_LONE_SWORDSMAN.item_name)))

    def test_genghis_5_hermits(self):
        self.build()
        for unit in (U.MONK, U.ELITE_LEITIS):
            with self.subTest(unit.name):
                self.assert_bare(S.AP_GENGHIS_5, unit, I.AP_GENGHIS_5_HERMITS.item_name)

    def test_genghis_6_subotais_army(self):
        self.build()
        for unit in (H.SUBOTAI, H.KHAN, H.SABOTEUR):
            with self.subTest(unit.name):
                self.assert_bare(S.AP_GENGHIS_6, unit, I.AP_GENGHIS_6_SUBOTAIS_ARMY.item_name)


class TestBuildingsComeWithTheHandOver(GrantTestBase):

    def test_the_tayichiud_base_hands_over_its_mills(self):
        self.build()
        self.assert_standing_with(S.AP_GENGHIS_2, B.MILL,
                                  I.AP_GENGHIS_2_TAYICHIUD_BASE.item_name)

    def test_the_hermits_hand_over_their_monastery(self):
        self.build()
        self.assert_standing_with(S.AP_GENGHIS_5, B.MONASTERY,
                                  I.AP_GENGHIS_5_HERMITS.item_name)


class TestEveryHandOverIsAuthored(GrantTestBase):

    def test_each_scenario_authors_exactly_the_units_its_triggers_hand_over(self):
        self.build()
        for scenario_logic in self.world.rules.logic.scenarios:
            scenario = scenario_logic.scenario
            with self.subTest(scenario.scenario_name):
                self.assertEqual(set(scenario.trigger_units),
                                 set(scenario_logic.starting_state.obtains_unit))

    def test_nothing_derives_a_grant_from_a_roster(self):
        self.assertFalse(hasattr(ScenarioStartingState, "default_mercenary_grants"))


class TestOnlyTheGatedMercenariesCostMoreThanTheirItem(GrantTestBase):
    caveman = Caveman.option_true

    def test_a_bare_mercenary_hands_its_whole_roster_over_on_its_own_item(self):
        self.build()
        for item in CATEGORY_TO_ITEMS[Mercenary]:
            if item in GATED:
                continue
            for soldier in item.type.units:
                with self.subTest(item=item.name, unit=soldier.unit.name):
                    obtained = self.hand_over(item.type.vanilla_scenario, soldier.unit)
                    self.assertTrue(obtained(self.state_with(item.item_name)),
                                    f"{item.item_name} is ruled bare, so it hands over "
                                    f"{soldier.unit.name} on its own")

    def test_a_gated_mercenary_hands_nothing_over_on_its_item_alone(self):
        self.build()
        for item in GATED:
            for soldier in item.type.units:
                with self.subTest(item=item.name, unit=soldier.unit.name):
                    obtained = self.hand_over(item.type.vanilla_scenario, soldier.unit)
                    self.assertFalse(obtained(self.state_with(item.item_name)),
                                     f"{soldier.unit.name} reaches logic on "
                                     f"{item.item_name} alone, without the access the "
                                     "hand-over needs")


class TestCavemanHandsOutMilitia(GrantTestBase):
    caveman = Caveman.option_true

    def test_own_militia_asks_for_nothing_under_caveman(self):
        self.build()
        owned = self.world.rules.logic.units.can_own_anywhere(U.MILITIA).resolve(self.world)
        self.assertTrue(owned(self.state_with()))
