from BaseClasses import CollectionState

from ..Options import ExistingTechs, LockTechs, Techsanity
from ..items.Items import Age2ItemData
from ..locations.Buildings import Age2BuildingData
from ..locations.Civilizations import Age2CivData
from ..locations.Scenarios import CAMPAIGN_TO_SCENARIOS
from ..locations.Techs import Age2TechData
from ..locations.connections.CivilizationTechs import CIV_TO_TECHS
from .bases import Age2RuleTestBase


MILL_CHAIN = (Age2TechData.CROP_ROTATION, Age2TechData.HEAVY_PLOW, Age2TechData.HORSE_COLLAR)


class TestPrerequisites(Age2RuleTestBase):
    def test_a_technology_wants_every_item_below_it_in_the_chain(self):
        self.build(techsanity=Techsanity.option_generic)
        wanted = self.item_requirements(Age2TechData.CROP_ROTATION.location_name)
        for tech in MILL_CHAIN:
            self.assertIn(tech.item.item_name, wanted, tech.name)
        # and only downwards: the bottom of the chain wants nothing above it
        self.assertNotIn(Age2TechData.HEAVY_PLOW.item.item_name,
                         self.item_requirements(Age2TechData.HORSE_COLLAR.location_name))

    def test_withholding_any_link_blocks_everything_above_it(self):
        self.build(techsanity=Techsanity.option_generic)
        self.assertTrue(self.can_reach(Age2TechData.CROP_ROTATION.location_name))
        for tech in MILL_CHAIN:
            with self.subTest(withheld=tech.name):
                state = self.state_without(tech.item.item_name)
                self.assertFalse(state.can_reach_location(
                    Age2TechData.CROP_ROTATION.location_name, self.world.player))
        # the reverse does not hold -- the bottom does not need the top
        self.assertTrue(self.can_reach(
            Age2TechData.HORSE_COLLAR.location_name,
            self.state_without(Age2TechData.CROP_ROTATION.item.item_name)))

    def test_the_deepest_chain_is_carried_the_whole_way(self):
        # Champion is four deep, and is the case that catches a walk that stops
        # after the first prerequisite.
        self.build(techsanity=Techsanity.option_units)
        chain = (Age2TechData.CHAMPION, Age2TechData.TWO_HANDED_SWORDSMAN,
                 Age2TechData.LONG_SWORDSMAN, Age2TechData.MAN_AT_ARMS)
        wanted = self.item_requirements(Age2TechData.CHAMPION.location_name)
        for tech in chain:
            self.assertIn(tech.item.item_name, wanted, tech.name)


class TestPrerequisiteOutsideThePool(Age2RuleTestBase):
    """A prerequisite the seed does not hand out is one the game already
    researched, so it asks for nothing. Shipped data never produces this --
    every chain survives every civilization and mode filter -- so the gap has
    to be made rather than found."""

    def setUp(self):
        for civ in Age2CivData:
            original = CIV_TO_TECHS[civ]
            self.addCleanup(CIV_TO_TECHS.__setitem__, civ, original)
            CIV_TO_TECHS[civ] = [tech for tech in original if tech is not Age2TechData.HEAVY_PLOW]

    def test_a_prerequisite_outside_the_pool_imposes_nothing(self):
        self.build(techsanity=Techsanity.option_generic)
        self.assertNotIn(Age2TechData.HEAVY_PLOW, self.world.shuffled_techs)
        wanted = self.item_requirements(Age2TechData.CROP_ROTATION.location_name)
        self.assertNotIn(Age2TechData.HEAVY_PLOW.item.item_name, wanted)
        self.assertIn(Age2TechData.CROP_ROTATION.item.item_name, wanted)

    def test_the_chain_stops_at_the_gap_rather_than_stepping_over_it(self):
        # Horse Collar sits below the gap. Heavy Plow being granted means it was
        # granted too, so asking for it would be asking for something the player
        # was never given a way to earn.
        self.build(techsanity=Techsanity.option_generic)
        self.assertNotIn(Age2TechData.HORSE_COLLAR.item.item_name,
                         self.item_requirements(Age2TechData.CROP_ROTATION.location_name))


