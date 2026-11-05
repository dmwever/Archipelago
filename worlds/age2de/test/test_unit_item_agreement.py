import itertools
import tempfile
from pathlib import Path

from test.general import setup_solo_multiworld

from .. import Age2World
from ..Options import (IncludeUniqueUnits, ShuffleVillager, Techsanity, Unitsanity,
                       UnitsanityItems)
from ..client.handlers.InstallHandler import InstallHandler
from ..client.handlers.install.UnitData import UnitData
from ..generation import SlotData
from ..locations.UnitLocations import unit_location
from ..items.Items import Age2ItemData
from ..locations.Campaigns import NAME_TO_CAMPAIGN
from ..locations.UnitLines import Age2UnitLineData
from ..locations.Units import Age2UnitData
from ..locations.connections.CivilizationUnits import CIV_TO_UNITS
from ..locations.connections.LocationMapping import location_name_to_id
from .test_installer import fake_user_folder
from .test_unit_pool import UnitPoolTestBase

MODES = [Unitsanity.option_none, Unitsanity.option_unit_line, Unitsanity.option_all]
ITEM_MODES = [UnitsanityItems.option_unit_line, UnitsanityItems.option_upgrades,
              UnitsanityItems.option_buildings]
VILLAGER = [ShuffleVillager.option_no, ShuffleVillager.option_yes,
            ShuffleVillager.option_include_professions]
UNIQUES = [IncludeUniqueUnits.option_none, IncludeUniqueUnits.option_unique,
           IncludeUniqueUnits.option_regional, IncludeUniqueUnits.option_both]


class UnitTableAgreementBase(UnitPoolTestBase):
    def installed(self, world) -> dict[str, int]:
        return SlotData.options(world.fill_slot_data())

    def places(self, world) -> list:
        ids = [location_name_to_id[location.name]
               for location in world.multiworld.get_locations(1)
               if location.name in location_name_to_id]
        return [place for place in map(unit_location, ids) if place is not None]

    def table_for(self, world) -> UnitData:
        installed = self.installed(world)
        return UnitData(
            self.places(world),
            world.pool.civs.included,
            installed[SlotData.US_MODE],
            installed[SlotData.US_ITEMS],
            "a1b2c3d4",
            caveman=bool(installed[SlotData.US_CAVEMAN]),
            techs=world.pool.techs.shuffled,
        )

    def place_name(self, place) -> str:
        for attribute in ("unit_name", "job_name", "hero_name", "escort_name", "line_name"):
            name = getattr(place, attribute, None)
            if name:
                return name
        return place.name

    def granted_names(self, world) -> set[str]:
        names = {item.name for item in world.multiworld.itempool}
        return names | {item.name for item in world.multiworld.precollected_items[1]}

    def every_combination(self):
        for mode, items, villager in itertools.product(MODES, ITEM_MODES, VILLAGER):
            with self.subTest(unitsanity=mode, items=items, villager=villager):
                yield self.build(unitsanity=mode, unitsanity_items=items,
                                 shuffle_villager=villager)

    def every_unique_unit_setting(self):
        for uniques, items in itertools.product(UNIQUES, ITEM_MODES):
            with self.subTest(uniques=uniques, items=items):
                yield self.build(unitsanity=Unitsanity.option_all,
                                 unitsanity_items=items,
                                 include_unique_units=uniques)


class TestTheGameWaitsForItemsTheSeedContains(UnitTableAgreementBase):
    def test_every_gating_item_is_one_the_seed_hands_out(self):
        for world in self.every_combination():
            granted = self.granted_names(world)
            for row in self.table_for(world).rows():
                for item_id in row.items:
                    self.assertIn(
                        Age2ItemData(item_id).item_name, granted,
                        f"{self.place_name(row.unit)} waits for an item the seed "
                        "never contains")

    def test_no_trainable_unit_is_gated_by_nothing(self):
        """A unit no civilisation in the seed trains is the exception: only a scenario hands
        one over, and like a hero it is owned when granted."""
        for world in self.every_combination():
            trainable = {unit for civ in world.pool.civs.included for unit in CIV_TO_UNITS[civ]}
            ungated = [row.unit.unit_name for row in self.table_for(world).rows()
                       if not row.items and isinstance(row.unit, Age2UnitData)
                       and row.unit in trainable]
            self.assertEqual(ungated, [])

    def test_every_option_combination_installs(self):
        for world in self.every_combination():
            self.table_for(world).rows()


class TestVillagersCanBeShuffledAlone(UnitTableAgreementBase):
    def setUp(self):
        self.villager_world = self.build(unitsanity=Unitsanity.option_none,
                                         shuffle_villager=ShuffleVillager.option_yes)

    def test_the_location_is_placed(self):
        self.assertIn("Own Villager (Male) Line",
                      [location.name
                       for location in self.villager_world.multiworld.get_locations(1)])

    def test_the_game_is_told_unitsanity_is_on(self):
        self.assertNotEqual(self.installed(self.villager_world)[SlotData.US_MODE],
                            Unitsanity.option_none)

    def test_what_was_asked_for_still_reaches_the_game(self):
        self.assertEqual(self.installed(self.villager_world)[SlotData.US_VILLAGER],
                         ShuffleVillager.option_yes)

    def test_a_row_completes_that_check(self):
        rows = self.table_for(self.villager_world).rows()
        self.assertTrue(any(row.location_id == Age2UnitLineData.VILLAGER_MALE_LINE.id
                            for row in rows))


