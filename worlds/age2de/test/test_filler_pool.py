"""Milestone locations: the catalogue, the id band, and the budget they have to fit in.

Nothing selects a milestone yet - FillerPool is deliberately empty until the rules that make them
reachable exist - so these pin the things that have to be right before anything is switched on.
A milestone whose id lands in another family's band, or that pushes the game past a struct cap it
fails silently at, is a bug nobody sees until a seed is already being played.
"""
import os
import pathlib
import re
import unittest

from ..Options import MinimumFillerLocations
from ..client.handlers.install.FillerData import FillerData
from ..locations.FillerLocations import (
    Age2FillerLocationData, FillerKind, FillerTier, FILLER_LOCATION_COUNT, KIND_TO_LOCATIONS)
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
        """Every one of them, without exception. The prefix is added by __init__ rather than
        typed into each member, so a new milestone cannot be declared without it."""
        for filler in Age2FillerLocationData:
            with self.subTest(filler.location_name):
                self.assertTrue(filler.location_name.startswith("Milestone: "))

    def test_the_only_character_the_game_rewrites_is_the_percent_sign(self) -> None:
        """MessageHandler._parse_evil_characters rewrites what would break xsChatData, which
        takes its argument as a printf format. The percent signs in the explore names are a
        deliberate exception - in game they read "10 percent" where the spoiler log reads "10%".
        Nothing else may differ, so a name picking up an accented character fails here.
        """
        from ..client.handlers.MessageHandler import _parse_evil_characters
        for filler in Age2FillerLocationData:
            with self.subTest(filler.location_name):
                self.assertEqual(
                    _parse_evil_characters(filler.location_name.replace("%", "")),
                    filler.location_name.replace("%", ""))

    def test_the_option_ceiling_is_the_whole_catalogue(self) -> None:
        """range_end is a class attribute and cannot import the catalogue, so it is a literal.
        This is what stops the two drifting."""
        self.assertEqual(FILLER_LOCATION_COUNT, MinimumFillerLocations.range_end)

    def test_a_collect_milestone_names_its_resource_and_no_other_kind_does(self) -> None:
        for filler in Age2FillerLocationData:
            with self.subTest(filler.location_name):
                if filler.kind is FillerKind.COLLECT:
                    self.assertIsNotNone(filler.resource)
                else:
                    self.assertIsNone(filler.resource)

    def test_thresholds_rise_within_a_kind(self) -> None:
        """Declaration order is install order and selection order, so a ladder out of sequence
        would make a harder milestone look like the easier one."""
        for kind, members in KIND_TO_LOCATIONS.items():
            if kind is FillerKind.COLLECT:
                continue  # four interleaved ladders, one per resource
            with self.subTest(kind.name):
                thresholds = [member.threshold for member in members]
                self.assertEqual(sorted(thresholds), thresholds)

    def test_a_harder_milestone_is_never_an_easier_tier(self) -> None:
        order = {FillerTier.FREE: 0, FillerTier.EARLY: 1, FillerTier.REGULAR: 2}
        for kind, members in KIND_TO_LOCATIONS.items():
            for earlier, later in zip(members, members[1:]):
                if earlier.resource is not later.resource:
                    continue
                with self.subTest(f"{earlier.location_name} -> {later.location_name}"):
                    self.assertLessEqual(order[earlier.tier], order[later.tier])


