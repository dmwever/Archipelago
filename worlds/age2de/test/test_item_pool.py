"""smart_add_starting_resources had two defects that cancelled each other out in the pool count.

The `>` branch halved the four target amounts and continued without reducing locations_to_fill,
and ceil(x / amount) is at least 1 for any x above zero, so the worst case floored at four: one
to three remaining locations never terminated. The `==` branch called create_item four times over
and appended none of it, so it returned fewer items than asked for - create_items then made the
difference up with plain filler, which is why generation still completed.
"""
from collections import Counter
import unittest

from BaseClasses import ItemClassification

from . import bases
from ..items import Items
from ..locations.Campaigns import Age2CampaignData
from ..locations.Scenarios import CAMPAIGN_TO_SCENARIOS

ATTILA = Age2CampaignData.ATTILA.campaign_name
JOAN = Age2CampaignData.JOAN.campaign_name


class TestSmartStartingResources(bases.Age2TestBase):
    options = {
        "enabled_campaigns": {ATTILA},
        "starting_campaigns": {ATTILA},
    }

    def test_returns_exactly_the_number_asked_for(self) -> None:
        # 1 to 3 is the range that used to hang; 15 and 20 returned 0 and 8.
        for wanted in range(0, 40):
            got = self.world.pool.resources.build_items(wanted)
            self.assertEqual(wanted, len(got), f"asked for {wanted} items, got {len(got)}")

    def test_zero_locations_returns_nothing(self) -> None:
        self.assertEqual([], self.world.pool.resources.build_items(0))

    def test_a_negative_count_returns_nothing(self) -> None:
        self.assertEqual([], self.world.pool.resources.build_items(-5))

    def test_the_exact_fit_hands_back_the_large_items(self) -> None:
        # 725/250 + 850/250 + 750/250 + 400/125 = 3 + 4 + 3 + 4 = 14. The targets came down by
        # what the three town-centre items now contribute to the same totals.
        got = self.world.pool.resources.build_items(14)
        self.assertEqual(
            Counter({
                Items.Age2ItemData.STARTING_WOOD_LARGE.item_name: 3,
                Items.Age2ItemData.STARTING_FOOD_LARGE.item_name: 4,
                Items.Age2ItemData.STARTING_GOLD_LARGE.item_name: 3,
                Items.Age2ItemData.STARTING_STONE_LARGE.item_name: 4,
            }),
            Counter(item.item_name for item in got),
            "the exact-fit branch created items and threw them away",
        )

    def test_everything_returned_is_a_starting_resource(self) -> None:
        for wanted in (5, 15, 30):
            for item in self.world.pool.resources.build_items(wanted):
                self.assertIsInstance(item.type, Items.StartingResources)


class TestTownCentreItems(bases.Age2TestBase):
    """Starting Town Center Stone declared Resource.FOOD. A Town Center costs wood and stone, and
    nothing in Python reads TCResources.type yet - the XS side is what would act on it."""

    options = {
        "enabled_campaigns": {ATTILA},
        "starting_campaigns": {ATTILA},
    }

    def test_the_pair_covers_the_real_cost(self) -> None:
        cost = Items.Age2ItemData.TOWN_CENTER.type.needed_resources
        granted = {
            Items.Age2ItemData.TOWN_CENTER_WOOD.type.type:
                Items.Age2ItemData.TOWN_CENTER_WOOD.type.amount,
            Items.Age2ItemData.TOWN_CENTER_STONE.type.type:
                Items.Age2ItemData.TOWN_CENTER_STONE.type.amount,
        }
        self.assertEqual({resource: int(amount) for resource, amount in cost.items()}, granted,
                         "the Town Center items do not add up to a Town Center")

    def test_the_villager_food_joins_the_pair(self) -> None:
        """The third of the opening set: a town centre you cannot put villagers in front of is
        not a start. 150 food is three villagers at 50 each."""
        food = Items.Age2ItemData.STARTING_VILLAGER_FOOD
        self.assertIsInstance(food.type, Items.TCResources)
        self.assertEqual(food.type.type, Items.Resource.FOOD)
        self.assertEqual(food.type.amount, 150)
        self.assertIn(food, Items.CATEGORY_TO_ITEMS[Items.TCResources])

    def test_exactly_one_of_each_opening_item_reaches_the_pool(self) -> None:
        names = [item.name for item in self.multiworld.itempool]
        for item in Items.CATEGORY_TO_ITEMS[Items.TCResources]:
            with self.subTest(item.item_name):
                self.assertEqual(names.count(item.item_name), 1)


class TestStartingResourcesAreProgression(bases.Age2TestBase):
    """They became progression when the economy started counting what they add up to:
    state.prog_items only ever holds advancement items."""

    options = {
        "enabled_campaigns": {ATTILA},
        "starting_campaigns": {ATTILA},
    }

    def test_the_band_is_progression(self) -> None:
        for item in Items.CATEGORY_TO_ITEMS[Items.StartingResources]:
            with self.subTest(item.item_name):
                self.assertEqual(Items.classification_for(item),
                                 ItemClassification.progression)

    def test_they_are_still_not_filler(self) -> None:
        """create_filler draws from filler_items, which is the Resources band alone. A starting
        resource turning up there would make the padding fight the economy."""
        for item in Items.CATEGORY_TO_ITEMS[Items.StartingResources]:
            with self.subTest(item.item_name):
                self.assertNotIn(item, Items.filler_items)

    def test_the_tally_matches_the_pool(self) -> None:
        by_hand = {resource: 0 for resource in Items.Resource}
        pooled = [item for item in self.multiworld.itempool if item.player == self.world.player]
        for item in pooled + self.multiworld.precollected_items[self.world.player]:
            payload = Items.NAME_TO_ITEM[item.name].type
            if isinstance(payload, (Items.StartingResources, Items.TCResources)):
                by_hand[payload.type] += payload.amount
        self.assertEqual(self.world.pool.resources.totals, by_hand)


