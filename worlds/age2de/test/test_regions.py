"""create_regions pulled the first scenario of each campaign out of the loop.

Two consequences. Its civ never reached included_civs, which is what decides further down which
buildings become locations - and all() over an empty included_civs is True, so a campaign whose
only scenario was the held-out one produced no building locations at all. And the except
StopIteration handler named first_scn, which is bound by the next() that raises, so an empty
campaign died with NameError instead of the OptionError it meant to raise.
"""
import unittest
from unittest import mock

from Options import OptionError
from test.general import setup_solo_multiworld

from . import bases
from .. import Age2World
from ..locations.Campaigns import Age2CampaignData
from ..locations.Scenarios import CAMPAIGN_TO_SCENARIOS

ATTILA = Age2CampaignData.ATTILA.campaign_name
JOAN = Age2CampaignData.JOAN.campaign_name


class TestCivilizationCollection(bases.Age2TestBase):
    options = {
        "enabled_campaigns": {ATTILA, JOAN},
        "starting_campaigns": {ATTILA},
    }

    def test_every_included_scenario_contributes_its_civilisation(self) -> None:
        # Passes before the fix too, because every chapter of a campaign shares one civ today.
        # It pins the invariant for the first campaign whose opener differs from the rest.
        for campaign in self.world.included_campaigns:
            for scenario in CAMPAIGN_TO_SCENARIOS[campaign]:
                self.assertIn(scenario.civ, self.world.included_civs,
                              f"{scenario.scenario_name} never registered its civilisation")

    def test_the_first_scenario_of_a_campaign_counts(self) -> None:
        for campaign in self.world.included_campaigns:
            opener = CAMPAIGN_TO_SCENARIOS[campaign][0]
            self.assertIn(opener.civ, self.world.included_civs,
                          "the campaign's first scenario was held out of the civ loop")


class TestVictoryEvents(bases.Age2TestBase):
    options = {
        "enabled_campaigns": {ATTILA, JOAN},
        "starting_campaigns": {ATTILA},
    }

    def test_the_victory_event_has_no_address(self) -> None:
        victory = self.world.get_location("Victory")
        self.assertIsNone(victory.address,
                          "the Victory event carried address 0, which is the Victory item's id")

    def test_each_scenario_has_one_completion_event(self) -> None:
        names = [location.name for location in self.multiworld.get_locations(self.player)]
        for campaign in self.world.included_campaigns:
            for scenario in CAMPAIGN_TO_SCENARIOS[campaign]:
                event = "Complete " + scenario.scenario_name
                self.assertEqual(1, names.count(event),
                                 f"{event} was registered {names.count(event)} times")

    def test_completion_events_are_registered_with_their_region(self) -> None:
        for campaign in self.world.included_campaigns:
            for scenario in CAMPAIGN_TO_SCENARIOS[campaign]:
                region = self.world.get_region(scenario.scenario_name)
                event = "Complete " + scenario.scenario_name
                self.assertIn(event, [location.name for location in region.locations],
                              "a hand-built Location never reached its region")


class TestEmptyCampaign(unittest.TestCase):
    def test_a_campaign_with_no_scenarios_is_an_option_error(self) -> None:
        world: Age2World = setup_solo_multiworld(Age2World, ()).worlds[1]
        world.options.enabled_campaigns.value = {ATTILA, JOAN}
        world.options.starting_campaigns.value = {ATTILA}
        world.generate_early()

        empty = dict(CAMPAIGN_TO_SCENARIOS)
        empty[Age2CampaignData.JOAN] = []
        with mock.patch.dict("worlds.age2de.CAMPAIGN_TO_SCENARIOS", empty, clear=True):
            with self.assertRaises(OptionError):
                world.create_regions()


if __name__ == "__main__":
    unittest.main()
