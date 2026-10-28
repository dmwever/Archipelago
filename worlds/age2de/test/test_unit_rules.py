from ..Options import ExistingTechs, IncludeUniqueUnits, ShuffleVillager, Techsanity, Unitsanity
from ..items.Items import Age2ItemData
from ..locations.Buildings import Age2BuildingData
from ..locations.EscortUnits import Age2EscortUnitData
from ..locations.Scenarios import Age2ScenarioData
from ..locations.UnitLines import Age2UnitLineData
from ..locations.Units import Age2UnitData
from ..locations.VillagerJobs import Age2VillagerJobData
from .bases import Age2RuleTestBase

EVERYTHING = dict(unitsanity=Unitsanity.option_all,
                  include_unique_units=IncludeUniqueUnits.option_both)


class TestUpgradedAway(Age2RuleTestBase):
    """A scenario auto-researches everything STRICTLY below the age it starts in, and an upgrade
    changes what the building turns out. So an Imperial scenario trains Crossbowmen and can never
    produce an Archer, while a Castle-Age one has not researched Crossbowman yet and still can."""

    def upgraded_away(self, world, unit: Age2UnitData) -> list[str]:
        return [scenario.scenario.name for scenario in world.rules.logic.scenarios
                if scenario.units.upgraded_away(unit)]

    def test_vanilla_technologies_upgrade_the_lower_tiers_away(self):
        world = self.build(existing_techs=ExistingTechs.option_vanilla, **EVERYTHING)
        # Man-at-Arms is Feudal, so it is researched only where the scenario opens above Feudal.
        # A Militia is still a Militia in the one Dark scenario and in both Feudal ones.
        gone = self.upgraded_away(world, Age2UnitData.MILITIA)
        self.assertEqual(len(gone), 9)
        for kept in ("AP_ATTILA_1", "AP_JOAN_2", "AP_JOAN_3"):
            self.assertNotIn(kept, gone)
        # Crossbowman is Castle, so only the two Imperial scenarios have upgraded the Archer away.
        self.assertEqual(len(self.upgraded_away(world, Age2UnitData.ARCHER)), 2)

    def test_withheld_upgrades_leave_every_tier_trainable(self):
        """Under find_items the upgrade is an item, so when it lands is your choice."""
        world = self.build(existing_techs=ExistingTechs.option_find_items,
                           techsanity=Techsanity.option_all, **EVERYTHING)
        for unit in (Age2UnitData.MILITIA, Age2UnitData.ARCHER, Age2UnitData.SPEARMAN):
            self.assertEqual(self.upgraded_away(world, unit), [], unit.name)

    def test_a_top_tier_is_never_upgraded_away(self):
        world = self.build(existing_techs=ExistingTechs.option_vanilla, **EVERYTHING)
        for unit in (Age2UnitData.PALADIN, Age2UnitData.CHAMPION, Age2UnitData.HALBERDIER):
            self.assertEqual(self.upgraded_away(world, unit), [], unit.name)


class TestOwningAUnit(Age2RuleTestBase):

    def test_everything_placed_is_reachable(self):
        world = self.build(shuffle_villager=ShuffleVillager.option_include_professions,
                           **EVERYTHING)
        unreachable = [location.name for location in self.multiworld.get_locations(world.player)
                       if location.name.startswith("Own ") and not self.can_reach(location.name)]
        self.assertEqual(unreachable, [])

    def test_a_tier_upgraded_away_everywhere_still_has_somewhere_to_be_owned(self):
        """Under Unitsanity All a location exists per tier, not per line, so a tier every scenario
        researches past is a location with no way to be reached. Vanilla is the mode that upgrades
        the most tiers away, so it is the one that would lose them."""
        world = self.build(existing_techs=ExistingTechs.option_vanilla, **EVERYTHING)
        unreachable = [location.name for location in self.multiworld.get_locations(world.player)
                       if location.name.startswith("Own ") and not self.can_reach(location.name)]
        self.assertEqual(unreachable, [])

    def test_a_handed_over_unit_needs_no_building(self):
        """No Hun trains a Mangudai; an Attila 1 mercenary muster spawns eighteen."""
        self.build(**EVERYTHING)
        self.assertTrue(self.can_reach(Age2UnitData.MANGUDAI.location_name))

    def test_being_given_a_higher_tier_does_not_hand_you_the_lower_one(self):
        """An Attila 2 mercenary muster spawns an Onager, which makes the Mangonel line's region
        reachable. Owning a Mangonel is a different question - a granted unit never advances or
        descends its line - and the location rule is what asks it."""
        self.build(**EVERYTHING)
        without = self.state_without(Age2UnitLineData.MANGONEL_LINE.item.item_name)
        self.assertTrue(self.can_reach(Age2UnitData.ONAGER.location_name, without))
        self.assertFalse(self.can_reach(Age2UnitData.MANGONEL.location_name, without))

    def test_a_hero_is_reachable_only_because_a_scenario_grants_one(self):
        world = self.build(**EVERYTHING)
        for hero in world.pool.units.heroes:
            self.assertTrue(self.can_reach(hero.location_name), hero.name)
        self.assertTrue(self.can_reach(Age2EscortUnitData.CART.location_name))

    def test_a_line_is_owned_when_any_of_its_tiers_is(self):
        self.build(unitsanity=Unitsanity.option_unit_line,
                   include_unique_units=IncludeUniqueUnits.option_both)
        self.assertTrue(self.can_reach(Age2UnitLineData.KNIGHT_LINE.location_name))


