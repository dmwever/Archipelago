from ..Options import ExistingTechs, IncludeUniqueUnits, ShuffleVillager, Techsanity, Unitsanity
from ..items.Items import Age2ItemData
from ..locations.Buildings import Age2BuildingData
from ..locations.EscortUnits import Age2EscortUnitData
from ..locations.Heroes import Age2HeroData
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
        reachable. Owning a Mangonel is a different question - a granted unit never climbs or
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
        world = self.build(unitsanity=Unitsanity.option_unit_line,
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


class TestTheBuilderBuilds(Age2RuleTestBase):
    """With professions shuffled a villager cannot swap into a Builder until the profession
    arrives, so nothing gets put up without it. Buildings that stand at the start need nobody."""

    BUILDER = Age2ItemData.PROFESSION_BUILDER.item_name

    def test_putting_a_building_up_needs_the_builder(self):
        self.build(shuffle_villager=ShuffleVillager.option_include_professions)
        location = Age2BuildingData.BARRACKS.location_name
        self.assertTrue(self.can_reach(location))
        self.assertFalse(self.can_reach(location, self.state_without(self.BUILDER)))

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

    def test_a_repairer_is_free(self):
        self.assertTrue(self.can_reach(Age2VillagerJobData.REPAIRER_FEMALE.location_name))

    def test_the_resource_jobs_are_free_unless_a_scenario_says_otherwise(self):
        """A gold miner needs gold on the map, not a building anyone can withhold."""
        for job in (Age2VillagerJobData.GOLD_MINER_MALE, Age2VillagerJobData.HUNTER_FEMALE,
                    Age2VillagerJobData.LUMBERJACK_MALE, Age2VillagerJobData.SHEPHERD_FEMALE,
                    Age2VillagerJobData.FISHERMAN_MALE):
            self.assertTrue(self.can_reach(job.location_name), job.name)

    def test_both_sexes_of_a_job_ask_the_same_thing(self):
        without = self.state_without(Age2BuildingData.FARM.item.item_name)
        for job in (Age2VillagerJobData.FARMER_MALE, Age2VillagerJobData.FARMER_FEMALE):
            self.assertFalse(self.can_reach(job.location_name, without), job.name)
