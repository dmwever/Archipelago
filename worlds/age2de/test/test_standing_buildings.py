"""Buildings that already stand on the map count, and are not bought a second time."""

import unittest

from . import bases
from ..locations.Ages import Age2AgeData
from ..locations.Buildings import Age2BuildingData
from ..locations.Scenarios import Age2ScenarioData
from ..locations.Techs import Age2TechData

DARK_AGE_BUILDINGS = (Age2BuildingData.MILL, Age2BuildingData.LUMBER_CAMP,
                      Age2BuildingData.MINING_CAMP, Age2BuildingData.DOCK,
                      Age2BuildingData.BARRACKS)


class TestStandingBuildingsCount(bases.Age2RuleTestBase):
    campaigns = ["Attila the Hun", "Joan of Arc"]
    starting_campaigns = ["Attila the Hun"]

    def deps(self, rule) -> set[str]:
        return set(rule.resolve(self.world).item_dependencies())

    def test_the_two_buildings_for_a_climb_can_be_ones_already_standing(self):
        """Attila 1's Bleda's Camp puts a Mill, Lumber Camp and Barracks on the map. The climb out
        of the Dark Age asks for two buildings, and those three are two of them - without the camp
        the player would also need the building items, and this is the difference."""
        self.build(techsanity=3, unitsanity=2, shuffle_ages=1)
        scenario = self.world.rules.logic.for_scenario(Age2ScenarioData.AP_ATTILA_1)
        state = self.state_without(*[building.item.item_name
                                     for building in DARK_AGE_BUILDINGS])
        for building in DARK_AGE_BUILDINGS:
            with self.subTest(building.name):
                self.assertFalse(scenario.buildings.can_build_building(building)
                                 .resolve(self.world)(state),
                                 "the building item was not actually withheld")
        standing = [building for building in DARK_AGE_BUILDINGS
                    if scenario.has_building(building).resolve(self.world)(state)]
        self.assertGreaterEqual(len(standing), 2, "Bleda's Camp should leave buildings standing")
        self.assertTrue(scenario.ages.two_from(Age2AgeData.DARK).resolve(self.world)(state))

    def test_a_standing_town_centre_is_not_bought_again(self):
        """Attila 3 opens with a Town Centre, so its climb wants neither the item nor the 275 wood
        and 100 stone that putting one up would cost."""
        self.build(techsanity=3, unitsanity=2, shuffle_ages=1)
        scenario = self.world.rules.logic.for_scenario(Age2ScenarioData.AP_ATTILA_3)
        wanted = self.deps(scenario.ages.climb(Age2AgeData.CASTLE))
        self.assertNotIn(Age2BuildingData.TOWN_CENTER.item.item_name, wanted)
        self.assertFalse([name for name in wanted if "Stone" in name])

    def test_a_tech_researched_at_a_standing_building_does_not_want_the_item(self):
        """Attila 3's Blacksmith stands, so Iron Casting never asks for the Blacksmith item."""
        self.build(techsanity=3, unitsanity=2, shuffle_ages=1)
        scenario = self.world.rules.logic.for_scenario(Age2ScenarioData.AP_ATTILA_3)
        wanted = self.deps(scenario.techs.can_research(Age2TechData.IRON_CASTING))
        self.assertNotIn(Age2BuildingData.BLACKSMITH.item.item_name, wanted)


if __name__ == "__main__":
    unittest.main()