class TestUnitItems(Age2RuleTestBase):

    def test_a_line_item_is_required_to_train_its_units(self):
        """No scenario hands over a Skirmisher, so training is the only way to own one."""
        self.build(**EVERYTHING)
        without = self.state_without(Age2UnitLineData.SKIRMISHER_LINE.item.item_name)
        self.assertFalse(self.can_reach(Age2UnitData.SKIRMISHER.location_name, without))
        self.assertTrue(self.can_reach(Age2UnitData.SKIRMISHER.location_name))

    def test_a_granted_unit_needs_no_item(self):
        """Attila 2 opens with Tarkans, so the line item is not what makes one yours."""
        self.build(**EVERYTHING)
        without = self.state_without(Age2UnitLineData.TARKAN_LINE.item.item_name)
        self.assertTrue(self.can_reach(Age2UnitData.TARKAN.location_name, without))

    def test_a_trade_cart_wants_a_horse_where_there_are_horses(self):
        world = self.build(**EVERYTHING)
        units = world.rules.logic.units
        self.assertTrue(units.has_horses())
        self.assertTrue(units.token_applies(Age2UnitData.TRADE_CART,
                                            Age2ItemData.UPGRADE_HORSE))


class TestTrainingVillagers(Age2RuleTestBase):
    """With villagers shuffled the game trains none until the Villager item arrives, whatever
    unitsanity says. The villagers a scenario starts with need nothing."""

    VILLAGER = Age2ItemData.UNIT_LINE_VILLAGER.item_name

    def test_training_a_villager_needs_the_villager_item(self):
        for mode in (ShuffleVillager.option_yes, ShuffleVillager.option_include_professions):
            with self.subTest(shuffle_villager=mode):
                world = self.build(shuffle_villager=mode)
                rule = world.rules.logic.units.has_unit_items(Age2UnitData.VILLAGER_FEMALE)
                self.assertIn(self.VILLAGER, rule.resolve(world).item_dependencies())

    def test_unshuffled_villagers_need_nothing(self):
        world = self.build(shuffle_villager=ShuffleVillager.option_no)
        rule = world.rules.logic.units.has_unit_items(Age2UnitData.VILLAGER_MALE)
        self.assertTrue(rule.resolve(world).always_true)

    def test_a_villager_location_is_out_of_logic_without_it(self):
        self.build(shuffle_villager=ShuffleVillager.option_include_professions)
        location = Age2UnitData.VILLAGER_MALE.location_name
        self.assertTrue(self.can_reach(location))
        self.assertFalse(self.can_reach(location, self.state_without(self.VILLAGER)))


