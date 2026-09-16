"""included_campaigns and starting_campaigns used to be sets of enum members.

Age2CampaignData builds its members with object.__new__, so they hash by identity and a set
iterates in whatever order that run produced. That order picks region creation order, the order
items enter the pool, and the order Logic.scenarios is filled - which is the order that decides
which scenario gets the degenerate can_build_base. Two runs of one seed could disagree.
"""
from . import bases
from ..locations.Campaigns import Age2CampaignData
from ..locations.Scenarios import CAMPAIGN_TO_SCENARIOS

ATTILA = Age2CampaignData.ATTILA.campaign_name
JOAN = Age2CampaignData.JOAN.campaign_name


class TestCampaignOrder(bases.Age2TestBase):
    options = {
        "enabled_campaigns": {ATTILA, JOAN},
        "starting_campaigns": {ATTILA},
    }

    def test_campaigns_are_kept_in_definition_order(self) -> None:
        self.assertEqual(
            [Age2CampaignData.ATTILA, Age2CampaignData.JOAN],
            self.world.included_campaigns,
            "a set here made region, item and rule order depend on how the members hashed",
        )

    def test_starting_campaigns_follow_the_same_order(self) -> None:
        self.assertEqual([Age2CampaignData.ATTILA], self.world.starting_campaigns)

    def test_regions_are_created_in_campaign_order(self) -> None:
        expected = [scenario.scenario_name
                    for campaign in self.world.included_campaigns
                    for scenario in CAMPAIGN_TO_SCENARIOS[campaign]]
        created = [region.name for region in self.multiworld.get_regions(self.player)]
        self.assertEqual(expected, [name for name in created if name in expected],
                         "scenario regions were not created in campaign order")

    def test_scenario_logic_follows_region_order(self) -> None:
        expected = [scenario.scenario_name
                    for campaign in self.world.included_campaigns
                    for scenario in CAMPAIGN_TO_SCENARIOS[campaign]]
        # ScenarioRules keeps its scenario only as the entrance it rules, and the entrance is
        # named after the scenario.
        built = [rules.entrance.name for rules in self.world.rules.scenario_rules]
        self.assertEqual(expected, built,
                         "scenario rules were built in a different order than the regions")