class TestTheIdBand(unittest.TestCase):
    """6000-7199, which has to clear three separate things."""

    def test_ids_are_acked_globally(self) -> None:
        """AP.xs sends a location to every scenario when id // 100 is below MIN_SCENARIO_ID
        (101). A milestone earned in one scenario has to stay earned, so all of them must be
        under 10100 - otherwise the game reads the id as belonging to some scenario."""
        for filler in Age2FillerLocationData:
            with self.subTest(filler.location_name):
                self.assertLess(filler.id // 100, 101)

    def test_no_id_is_read_as_a_unit(self) -> None:
        """InstallHandler maps every received id through unit_location. An id inside the unit
        bands would install a milestone as a unit."""
        for filler in Age2FillerLocationData:
            with self.subTest(filler.location_name):
                self.assertIsNone(unit_location(filler.id))

    def test_no_name_or_id_collides_with_another_family(self) -> None:
        names = {filler.location_name for filler in Age2FillerLocationData}
        ids = {filler.id for filler in Age2FillerLocationData}
        others = {name: id for name, id in location_name_to_id.items() if name not in names}
        self.assertEqual(set(), ids & set(others.values()))
        self.assertEqual(len(location_name_to_id), len(set(location_name_to_id)))


class TestNothingIsSelectedYet(Age2TestBase):
    options = {"minimum_filler_locations": MinimumFillerLocations.range_end}

    def test_the_pool_is_empty(self) -> None:
        """The floor is not honoured yet, on purpose: a milestone with no rule is a location the
        fill treats as free and the player may have no way to earn."""
        self.assertEqual([], self.world.pool.filler.locations)

    def test_the_player_minimum_is_read(self) -> None:
        self.assertEqual(MinimumFillerLocations.range_end, self.world.pool.filler.minimum)

    def test_no_milestone_is_a_location(self) -> None:
        placed = {location.name for location in self.multiworld.get_locations(self.player)}
        catalogue = {filler.location_name for filler in Age2FillerLocationData}
        self.assertEqual(set(), placed & catalogue)


class TestTheEconomyDoesNotMove(unittest.TestCase):
    """Milestone slots are held back from ResourcePool on purpose.

    HasResourceAmount reads pool.resources.totals, so funding starting resources out of milestone
    locations would change which scenarios are reachable - adding locations would quietly make the
    campaigns easier. Vacuous while the pool is empty; it is here to fail the moment that changes.
    """

    SEED = 20260406

    def totals(self, minimum: int) -> dict:
        from test.general import setup_solo_multiworld
        from .. import Age2World
        # The same seed both times: ResourcePool picks its items with world.random, so two
        # unseeded worlds differ by the draw rather than by the option under test.
        world = setup_solo_multiworld(Age2World, (), self.SEED).worlds[1]
        world.options.minimum_filler_locations.value = minimum
        for step in ("generate_early", "create_regions", "create_items"):
            getattr(world, step)()
        return dict(world.pool.resources.totals)

    def test_the_slider_does_not_change_starting_resources(self) -> None:
        self.assertEqual(self.totals(0), self.totals(MinimumFillerLocations.range_end))


class TestTheInstalledTable(unittest.TestCase):
    def test_an_empty_seed_writes_the_stub(self) -> None:
        """InitFiller reads two unset halves as "no milestones here" and stays quiet. Anything
        else would put a red line on screen in every scenario of every seed at slider 0."""
        rendered = FillerData().render()
        self.assertIn("extern const int FILLER_SEED_HIGH = -1;", rendered)
        self.assertIn("extern const int FILLER_SEED_LOW = -1;", rendered)
        self.assertNotIn("addFiller(", rendered)

    def test_a_row_names_the_xs_constant_rather_than_its_value(self) -> None:
        """So a kind the mod has not learned yet fails to compile instead of never firing."""
        rendered = FillerData([Age2FillerLocationData.KILL_25], "0000ABCD").render()
        self.assertIn("    addFiller(6202, FILLER_KILL_UNITS, 25);", rendered)

    def test_each_collect_resource_gets_its_own_counter(self) -> None:
        rendered = FillerData(
            [Age2FillerLocationData.FOOD_50, Age2FillerLocationData.STONE_1000],
            "0000ABCD").render()
        self.assertIn("FILLER_COLLECT_FOOD", rendered)
        self.assertIn("FILLER_COLLECT_STONE", rendered)

    def test_rows_come_out_in_catalogue_order(self) -> None:
        """So reinstalling the same seed produces the same file."""
        chosen = [Age2FillerLocationData.STONE_50, Age2FillerLocationData.EXPLORE_5,
                  Age2FillerLocationData.KILL_10]
        rendered = FillerData(chosen, "0000ABCD").render()
        order = [rendered.index(f"addFiller({filler.id},") for filler in
                 sorted(chosen, key=lambda filler: filler.id)]
        self.assertEqual(sorted(order), order)

    def test_a_non_milestone_is_refused(self) -> None:
        with self.assertRaises(ValueError):
            FillerData(["Kill 5 Units"], "0000ABCD").render()


@unittest.skipUnless(AGEIPELAGO_XS.is_dir(), "no local Ageipelago checkout")
class TestTheGameCanHoldThemAll(unittest.TestCase):
    """AddLocation takes a Location struct instance per location, and the struct library caps
    instances per type. Past the cap new() hands back cInvalidVector and the location is dropped
    with one red chat line - so the seed generates, installs, and is simply unwinnable."""

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

        # Everything one scenario registers. Techs, units, buildsanity and ages are global, so
        # each scenario puts up all of them; scenario objectives are only its own.
        per_scenario = {}
        for location in world.multiworld.get_locations(world.player):
            if location.address and 10100 <= location.address <= 20604:
                per_scenario[location.address // 100] = per_scenario.get(
                    location.address // 100, 0) + 1
        registered = (len(world.pool.techs.shuffled)
                      + sum(len(places) for places in world.pool.units.line_locations.values())
                      + 35                                   # buildsanity, always all of them
                      + len(world.pool.ages.locations)
                      + max(per_scenario.values(), default=0)
                      + FILLER_LOCATION_COUNT)               # the ceiling, not today's selection
        self.assertLessEqual(
            registered, cap,
            f"a worst-case seed registers {registered} Location structs against a cap of {cap}; "
            "raise MAX_INSTANCE_PER_STRUCT in structs.xs")


if __name__ == "__main__":
    unittest.main()