class TestTheBuilderBuilds(Age2RuleTestBase):
    """With professions shuffled a villager cannot swap into a Builder until the profession
    arrives, so nothing gets put up without it. Buildings that stand at the start need nobody."""

    BUILDER = Age2ItemData.PROFESSION_BUILDER.item_name

    def test_putting_a_building_up_needs_the_builder(self):
        self.build(shuffle_villager=ShuffleVillager.option_include_professions)
        location = Age2BuildingData.BARRACKS.location_name
        self.assertTrue(self.can_reach(location))
        self.assertFalse(self.can_reach(location, self.state_without(self.BUILDER)))

    def test_the_builder_comes_early(self):
        """Like the House: without it nothing gets built, so fill puts it in an early sphere."""
        world = self.build(shuffle_villager=ShuffleVillager.option_include_professions)
        self.assertEqual(1, world.multiworld.early_items[world.player].get(self.BUILDER))

    def test_without_professions_the_builder_is_no_requirement(self):
        self.build(shuffle_villager=ShuffleVillager.option_yes)
        location = Age2BuildingData.BARRACKS.location_name
        self.assertNotIn(self.BUILDER, self.item_requirements(location))


class TestVillagerJobs(Age2RuleTestBase):

    def setUp(self) -> None:
        super().setUp()
        self.build(shuffle_villager=ShuffleVillager.option_include_professions)

    def test_a_farmer_needs_a_farm(self):
        without = self.state_without(Age2BuildingData.FARM.item.item_name)
        self.assertFalse(self.can_reach(Age2VillagerJobData.FARMER_MALE.location_name, without))
        self.assertTrue(self.can_reach(Age2VillagerJobData.FARMER_MALE.location_name))

    def test_a_repairer_asks_for_no_item_of_its_own(self):
        """It needs a building to mend, and every scenario that opens with one supplies that
        itself - so with the pool collected there is nothing left to withhold."""
        self.assertTrue(self.can_reach(Age2VillagerJobData.REPAIRER_FEMALE.location_name))

    def test_the_resource_jobs_ask_the_map_and_not_an_item(self):
        """A gold miner needs gold where his villagers are, not a building anyone can withhold."""
        for job in (Age2VillagerJobData.GOLD_MINER_MALE, Age2VillagerJobData.HUNTER_FEMALE,
                    Age2VillagerJobData.LUMBERJACK_MALE, Age2VillagerJobData.SHEPHERD_FEMALE,
                    Age2VillagerJobData.FISHERMAN_MALE):
            self.assertTrue(self.can_reach(job.location_name), job.name)

    def test_both_sexes_of_a_job_ask_the_same_thing(self):
        without = self.state_without(Age2BuildingData.FARM.item.item_name)
        for job in (Age2VillagerJobData.FARMER_MALE, Age2VillagerJobData.FARMER_FEMALE):
            self.assertFalse(self.can_reach(job.location_name, without), job.name)


class TestAJobNeedsItsResourceWhereItsVillagersAre(Age2RuleTestBase):
    """Owning a job is a villager in some scenario taking that work up there, so the villagers
    and the thing worked have to belong to the same scenario. Bleda's Camp staffs Attila 1,
    which has no sheep in any tier; the Shepherd is somebody else's chapter."""

    JOB = Age2VillagerJobData.SHEPHERD_MALE
    CAMP = Age2ItemData.AP_ATTILA_1_BLEDAS_CAMP.item_name
    SHEPHERD = Age2ItemData.PROFESSION_SHEPHERD.item_name
    ATTILA_3 = ("The Great Ride: Unlock Next Scenario",
                "Progressive Attila Scenario", "Progressive Attila Scenario")

    def setUp(self) -> None:
        super().setUp()
        self.build(shuffle_villager=ShuffleVillager.option_include_professions)

    def test_villagers_where_no_sheep_graze_are_no_shepherd(self):
        state = self.state_with(self.CAMP, self.SHEPHERD)
        for job in (Age2VillagerJobData.SHEPHERD_MALE, Age2VillagerJobData.SHEPHERD_FEMALE):
            self.assertFalse(self.can_reach(job.location_name, state), job.name)

    def test_the_scenario_that_does_have_sheep_puts_it_back_in_logic(self):
        """Attila 3 opens with a flock in its own base and villagers of its own."""
        state = self.state_with(self.CAMP, self.SHEPHERD, *self.ATTILA_3)
        for job in (Age2VillagerJobData.SHEPHERD_MALE, Age2VillagerJobData.SHEPHERD_FEMALE):
            self.assertTrue(self.can_reach(job.location_name, state), job.name)


