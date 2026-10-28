import unittest
from unittest import mock

from rule_builder.rules import Has

from . import bases
from ..items.Items import Age2ItemData
from ..locations.Buildings import Age2BuildingData
from ..locations.connections.ScenarioResources import Tier
from ..locations.Scenarios import Age2ScenarioData
from ..locations.VillagerJobs import Age2VillagerJobData
from .test_economy_catalog import (
    LUMBERJACKS,
    VILLAGERS,
    ToyScenarioBase,
    building,
    job,
    tier,
)

TOWN_CENTER_WOOD = Age2ItemData.TOWN_CENTER_WOOD.item_name
TOWN_CENTER_STONE = Age2ItemData.TOWN_CENTER_STONE.item_name
UNLOCKED = "switch: unlocked"

class TestGoldMinersAtATownCenterPayForIt(ToyScenarioBase):
    ROUTE = "Gold Miners at a Town Center"
    MAP = {Tier.BASE: tier(gold_count=500)}
    GOLD_MINERS = (
        VILLAGERS,
        job(Age2VillagerJobData.GOLD_MINER_MALE),
        building(Age2BuildingData.TOWN_CENTER),
    )

    def test_with_no_standing_town_center_and_no_town_center_items_they_do_not_run(self):
        self.toy(self.MAP)
        self.assertNotIn(self.ROUTE, self.running(self.state(*self.GOLD_MINERS)))

    def test_with_the_town_center_items_they_run(self):
        self.toy(self.MAP)
        state = self.state(*self.GOLD_MINERS, TOWN_CENTER_WOOD, TOWN_CENTER_STONE)
        self.assertIn(self.ROUTE, self.running(state))

class TestABaseStoodByAScenarioItemIsItsOwnDropsite(bases.Age2RuleTestBase):
    campaigns = ["Genghis Khan"]
    starting_campaigns = ["Genghis Khan"]

    def test_farmers_and_lumberjacks_with_a_base_run_on_the_tayichiud_base_alone(self):
        self.build()
        revenge = self.world.rules.logic.for_scenario(Age2ScenarioData.AP_GENGHIS_2)
        economy = revenge.economy.has_economy_routes().resolve(self.world)
        state = self.state_without(TOWN_CENTER_WOOD, TOWN_CENTER_STONE)
        self.assertTrue(state.has(Age2ItemData.AP_GENGHIS_2_TAYICHIUD_BASE.item_name, self.world.player))
        running = {economy.routes[index].name for index in economy.running(state)}
        self.assertLessEqual({"Farmers", "Lumberjacks with a Base"}, running)

class TestOwnFarmerPaysSomeOfItsFarm(ToyScenarioBase):
    FARMER = (UNLOCKED, building(Age2BuildingData.FARM))

    def is_own_farmer_in_logic(self, *switches: str) -> bool:
        self.toy({})
        unlocked = mock.patch.object(self.scenario.starting_state, "is_unlocked", Has(UNLOCKED))
        with unlocked:
            location = self.world.rules.unit_rules.location_rule(Age2VillagerJobData.FARMER_MALE)
            return bool(location.resolve(self.world)(self.state(*switches)))

    def test_with_no_wood_route_of_some_it_is_out_of_logic(self):
        self.assertFalse(self.is_own_farmer_in_logic(*self.FARMER))

    def test_with_a_wood_route_of_some_it_is_in_logic(self):
        self.assertTrue(self.is_own_farmer_in_logic(*self.FARMER, *LUMBERJACKS))

if __name__ == "__main__":
    unittest.main()
