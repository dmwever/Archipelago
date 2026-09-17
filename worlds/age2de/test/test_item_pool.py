"""smart_add_starting_resources had two defects that cancelled each other out in the pool count.

The `>` branch halved the four target amounts and continued without reducing locations_to_fill,
and ceil(x / amount) is at least 1 for any x above zero, so the worst case floored at four: one
to three remaining locations never terminated. The `==` branch called create_item four times over
and appended none of it, so it returned fewer items than asked for - create_items then made the
difference up with plain filler, which is why generation still completed.
"""
from collections import Counter

from . import bases
from ..items import Items
from ..locations.Campaigns import Age2CampaignData

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
            got = self.world.smart_add_starting_resources(wanted)
            self.assertEqual(wanted, len(got), f"asked for {wanted} items, got {len(got)}")

    def test_zero_locations_returns_nothing(self) -> None:
        self.assertEqual([], self.world.smart_add_starting_resources(0))

    def test_a_negative_count_returns_nothing(self) -> None:
        self.assertEqual([], self.world.smart_add_starting_resources(-5))

    def test_the_exact_fit_hands_back_the_large_items(self) -> None:
        # 1000/250 + 1000/250 + 750/250 + 500/125 = 4 + 4 + 3 + 4 = 15.
        got = self.world.smart_add_starting_resources(15)
        self.assertEqual(
            Counter({
                Items.Age2ItemData.STARTING_WOOD_LARGE.item_name: 4,
                Items.Age2ItemData.STARTING_FOOD_LARGE.item_name: 4,
                Items.Age2ItemData.STARTING_GOLD_LARGE.item_name: 3,
                Items.Age2ItemData.STARTING_STONE_LARGE.item_name: 4,
            }),
            Counter(item.name for item in got),
            "the exact-fit branch created items and threw them away",
        )

    def test_everything_returned_is_a_starting_resource(self) -> None:
        for wanted in (5, 15, 30):
            for item in self.world.smart_add_starting_resources(wanted):
                self.assertIsInstance(Items.NAME_TO_ITEM[item.name].type, Items.StartingResources)


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
