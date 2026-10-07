import os
import pathlib
import re
import unittest

from ..Options import MinimumFillerLocations
from ..generation.pools import FillerPool
from ..client.handlers.install.FillerData import FillerData
from ..locations.FillerLocations import (
    Age2FillerLocationData, FillerKind, FILLER_LOCATION_COUNT, KIND_TO_LOCATIONS)
from ..locations.UnitLocations import unit_location
from ..locations.connections.LocationMapping import location_name_to_id, location_id_to_name
from .bases import Age2TestBase

AGEIPELAGO_XS = pathlib.Path(
    os.environ.get("AGEIPELAGO_PATH", "C:/Users/dmwev/Documents/GitHub/Ageipelago")
) / "age 2 files/resources/_common/xs"


class TestTheCatalogue(unittest.TestCase):
    def test_every_milestone_is_in_the_datapackage(self) -> None:
        for filler in Age2FillerLocationData:
            with self.subTest(filler.location_name):
                self.assertEqual(filler.id, location_name_to_id[filler.location_name])
                self.assertEqual(filler.location_name, location_id_to_name[filler.id])

    def test_every_name_is_marked_as_a_milestone(self) -> None:
        for filler in Age2FillerLocationData:
            with self.subTest(filler.location_name):
                self.assertTrue(filler.location_name.startswith("Milestone: "))

    def test_the_only_character_the_game_rewrites_is_the_percent_sign(self) -> None:
        from ..client.handlers.MessageHandler import _parse_evil_characters
        for filler in Age2FillerLocationData:
            with self.subTest(filler.location_name):
                self.assertEqual(
                    _parse_evil_characters(filler.location_name.replace("%", "")),
                    filler.location_name.replace("%", ""))

    def test_the_option_ceiling_is_the_whole_catalogue(self) -> None:
        self.assertEqual(FILLER_LOCATION_COUNT, MinimumFillerLocations.range_end)

    def test_a_collect_milestone_names_its_resource_and_no_other_kind_does(self) -> None:
        for filler in Age2FillerLocationData:
            with self.subTest(filler.location_name):
                if filler.kind is FillerKind.COLLECT:
                    self.assertIsNotNone(filler.resource)
                else:
                    self.assertIsNone(filler.resource)

    def test_thresholds_rise_within_a_kind(self) -> None:
        for kind, members in KIND_TO_LOCATIONS.items():
            if kind is FillerKind.COLLECT:
                continue
            with self.subTest(kind.name):
                thresholds = [member.threshold for member in members]
                self.assertEqual(sorted(thresholds), thresholds)

