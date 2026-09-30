"""The pools: what this seed contains, decided once in generate_early and read everywhere."""

import unittest

from . import bases
from ..locations.Buildings import Age2BuildingData
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
