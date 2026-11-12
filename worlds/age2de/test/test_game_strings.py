import unittest

from ..locations.Buildings import Age2BuildingData
from ..locations.EscortUnits import Age2EscortUnitData
from ..locations.Heroes import Age2HeroData
from ..locations.Techs import Age2TechData
from ..locations.Units import Age2UnitData
from ..locations.VillagerJobs import Age2VillagerJobData
from ..locations.connections.GameStrings import (
    BUILDING_NAME_STRINGS,
    ESCORT_NAME_STRINGS,
    EXTENDED_TOOLTIP_OFFSET,
    GAME_STRING_SOURCE,
    HERO_NAME_STRINGS,
    NAME_STRINGS_BY_KIND,
    TECH_NAME_STRINGS,
    UNIT_NAME_STRINGS,
    VILLAGER_JOB_NAME_STRINGS,
    extended_tooltip_id,
)

CATALOGUES = (
    (Age2TechData, TECH_NAME_STRINGS),
    (Age2UnitData, UNIT_NAME_STRINGS),
    (Age2VillagerJobData, VILLAGER_JOB_NAME_STRINGS),
    (Age2HeroData, HERO_NAME_STRINGS),
    (Age2EscortUnitData, ESCORT_NAME_STRINGS),
    (Age2BuildingData, BUILDING_NAME_STRINGS),
)


class TestTheDumpIsComplete(unittest.TestCase):
    def test_no_name_string_belongs_to_something_the_catalogue_dropped(self):
        for kind, names in CATALOGUES:
            for place in names:
                with self.subTest(f"{kind.__name__}.{place.name}"):
                    self.assertIsInstance(place, kind)

    def test_every_name_string_is_a_positive_id(self):
        for _, names in CATALOGUES:
            for place, name_string in names.items():
                with self.subTest(place.name):
                    self.assertIsInstance(name_string, int)
                    self.assertGreater(name_string, 0)

    def test_every_kind_is_reachable_by_its_type(self):
        for kind, names in CATALOGUES:
            self.assertIs(NAME_STRINGS_BY_KIND[kind], names, kind.__name__)


class TestProvenance(unittest.TestCase):
    def test_the_source_names_the_dat_it_was_read_from(self):
        self.assertIn(".dat", GAME_STRING_SOURCE)
        self.assertIn("aoe2kit", GAME_STRING_SOURCE)


class TestTheExtendedTooltipId(unittest.TestCase):
    def test_a_technology_reads_its_measured_tooltip(self):
        self.assertEqual(extended_tooltip_id(Age2TechData.LOOM), 28022)

    def test_a_unit_reads_its_measured_tooltip(self):
        self.assertEqual(extended_tooltip_id(Age2UnitData.ARCHER), 26083)

    def test_a_building_reads_its_measured_tooltip(self):
        self.assertEqual(extended_tooltip_id(Age2BuildingData.HOUSE), 26344)

    def test_a_late_technology_outside_the_vanilla_band_reads_its_measured_tooltip(self):
        self.assertEqual(
            extended_tooltip_id(Age2TechData.ORDONNANCE_COMPANIES_FRANKS), 528025)

    def test_a_late_unit_outside_the_vanilla_band_reads_its_measured_tooltip(self):
        self.assertEqual(extended_tooltip_id(Age2UnitData.HOPLITE), 426007)

    def test_the_offset_is_what_separates_a_name_from_its_tooltip(self):
        for kind, names in CATALOGUES:
            for place, name_string in names.items():
                with self.subTest(f"{kind.__name__}.{place.name}"):
                    self.assertEqual(extended_tooltip_id(place),
                                     name_string + EXTENDED_TOOLTIP_OFFSET)

    def test_something_outside_the_catalogue_raises_rather_than_reading_as_a_number(self):
        with self.assertRaises(KeyError):
            extended_tooltip_id(Age2TechData.LOOM.value)