class TestTheIdBand(unittest.TestCase):

    def test_ids_are_acked_globally(self) -> None:
        for filler in Age2FillerLocationData:
            with self.subTest(filler.location_name):
                self.assertLess(filler.id // 100, 101)

    def test_no_id_is_read_as_a_unit(self) -> None:
        for filler in Age2FillerLocationData:
            with self.subTest(filler.location_name):
                self.assertIsNone(unit_location(filler.id))

    def test_no_name_or_id_collides_with_another_family(self) -> None:
        names = {filler.location_name for filler in Age2FillerLocationData}
        ids = {filler.id for filler in Age2FillerLocationData}
        others = {name: id for name, id in location_name_to_id.items() if name not in names}
        self.assertEqual(set(), ids & set(others.values()))
        self.assertEqual(len(location_name_to_id), len(set(location_name_to_id)))


class TestSelection(Age2TestBase):
    options = {"minimum_filler_locations": MinimumFillerLocations.range_end}

    def test_only_milestones_some_scenario_affords_are_selected(self) -> None:
        for filler in self.world.pool.filler.locations:
            with self.subTest(filler.location_name):
                self.assertTrue(self.world.pool.filler.is_earnable(filler))

    def test_the_slider_is_a_floor_not_a_ceiling(self) -> None:
        pool = self.world.pool.filler
        self.assertEqual(len(pool.locations), min(pool.minimum, len(pool.earnable)))

    def test_every_selected_milestone_is_a_real_location(self) -> None:
        placed = {location.name for location in self.multiworld.get_locations(self.player)}
        for filler in self.world.pool.filler.locations:
            with self.subTest(filler.location_name):
                self.assertIn(filler.location_name, placed)

    def test_no_selected_milestone_is_unreachable(self) -> None:
        state = self.multiworld.get_all_state(False)
        for filler in self.world.pool.filler.locations:
            with self.subTest(filler.location_name):
                self.assertTrue(
                    self.multiworld.get_location(filler.location_name, self.player)
                    .can_reach(state))


class TestTheEconomyDoesNotMove(unittest.TestCase):

    SEED = 20260406

    def build(self, minimum: int):
        from test.general import setup_solo_multiworld
        from .. import Age2World
        from ..items import Items
        world = setup_solo_multiworld(Age2World, (), self.SEED).worlds[1]
        world.options.minimum_filler_locations.value = minimum
        for step in ("generate_early", "create_regions", "create_items"):
            getattr(world, step)()
        starting = [item for item in world.multiworld.itempool
                    if item.player == world.player
                    and isinstance(Items.NAME_TO_ITEM[item.name].type, Items.StartingResources)]
        return world, len(starting)

    def test_the_slider_does_not_grow_the_resource_budget(self) -> None:
        bare, bare_items = self.build(0)
        full, full_items = self.build(MinimumFillerLocations.range_end)
        self.assertEqual(bare_items, full_items,
                         "milestone locations were spent on starting resources")
        self.assertGreater(len(full.pool.filler.locations), 0,
                           "nothing was selected, so this proves nothing")

    def test_the_slider_does_add_locations(self) -> None:
        bare, _ = self.build(0)
        full, _ = self.build(MinimumFillerLocations.range_end)
        self.assertEqual(
            len(full.multiworld.get_unfilled_locations(full.player))
            - len(bare.multiworld.get_unfilled_locations(bare.player)),
            len(full.pool.filler.locations))


class TestTheInstalledTable(unittest.TestCase):
    def test_an_empty_seed_writes_the_stub(self) -> None:
        rendered = FillerData().render()
        self.assertIn("extern const int FILLER_SEED_HIGH = -1;", rendered)
        self.assertIn("extern const int FILLER_SEED_LOW = -1;", rendered)
        self.assertNotIn("addFillerLocation(", rendered)

    def test_a_row_names_the_xs_constant_rather_than_its_value(self) -> None:
        rendered = FillerData([Age2FillerLocationData.KILL_25], "0000ABCD").render()
        self.assertIn("    addFillerLocation(6203, FILLER_KILL_UNITS, 25);", rendered)

    def test_each_collect_resource_gets_its_own_counter(self) -> None:
        rendered = FillerData(
            [Age2FillerLocationData.FOOD_50, Age2FillerLocationData.STONE_1000],
            "0000ABCD").render()
        self.assertIn("FILLER_COLLECT_FOOD", rendered)
        self.assertIn("FILLER_COLLECT_STONE", rendered)

    def test_rows_come_out_in_catalogue_order(self) -> None:
        chosen = [Age2FillerLocationData.STONE_50, Age2FillerLocationData.EXPLORE_5,
                  Age2FillerLocationData.KILL_10]
        rendered = FillerData(chosen, "0000ABCD").render()
        order = [rendered.index(f"addFillerLocation({filler.id},") for filler in
                 sorted(chosen, key=lambda filler: filler.id)]
        self.assertEqual(sorted(order), order)

    def test_a_non_milestone_is_refused(self) -> None:
        with self.assertRaises(ValueError):
            FillerData(["Kill 5 Units"], "0000ABCD").render()


@unittest.skipUnless(AGEIPELAGO_XS.is_dir(), "no local Ageipelago checkout")
class TestTheGameCanHoldThemAll(unittest.TestCase):

    def declared(self, name: str, source: str) -> int:
        found = re.search(r"^extern (?:const )?int %s = (\d+);" % name, source, re.M)
        self.assertIsNotNone(found, f"{name} not declared")
        return int(found.group(1))

    def test_the_worst_case_seed_fits_under_the_struct_cap(self) -> None:
        from test.general import setup_solo_multiworld
        from .. import Age2World
        cap = self.declared("MAX_INSTANCE_PER_STRUCT",
                            (AGEIPELAGO_XS / "structs.xs").read_text(encoding="utf-8"))
        filler_capacity = self.declared(
            "FILLER_CAPACITY", (AGEIPELAGO_XS / "AP_Constants.xs").read_text(encoding="utf-8"))
        self.assertGreaterEqual(filler_capacity, FILLER_LOCATION_COUNT,
                                "FILLER_CAPACITY cannot hold the catalogue")

        world = setup_solo_multiworld(Age2World, ()).worlds[1]
        world.options.enabled_campaigns.value = {"Joan of Arc", "Attila the Hun"}
        world.options.starting_campaigns.value = {"Joan of Arc"}
        for name, value in dict(techsanity=3, unitsanity=2, unitsanity_items=2, shuffle_ages=1,
                                shuffle_villager=2, include_unique_units=3,
                                minimum_filler_locations=FILLER_LOCATION_COUNT).items():
            getattr(world.options, name).value = value
        for step in ("generate_early", "create_regions"):
            getattr(world, step)()

        per_scenario = {}
        for location in world.multiworld.get_locations(world.player):
            if location.address and 10100 <= location.address <= 20604:
                per_scenario[location.address // 100] = per_scenario.get(
                    location.address // 100, 0) + 1
        registered = (len(world.pool.techs.shuffled)
                      + sum(len(places) for places in world.pool.units.line_locations.values())
                      + 35
                      + len(world.pool.ages.locations)
                      + max(per_scenario.values(), default=0)
                      + FILLER_LOCATION_COUNT)
        self.assertLessEqual(
            registered, cap,
            f"a worst-case seed registers {registered} Location structs against a cap of {cap}; "
            "raise MAX_INSTANCE_PER_STRUCT in structs.xs")


class TestTheSelectionAlgorithm(unittest.TestCase):

    JOAN, ATTILA = "Joan of Arc", "Attila the Hun"

    def build(self, campaigns, starting, **options):
        from test.general import setup_solo_multiworld
        from .. import Age2World
        world = setup_solo_multiworld(Age2World, (), 7).worlds[1]
        world.options.enabled_campaigns.value = set(campaigns)
        world.options.starting_campaigns.value = {starting}
        for name, value in options.items():
            getattr(world.options, name).value = value
        for step in ("generate_early", "create_regions", "create_items", "set_rules"):
            getattr(world, step)()
        return world

    def density(self, world):
        locations = [l for l in world.multiworld.get_locations(world.player)
                     if l.item is None]
        progression = sum(1 for i in world.multiworld.itempool
                          if i.player == world.player and i.advancement)
        return progression / len(locations)

    def test_a_default_seed_gets_no_milestones(self):
        for campaign in (self.ATTILA, self.JOAN):
            with self.subTest(campaign):
                world = self.build([campaign], campaign)
                self.assertEqual([], world.pool.filler.locations)

    def test_criterion_one_is_dormant_for_both_current_campaigns(self):
        for campaign in (self.ATTILA, self.JOAN):
            with self.subTest(campaign):
                world = self.build([campaign], campaign)
                self.assertEqual(0, world.pool.filler.early_shortfall())

    def test_criterion_one_fires_when_the_opening_scenario_is_bare(self):
        world = self.build([self.ATTILA], self.ATTILA)
        pool = world.pool.filler
        self.assertGreater(FillerPool.EARLY_FLOOR, 0)
        self.assertEqual(max(0, FillerPool.EARLY_FLOOR - pool.opening_locations),
                         pool.early_shortfall())

    def test_the_worst_density_cell_is_brought_under_target(self):
        world = self.build([self.JOAN], self.JOAN, techsanity=1, unitsanity=1)
        self.assertGreater(len(world.pool.filler.locations), 0)
        self.assertLessEqual(self.density(world), FillerPool.DENSITY_TARGET)

    def test_a_seed_already_under_target_pays_nothing(self):
        world = self.build([self.ATTILA], self.ATTILA, techsanity=1, unitsanity=1)
        self.assertLess(self.density(world), FillerPool.DENSITY_TARGET)
        self.assertEqual([], world.pool.filler.locations)

    def test_the_slider_still_raises_the_count(self):
        world = self.build([self.ATTILA], self.ATTILA, minimum_filler_locations=20)
        self.assertEqual(20, len(world.pool.filler.locations))


if __name__ == "__main__":
    unittest.main()
