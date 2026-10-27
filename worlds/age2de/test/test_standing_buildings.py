"""Buildings that already stand on the map count, and are not bought a second time."""

import unittest

from . import bases
from ..items.Items import Age2ItemData
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

    def test_the_two_buildings_for_an_advance_can_be_ones_already_standing(self):
        """Attila 1's Bleda's Camp puts a Mill, Lumber Camp and Barracks on the map. Advancing out
        of the Dark Age asks for two buildings, and those three are two of them - without the camp
        the player would also need the building items, and this is the difference."""
        self.build(techsanity=3, unitsanity=2, shuffle_ages=1)
        scenario = self.world.rules.logic.for_scenario(Age2ScenarioData.AP_ATTILA_1)
        state = self.state_without(*[building.item.item_name
                                     for building in DARK_AGE_BUILDINGS])
        for building in DARK_AGE_BUILDINGS:
            with self.subTest(building.name):
                self.assertFalse(scenario.buildings.can_build_structurally(building)
                                 .resolve(self.world)(state),
                                 "the building item was not actually withheld")
        standing = [building for building in DARK_AGE_BUILDINGS
                    if scenario.has_building_structurally(building).resolve(self.world)(state)]
        self.assertGreaterEqual(len(standing), 2, "Bleda's Camp should leave buildings standing")
        age_up = scenario.ages.age_up_requirement_structurally(Age2AgeData.FEUDAL)
        self.assertTrue(age_up.resolve(self.world)(state))

    def test_a_standing_town_centre_is_not_bought_again(self):
        """Attila 3 opens with a Town Centre, so advancing wants neither the item nor the 275 wood
        and 100 stone that putting one up would cost."""
        self.build(techsanity=3, unitsanity=2, shuffle_ages=1)
        scenario = self.world.rules.logic.for_scenario(Age2ScenarioData.AP_ATTILA_3)
        wanted = self.deps(scenario.ages.can_reach_structurally(Age2AgeData.CASTLE))
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


class TestABaseStandsATownCenter(bases.Age2RuleTestBase):
    """A base is more than a Town Center, but never less: whatever gives a scenario its base has
    to declare the Town Center standing too. Attila 1's Bleda's Camp once did not, and the budget
    and the age-ups quietly paid for a Town Center the camp had already put up."""

    campaigns = ["Attila the Hun", "Joan of Arc", "Genghis Khan"]
    starting_campaigns = ["Attila the Hun"]

    def test_every_standing_town_center_is_a_base(self):
        from BaseClasses import CollectionState
        from ..Options import BuildingOption, ShuffleVillager
        self.build(
            shuffle_villager=ShuffleVillager.option_include_professions,
            shuffle_buildings={BuildingOption.base},
        )
        for scenario in self.world.rules.logic.scenarios:
            state = scenario.starting_state
            town_center = state.starts_with_building[Age2BuildingData.TOWN_CENTER].resolve(self.world)
            if town_center.always_false:
                continue
            base = scenario.can_have_base().resolve(self.world)
            with_town_center = CollectionState(self.multiworld)
            for name in town_center.item_dependencies():
                with_town_center.collect(self.world.create_item(name), prevent_sweep=True)
            with self.subTest(scenario.scenario.scenario_name):
                self.assertTrue(town_center(with_town_center),
                                "collecting the Town Center's items should stand it")
                self.assertTrue(base(with_town_center),
                                "the Town Center stands but the base still has to be built")


class TestTheBaseIsPaidByItsItems(bases.Age2RuleTestBase):
    """A base is paid by the items that seed it - the villagers' food, and the Town Center's wood
    and stone where none stands - never by the rest of the starting pile or an easy source."""

    campaigns = ["Attila the Hun", "Joan of Arc"]
    starting_campaigns = ["Attila the Hun"]

    FOOD = Age2ItemData.STARTING_VILLAGER_FOOD.item_name
    WOOD = Age2ItemData.TOWN_CENTER_WOOD.item_name
    STONE = Age2ItemData.TOWN_CENTER_STONE.item_name

    def deps(self, scenario: Age2ScenarioData) -> set[str]:
        logic = self.world.rules.logic.for_scenario(scenario)
        return set(logic.has_base().resolve(self.world).item_dependencies())

    def test_a_base_to_build_asks_for_all_three(self):
        self.build()
        self.assertLessEqual({self.FOOD, self.WOOD, self.STONE}, self.deps(Age2ScenarioData.AP_ATTILA_1))

    def test_a_standing_town_center_needs_only_the_food(self):
        """The Walls of Constantinople always has its Town Center."""
        self.build()
        wanted = self.deps(Age2ScenarioData.AP_ATTILA_3)
        self.assertIn(self.FOOD, wanted)
        self.assertNotIn(self.WOOD, wanted)
        self.assertNotIn(self.STONE, wanted)


class TestJoan4FrenchCampStands(bases.Age2RuleTestBase):
    """Joan 4's "AP Give Base" trigger hands P1 the French Camp from Gaia: a Town Center, a Mill,
    a Lumber Camp and a Mining Camp. The logic recorded none of them, so the base was bought a
    second time and the Lumber Camp asked for a seed item the map had already paid."""

    campaigns = ["Attila the Hun", "Joan of Arc"]
    starting_campaigns = ["Attila the Hun"]

    CAMP = Age2ItemData.AP_JOAN_4_FRENCH_CAMP.item_name
    CAMP_BUILDINGS = (Age2BuildingData.TOWN_CENTER, Age2BuildingData.MILL,
              Age2BuildingData.LUMBER_CAMP, Age2BuildingData.MINING_CAMP)

    def joan_4(self):
        return self.world.rules.logic.for_scenario(Age2ScenarioData.AP_JOAN_4)

    def test_the_camp_stands_all_four_buildings_and_nothing_stands_without_it(self):
        self.build()
        standing = self.joan_4().starting_state.starts_with_building
        with_camp = self.state_with(self.CAMP)
        without_camp = self.state_with()
        for building in self.CAMP_BUILDINGS:
            with self.subTest(building.name):
                rule = standing[building].resolve(self.world)
                self.assertTrue(rule(with_camp), "the French Camp should stand it")
                self.assertFalse(rule(without_camp), "nothing stands before the camp arrives")

    def test_the_base_no_longer_asks_for_the_town_center_items(self):
        """The camp's Town Center is already up, so the 275 wood and 100 stone that putting one
        up would cost are not Joan 4's to find."""
        self.build()
        state = self.state_without(Age2ItemData.TOWN_CENTER_WOOD.item_name,
                                   Age2ItemData.TOWN_CENTER_STONE.item_name)
        self.assertTrue(self.joan_4().has_base().resolve(self.world)(state))

    def test_the_lumber_camp_needs_no_seed_item(self):
        """A building standing at the start asks for no seed item, so the Lumber Camp route runs
        with Starting Lumber Camp Wood withheld."""
        self.build()
        scenario = self.joan_4()
        economy = scenario.economy.has_economy_routes().resolve(self.world)
        state = self.state_without(Age2ItemData.LUMBER_CAMP_WOOD.item_name)
        running = {economy.routes[index].name for index in economy.running(state)}
        self.assertIn("Lumberjacks at a Lumber Camp", running)