class TestUnitsanityStaysOffWhenNothingIsShuffled(UnitTableAgreementBase):
    def test_the_seedless_defaults_report_none(self):
        self.assertEqual(SlotData.options()[SlotData.US_MODE], Unitsanity.option_none)

    def test_villager_off_reports_none(self):
        world = self.build(unitsanity=Unitsanity.option_none,
                           shuffle_villager=ShuffleVillager.option_no)
        self.assertEqual(self.installed(world)[SlotData.US_MODE], Unitsanity.option_none)


class TestTheVillagerIsGatedByItsLine(UnitPoolTestBase):
    def test_its_line_item_gates_it_in_every_item_mode(self):
        from ..locations.Civilizations import Age2CivData
        for items in ITEM_MODES:
            with self.subTest(items=items):
                table = UnitData([Age2UnitLineData.VILLAGER_MALE_LINE],
                                 (Age2CivData.HUNS, Age2CivData.FRANKS),
                                 Unitsanity.option_all, items, "a1b2c3d4")
                self.assertEqual(table.items_for(Age2UnitData.VILLAGER_MALE),
                                 (Age2UnitLineData.VILLAGER_MALE_LINE.item.id,))
class TestUniqueUnitsInstall(UnitTableAgreementBase):
    def test_every_unique_unit_setting_installs(self):
        for world in self.every_unique_unit_setting():
            self.table_for(world).render()

    def test_a_granted_only_line_still_gets_a_row(self):
        for world in self.every_unique_unit_setting():
            if world.options.include_unique_units == IncludeUniqueUnits.option_none:
                continue
            if "Own Mangudai" not in {location.name
                                      for location in world.multiworld.get_locations(1)}:
                continue
            emitted = {row.unit for row in self.table_for(world).rows()}
            self.assertIn(Age2UnitData.MANGUDAI, emitted,
                          "a unit only a grant can supply is placed but never reaches the game")

class TestTheInstalledUpgradeItemIsInTheSeed(UnitTableAgreementBase):
    def build_three_campaigns(self, techsanity: int) -> Age2World:
        world = setup_solo_multiworld(Age2World, ()).worlds[1]
        world.options.enabled_campaigns.value = {
            "Attila the Hun",
            "Joan of Arc",
            "Genghis Khan",
        }
        world.options.starting_campaigns.value = {"Attila the Hun"}
        world.options.caveman.value = 1
        world.options.unitsanity.value = Unitsanity.option_all
        world.options.techsanity.value = techsanity
        world.generate_early()
        world.create_regions()
        world.create_items()
        return world

    def installed_upgrade_items(self, world: Age2World) -> list[tuple[int, int]]:
        with tempfile.TemporaryDirectory() as folder:
            handler = InstallHandler()
            handler.set_user_folder(str(fake_user_folder(Path(folder))))
            campaigns = [
                NAME_TO_CAMPAIGN[name]
                for name in world.options.enabled_campaigns.value
            ]
            location_ids = [
                location.address for location in world.multiworld.get_locations(1)
                    if location.address is not None
            ]
            handler.setup(campaigns, 1, "a1b2c3d4", "Player", world.fill_slot_data(), location_ids)
            rendered = handler._write_unit_data().read_text(encoding="utf-8")
        rows: list[tuple[int, int]] = []
        for line in rendered.splitlines():
            if not line.startswith("    addUnit("):
                continue
            arguments = line.removeprefix("    addUnit(").removesuffix(");").split(", ")
            self.assertEqual(len(arguments), 7, line)
            rows.append((int(arguments[1]), int(arguments[5])))
        return rows

    def expected_upgrade_item(self, world: Age2World, game_id: int) -> int:
        units = {unit.game_id: unit for unit in Age2UnitData}
        if game_id not in units:
            return UnitData.NO_UPGRADE_ITEM
        tech = units[game_id].upgrade_tech
        if tech is None or tech.item is None or not world.pool.techs.includes(tech):
            return UnitData.NO_UPGRADE_ITEM
        return tech.item.id

    def test_a_unit_waits_for_exactly_the_upgrade_item_logic_waits_for(self):
        for techsanity in (
            Techsanity.option_generic,
            Techsanity.option_units,
            Techsanity.option_all,
        ):
            with self.subTest(techsanity=techsanity):
                world = self.build_three_campaigns(techsanity)
                rows = self.installed_upgrade_items(world)
                wrong = [
                    (game_id, item_id, self.expected_upgrade_item(world, game_id))
                    for game_id, item_id in rows
                        if item_id != self.expected_upgrade_item(world, game_id)
                ]
                self.assertEqual(wrong, [])
                gated = [item_id for _, item_id in rows if item_id != UnitData.NO_UPGRADE_ITEM]
                if techsanity == Techsanity.option_generic:
                    self.assertEqual(gated, [])
                else:
                    self.assertNotEqual(gated, [])
