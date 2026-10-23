"""Build Fish Trap was in logic without a Fishing Ship, and asked for villagers and the Builder
profession instead, though only a Fishing Ship can put a Fish Trap up (playtest #12)."""

import unittest

from . import bases
from ..items.Items import Age2ItemData
from ..locations.Buildings import Age2BuildingData
from ..locations.Scenarios import Age2ScenarioData
from ..locations.Units import Age2UnitData
from ..Options import ShuffleVillager, UnitsanityItems

BUILD_FISH_TRAP = Age2BuildingData.FISH_TRAP.location_name
FISHING_SHIP_LINE = Age2ItemData.UNIT_LINE_FISHING_SHIP.item_name
BUILDER = Age2ItemData.PROFESSION_BUILDER.item_name
JOAN_2_DOCK = Age2ItemData.AP_JOAN_2_DOCK.item_name


class TestFishTrapBuilder(bases.Age2RuleTestBase):
    campaigns = ["Attila the Hun", "Joan of Arc", "Genghis Khan"]
    starting_campaigns = ["Attila the Hun"]

    def build_fish_trap_dependencies(self) -> set[str]:
        rule = self.world.rules.logic.can_build_location_anywhere(Age2BuildingData.FISH_TRAP)
        return set(rule.resolve(self.world).item_dependencies())

    def test_a_fish_trap_needs_a_fishing_ship(self):
        self.build()
        self.assertTrue(self.can_reach(BUILD_FISH_TRAP, self.state_without()))
        self.assertFalse(self.can_reach(BUILD_FISH_TRAP, self.state_without(FISHING_SHIP_LINE)))

    def test_the_fishing_ship_items_are_dependencies(self):
        for mode in (UnitsanityItems.option_unit_line, UnitsanityItems.option_buildings):
            with self.subTest(unitsanity_items=mode):
                self.build(unitsanity_items=mode)
                logic = self.world.rules.logic
                fishing_ship_items = set(logic.units.has_unit_items(Age2UnitData.FISHING_SHIP)
                                         .resolve(self.world).item_dependencies())
                self.assertTrue(fishing_ship_items, "the Fishing Ship should be an item in this mode")
                self.assertLessEqual(fishing_ship_items, self.build_fish_trap_dependencies())

    def test_joan_2s_dock_item_stands_a_dock(self):
        self.build(shuffle_villager=ShuffleVillager.option_include_professions)
        joan_2 = self.world.rules.logic.for_scenario(Age2ScenarioData.AP_JOAN_2)
        dock = joan_2.has_building(Age2BuildingData.DOCK).resolve(self.world)
        self.assertTrue(dock(self.state_without(BUILDER)))
        self.assertFalse(dock(self.state_without(BUILDER, JOAN_2_DOCK)))

    def test_a_fish_trap_beside_joan_2s_dock_does_not_ask_for_the_builder(self):
        # Asked of the building, not the Build location: the location also pays the trap's wood,
        # and chopping wood still wants a Lumber Camp, which a Builder puts up.
        self.build(shuffle_villager=ShuffleVillager.option_include_professions)
        joan_2 = self.world.rules.logic.for_scenario(Age2ScenarioData.AP_JOAN_2)
        fish_trap = joan_2.buildings.can_build_building(Age2BuildingData.FISH_TRAP).resolve(self.world)
        self.assertTrue(fish_trap(self.state_without(BUILDER)))
        self.assertFalse(fish_trap(self.state_without(BUILDER, JOAN_2_DOCK)))
        self.assertFalse(fish_trap(self.state_without(BUILDER, FISHING_SHIP_LINE)))

    def test_every_other_building_still_asks_for_builders(self):
        self.build(shuffle_villager=ShuffleVillager.option_include_professions)
        for scenario in self.world.rules.logic.scenarios:
            for building in Age2BuildingData:
                if building is Age2BuildingData.FISH_TRAP:
                    continue
                rule = scenario.buildings.can_build_building(building).resolve(self.world)
                if rule.always_false:
                    continue
                with self.subTest(scenario=scenario.scenario.scenario_name, building=building.name):
                    self.assertIn(BUILDER, set(rule.item_dependencies()))


if __name__ == "__main__":
    unittest.main()