class TestARepairerNeedsSomethingToMend(Age2RuleTestBase):
    """Nothing the scan counts is what a Repairer works - a building is. Attila 1 opened with the
    Roman villagers alone has people and not one wall to patch."""

    VILLAGERS = Age2ItemData.AP_ATTILA_1_ROMAN_VILLAGERS.item_name
    REPAIRER = Age2ItemData.PROFESSION_REPAIRER.item_name
    BUILDER = Age2ItemData.PROFESSION_BUILDER.item_name
    LUMBERJACK = Age2ItemData.PROFESSION_LUMBERJACK.item_name
    TOWN_CENTER_ITEMS = (
        Age2ItemData.TOWN_CENTER_WOOD.item_name,
        Age2ItemData.TOWN_CENTER_STONE.item_name,
    )
    JOB = Age2VillagerJobData.REPAIRER_MALE

    def setUp(self) -> None:
        super().setUp()
        self.build(shuffle_villager=ShuffleVillager.option_include_professions)

    def test_villagers_with_nothing_standing_and_nothing_buildable_mend_nothing(self):
        state = self.state_with(self.VILLAGERS, self.REPAIRER)
        self.assertFalse(self.can_reach(self.JOB.location_name, state))

    def test_the_builder_gives_them_something_to_mend(self):
        state = self.state_with(
            self.VILLAGERS,
            self.REPAIRER,
            self.BUILDER,
            self.LUMBERJACK,
            *self.TOWN_CENTER_ITEMS,
        )
        self.assertTrue(self.can_reach(self.JOB.location_name, state))

    def test_the_builder_mends_nothing_with_nothing_to_build_it_from(self):
        state = self.state_with(self.VILLAGERS, self.REPAIRER, self.BUILDER)
        self.assertFalse(self.can_reach(self.JOB.location_name, state))

    def test_a_building_standing_at_the_start_is_enough_on_its_own(self):
        """Bleda's Camp opens with a Town Center and six more buildings, no Builder needed."""
        state = self.state_with(Age2ItemData.AP_ATTILA_1_BLEDAS_CAMP.item_name, self.REPAIRER)
        self.assertTrue(self.can_reach(self.JOB.location_name, state))


class TestWhichTiersCountForAJob(Age2RuleTestBase):
    """Sheep are the one resource a tier puts out of reach: an ally's cannot be taken and an
    enemy's cannot be targeted. Everything else is worked wherever it lies, because owning a job
    is a villager starting the work, not holding the ground long enough to finish it."""

    campaigns = ["Attila the Hun", "Joan of Arc", "Genghis Khan"]

    def setUp(self) -> None:
        super().setUp()
        self.world = self.build(shuffle_villager=ShuffleVillager.option_include_professions)

    def offers(self, scenario: Age2ScenarioData, job: Age2VillagerJobData) -> bool:
        rule = self.world.rules.logic.for_scenario(scenario).units.can_do_job(job)
        return not rule.resolve(self.world).always_false

    def test_a_flock_inside_an_enemy_base_is_no_flock(self):
        """Joan 2 has villagers and 1500 food of sheep, all of it English."""
        self.assertFalse(self.offers(Age2ScenarioData.AP_JOAN_2,
                                     Age2VillagerJobData.SHEPHERD_MALE))

    def test_a_flock_in_the_open_counts(self):
        self.assertTrue(self.offers(Age2ScenarioData.AP_GENGHIS_2,
                                    Age2VillagerJobData.SHEPHERD_MALE))

    def test_hunt_inside_an_enemy_base_still_counts(self):
        """Joan 3's only game is in a hostile camp, and a hunter who walks in is a hunter."""
        self.assertTrue(self.offers(Age2ScenarioData.AP_JOAN_3,
                                    Age2VillagerJobData.HUNTER_MALE))

    def test_a_scenario_with_none_of_the_resource_offers_nothing(self):
        self.assertFalse(self.offers(Age2ScenarioData.AP_ATTILA_1,
                                     Age2VillagerJobData.SHEPHERD_MALE))
        self.assertFalse(self.offers(Age2ScenarioData.AP_JOAN_4,
                                     Age2VillagerJobData.HUNTER_MALE))

    def test_a_fixed_force_takes_no_job_at_all(self):
        for scenario in (Age2ScenarioData.AP_JOAN_1, Age2ScenarioData.AP_JOAN_5,
                         Age2ScenarioData.AP_GENGHIS_1):
            for job in Age2VillagerJobData:
                with self.subTest(f"{scenario.name}.{job.name}"):
                    self.assertFalse(self.offers(scenario, job))