class TestLockTechs(Age2RuleTestBase):
    def test_effects_asks_for_no_tech_item(self):
        self.build(techsanity=Techsanity.option_generic, lock_techs=LockTechs.option_effects)
        wanted = self.item_requirements(Age2TechData.CROP_ROTATION.location_name)
        for tech in MILL_CHAIN:
            self.assertNotIn(tech.item.item_name, wanted, tech.name)

    def test_effects_still_asks_for_the_age(self):
        # Effects unlocks the effect, not the age. Crop Rotation is an Imperial
        # technology whichever way the option is set.
        self.build(techsanity=Techsanity.option_generic, lock_techs=LockTechs.option_effects)
        starved = self.state_without(*self.imperial_blockers())
        self.assertFalse(starved.can_reach_location(
            Age2TechData.CROP_ROTATION.location_name, self.world.player))

    def imperial_blockers(self) -> list[str]:
        return [building.item.item_name for building in
                (Age2BuildingData.MONASTERY, Age2BuildingData.UNIVERSITY,
                 Age2BuildingData.SIEGE_WORKSHOP, Age2BuildingData.CASTLE)]


class TestAgeGate(Age2RuleTestBase):
    def test_two_technologies_in_one_region_can_disagree(self):
        # Both live in the Mill. If the age ever migrates from the location to
        # the region entrance, these two stop being separable and this fails.
        self.build(techsanity=Techsanity.option_generic)
        starved = self.state_without(
            *[building.item.item_name for building in
              (Age2BuildingData.MONASTERY, Age2BuildingData.UNIVERSITY,
               Age2BuildingData.SIEGE_WORKSHOP, Age2BuildingData.CASTLE)])
        self.assertTrue(starved.can_reach_location(
            Age2TechData.HORSE_COLLAR.location_name, self.world.player))
        self.assertFalse(starved.can_reach_location(
            Age2TechData.CROP_ROTATION.location_name, self.world.player))


class TestExistingTechs(Age2RuleTestBase):
    def test_a_scenario_that_was_handed_a_technology_cannot_check_it(self):
        # Under Vanilla a scenario auto-researches everything below the age it
        # opens in, and those locations never send a check. Only the scenarios
        # standing in the age itself count.
        world = self.build(techsanity=Techsanity.option_all,
                           existing_techs=ExistingTechs.option_vanilla)
        scenarios = [scenario for campaign in world.included_campaigns
                     for scenario in CAMPAIGN_TO_SCENARIOS[campaign]]
        for tech in world.shuffled_techs:
            with self.subTest(tech=tech.name):
                rule = world.rules.logic.can_research_anywhere(tech).resolve(world)
                self.assertFalse(rule.always_false)
        # every technology has at least one scenario that opens at or below it
        for tech in world.shuffled_techs:
            self.assertTrue([s for s in scenarios if s.vanilla_age <= tech.age], tech.name)

    def test_find_items_hands_every_technology_back(self):
        # Withheld everywhere, so a scenario that opens above the age can still
        # research it -- for free, but it still sends the check.
        world = self.build(techsanity=Techsanity.option_all,
                           existing_techs=ExistingTechs.option_find_items)
        for tech in world.shuffled_techs:
            self.assertTrue(world.tech_pool.locked_at_start(tech), tech.name)


class TestReplacementBuildingReachesSharedTechs(Age2RuleTestBase):
    """A civilization that puts up a Settlement instead of a Mill still
    researches the Mill technologies. The location cannot move or be duplicated,
    so the Mill region earns a second, free entrance instead."""

    def setUp(self):
        was = Age2CivData.FRANKS.included_buildings
        Age2CivData.FRANKS.included_buildings = was + [Age2BuildingData.SETTLEMENT]
        self.addCleanup(setattr, Age2CivData.FRANKS, "included_buildings", was)

    def build_with_uniques(self):
        return self.build(techsanity=Techsanity.option_generic,
                          shuffle_buildings={"Economy", "Tech", "Military", "Unique"})

    def test_either_building_reaches_the_shared_technology(self):
        self.build_with_uniques()
        mill = Age2ItemData.MILL.item_name
        settlement = Age2ItemData.SETTLEMENT.item_name
        location = Age2TechData.HORSE_COLLAR.location_name
        self.assertTrue(self.can_reach(location, self.state_without(settlement)))
        self.assertTrue(self.can_reach(location, self.state_without(mill)))
        self.assertFalse(self.can_reach(location, self.state_without(mill, settlement)))

    def test_the_cross_entrance_carries_no_rule_of_its_own(self):
        # A rule here would double gate: the replacement's own door already
        # asked whether the player can build it.
        self.build_with_uniques()
        cross = self.multiworld.get_entrance("Settlement to Mill Techs", self.world.player)
        self.assertTrue(cross.access_rule(CollectionState(self.multiworld)))
