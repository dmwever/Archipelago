"""The pools: what this seed contains, decided once in generate_early and read everywhere."""

import unittest

from . import bases
from ..locations.Buildings import Age2BuildingData, BuildingOption
from ..locations.Campaigns import Age2CampaignData
from ..locations.Techs import Age2TechData
from ..locations.Units import Age2UnitData
from ..locations.connections.CivilizationTechs import CIV_TO_TECHS
from ..locations.connections.CivilizationUnits import CIV_TO_UNITS


class TestCivilizationPool(bases.Age2RuleTestBase):
    """Nobody picks the civs - they arrive with the scenarios, so the pool is derived twice over."""

    campaigns = ["Attila the Hun", "Joan of Arc"]
    starting_campaigns = ["Attila the Hun"]

    def test_the_civs_are_the_scenarios_civs_deduplicated_in_order(self):
        world = self.build()
        civs = world.pool.civs.included
        self.assertEqual(list(dict.fromkeys(scenario.civ
                                            for scenario in world.pool.scenarios.included)), civs)
        self.assertEqual(len(set(civs)), len(civs), "a civ appeared twice")

    def test_builds_is_true_for_a_building_someone_puts_up(self):
        world = self.build()
        for building in Age2BuildingData:
            with self.subTest(building.name):
                self.assertEqual(any(civ.builds(building) for civ in world.pool.civs.included),
                                 world.pool.civs.builds(building))

    def test_any_trains_matches_the_civ_rosters(self):
        world = self.build()
        for unit in (Age2UnitData.VILLAGER_MALE, Age2UnitData.KNIGHT, Age2UnitData.MANGUDAI,
                     Age2UnitData.LONGBOWMAN, Age2UnitData.SCOUT_CAVALRY):
            with self.subTest(unit.name):
                self.assertEqual(any(unit in CIV_TO_UNITS[civ] for civ in world.pool.civs.included),
                                 world.pool.civs.any_trains(unit))

    def test_researches_matches_the_civ_rosters(self):
        world = self.build()
        for tech in Age2TechData:
            with self.subTest(tech.name):
                self.assertEqual(any(tech in CIV_TO_TECHS[civ] for civ in world.pool.civs.included),
                                 world.pool.civs.any_researches(tech))

    def test_a_one_campaign_seed_carries_only_its_own_civs(self):
        """Attila alone is Huns; adding Joan brings the French in, and neither leaks into the other."""
        attila = self.build_with(["Attila the Hun"])
        joan = self.build_with(["Joan of Arc"])
        both = self.build_with(["Attila the Hun", "Joan of Arc"])
        self.assertEqual(set(attila) | set(joan), set(both))
        self.assertFalse(set(attila) & set(joan), "a civ appears in both campaigns")

    def build_with(self, campaigns: list[str]):
        self.campaigns = campaigns
        self.starting_campaigns = campaigns[:1]
        return self.build().pool.civs.included


class TestScenarioPool(bases.Age2RuleTestBase):
    campaigns = ["Attila the Hun", "Joan of Arc"]
    starting_campaigns = ["Attila the Hun"]

    def test_included_is_the_campaigns_expanded_in_order(self):
        world = self.build()
        expected = [scenario for campaign in world.pool.campaigns.enabled
                    for scenario in world.pool.scenarios.of(campaign)]
        self.assertEqual(expected, world.pool.scenarios.included)

    def test_first_scenario_opens_its_campaign(self):
        world = self.build()
        for campaign in world.pool.campaigns.enabled:
            with self.subTest(campaign.campaign_name):
                first = world.pool.scenarios.first_scenario(campaign)
                self.assertEqual(world.pool.scenarios.of(campaign)[0], first)
                self.assertEqual(min(s.chapter for s in world.pool.scenarios.of(campaign)),
                                 first.chapter)


class TestBuildingPool(bases.Age2RuleTestBase):
    campaigns = ["Attila the Hun", "Joan of Arc"]
    starting_campaigns = ["Attila the Hun"]

    def shuffled(self, **options):
        return self.build(**options).pool.buildings.shuffled

    def test_nothing_shuffled_when_no_category_is_chosen(self):
        self.assertEqual([], self.shuffled(shuffle_buildings=set()))

    def test_a_building_needs_a_chosen_category(self):
        economy = self.shuffled(shuffle_buildings={BuildingOption.economy})
        for building in economy:
            with self.subTest(building.name):
                self.assertIn(BuildingOption.economy, building.building_options)

    def test_unique_is_a_qualifier_not_a_category(self):
        """Unique alone selects nothing: a unique building is sorted by its other category, so
        the Folwark would need Economy as well as Unique."""
        self.assertEqual([], self.shuffled(shuffle_buildings={BuildingOption.unique}))

    def test_no_unique_building_is_reachable_with_the_shipped_civs(self):
        """Age2CivData.builds sends a unique building to included_buildings, and neither the Huns
        nor the Franks declare any - so no unique building is ever shuffled today, whatever
        Shuffle Buildings says. A civ that declares one will change this."""
        with_unique = self.shuffled(shuffle_buildings={BuildingOption.economy,
                                                       BuildingOption.unique})
        without = self.shuffled(shuffle_buildings={BuildingOption.economy})
        self.assertEqual(without, with_unique)
        for building in with_unique:
            with self.subTest(building.name):
                self.assertNotIn(BuildingOption.unique, building.building_options)

    def test_only_buildings_somebody_builds(self):
        world = self.build()
        for building in world.pool.buildings.shuffled:
            with self.subTest(building.name):
                self.assertTrue(world.pool.civs.builds(building))

    def test_locations_and_shuffled_agree(self):
        """Buildings have no separate on/off toggle, so the two are the same list."""
        world = self.build()
        self.assertEqual(world.pool.buildings.shuffled, world.pool.buildings.locations)


class TestCampaignPool(bases.Age2RuleTestBase):
    campaigns = ["Attila the Hun", "Joan of Arc"]
    starting_campaigns = ["Attila the Hun"]

    def test_starting_is_a_subset_of_enabled_in_the_same_order(self):
        world = self.build()
        self.assertEqual([campaign for campaign in world.pool.campaigns.enabled
                          if campaign in world.pool.campaigns.starting],
                         world.pool.campaigns.starting)

    def test_definition_order_not_set_order(self):
        world = self.build()
        self.assertEqual([campaign for campaign in Age2CampaignData
                          if campaign in world.pool.campaigns.enabled],
                         world.pool.campaigns.enabled)


if __name__ == "__main__":
    unittest.main()