class TestPoolBalances(bases.Age2TestBase):
    options = {
        "enabled_campaigns": {ATTILA, JOAN},
        "starting_campaigns": {ATTILA},
    }

    def test_the_pool_matches_the_location_count(self) -> None:
        unfilled = self.multiworld.get_unfilled_locations(self.player)
        self.assertEqual(len(unfilled), len(self.multiworld.itempool))

    def test_starting_resources_reach_the_pool(self) -> None:
        kinds = [Items.NAME_TO_ITEM[item.name].type for item in self.multiworld.itempool]
        self.assertTrue(any(isinstance(kind, Items.StartingResources) for kind in kinds),
                        "no starting resources reached the pool")


class TestProgressiveScenarioCoverage(unittest.TestCase):
    """A campaign is opened by its Campaign item and then advanced one chapter per Progressive
    Scenario, so the pool has to hold exactly one progressive fewer than the campaign has chapters.
    Nothing enforces that today: create_items just makes num_additional_scenarios copies. Too few
    and the campaign's last chapters can never be reached, with generation succeeding anyway; too
    many and the surplus sits in the pool as items that unlock nothing. A campaign added with the
    wrong count would land either way in silence.
    """

    def progressives(self, campaign: Age2CampaignData) -> list[Items.Age2ItemData]:
        return [item for item in Items.CATEGORY_TO_ITEMS[Items.ProgressiveScenario]
                if item.type.vanilla_campaign == campaign]

    def test_every_campaign_has_exactly_one_progressive_item(self) -> None:
        for campaign in Age2CampaignData:
            self.assertEqual(1, len(self.progressives(campaign)),
                             f"{campaign.campaign_name} needs exactly one progressive item; "
                             "create_items counts copies off a single member")

    def test_the_progressives_reach_the_last_chapter_and_no_further(self) -> None:
        for campaign in Age2CampaignData:
            chapters = len(CAMPAIGN_TO_SCENARIOS[campaign])
            progressive = self.progressives(campaign)[0]
            self.assertEqual(chapters, progressive.type.num_additional_scenarios + 1,
                             f"{campaign.campaign_name} has {chapters} chapters but its "
                             f"progressive makes {progressive.type.num_additional_scenarios} "
                             "copies; the campaign item opens the first chapter and each copy "
                             "opens one more")

    def test_every_campaign_has_exactly_one_campaign_item(self) -> None:
        for campaign in Age2CampaignData:
            owned = [item for item in Items.CATEGORY_TO_ITEMS[Items.Campaign]
                     if item.type.vanilla_campaign == campaign]
            self.assertEqual(1, len(owned),
                             f"{campaign.campaign_name} needs exactly one campaign item, or "
                             "sync_unlocked's any() would open it from the wrong one")


class TestTheHouseComesEarly(bases.Age2TestBase):
    """A civilisation that builds houses has no base without one, so a House found late left
    Joan 3 with no easy source of anything for most of a seed. It is an early item whenever it is
    shuffled at all."""

    options = {
        "enabled_campaigns": {ATTILA, JOAN},
        "starting_campaigns": {ATTILA},
        "shuffle_buildings": {"Economy"},
    }

    def test_the_house_is_asked_for_early(self) -> None:
        house = Items.Age2ItemData.HOUSE.item_name
        self.assertEqual(1, self.multiworld.early_items[self.player].get(house))

    def test_the_house_lands_in_the_first_sphere(self) -> None:
        from Fill import distribute_items_restrictive
        distribute_items_restrictive(self.multiworld)
        house = Items.Age2ItemData.HOUSE.item_name
        first_sphere = next(iter(self.multiworld.get_spheres()))
        holders = [location for location in first_sphere
                   if location.item.player == self.player and location.item.name == house]
        self.assertEqual(1, len(holders), "the House was not placed in the first sphere")


class TestAnUnshuffledHouseIsLeftAlone(bases.Age2TestBase):
    """With economy buildings unshuffled the House is precollected, so there is nothing to place."""

    options = {
        "enabled_campaigns": {ATTILA, JOAN},
        "starting_campaigns": {ATTILA},
        "shuffle_buildings": {"Tech"},
    }

    def test_the_house_is_not_an_early_item(self) -> None:
        house = Items.Age2ItemData.HOUSE.item_name
        self.assertNotIn(house, self.multiworld.early_items[self.player])


class TestHunsNeverAskForAHouse(bases.Age2TestBase):
    """Huns build no houses, so an Attila-only seed has no House location and no House item."""

    options = {
        "enabled_campaigns": {ATTILA},
        "starting_campaigns": {ATTILA},
        "shuffle_buildings": {"Economy"},
    }

    def test_the_house_is_not_an_early_item(self) -> None:
        house = Items.Age2ItemData.HOUSE.item_name
        self.assertNotIn(house, self.multiworld.early_items[self.player])
