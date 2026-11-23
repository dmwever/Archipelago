import pathlib
import tempfile
import unittest

from ..items.Items import CATEGORY_TO_ITEMS, Mercenary
from ..tools.write_mercenary_strings import (
    LANGUAGES,
    display_name,
    mercenary_name,
    render_strings_file,
    strings_file,
    write_strings_files,
)

FIRST_STRING_ID = 990001
LAST_STRING_ID = 990099

class TestMercenaryStrings(unittest.TestCase):

    def setUp(self) -> None:
        self.mercenaries = sorted(CATEGORY_TO_ITEMS[Mercenary], key=lambda item: item.id)

    def test_every_unit_has_a_display_name(self) -> None:
        for mercenary in self.mercenaries:
            for mercenary_unit in mercenary.type.units:
                self.assertTrue(display_name(mercenary_unit.unit), mercenary.item_name)

    def test_every_mercenary_has_a_short_name(self) -> None:
        for mercenary in self.mercenaries:
            self.assertTrue(mercenary_name(mercenary), mercenary.item_name)
            self.assertNotIn(":", mercenary_name(mercenary), mercenary.item_name)

    def test_string_ids_are_unique(self) -> None:
        ids = [mercenary.type.name_string_id for mercenary in self.mercenaries]
        self.assertEqual(len(set(ids)), len(ids), "two mercenaries share a name string")

    def test_string_ids_stay_in_the_band(self) -> None:
        for mercenary in self.mercenaries:
            self.assertIn(
                mercenary.type.name_string_id,
                range(FIRST_STRING_ID, LAST_STRING_ID + 1),
                mercenary.item_name,
            )

    def test_every_mercenary_renders_one_line(self) -> None:
        lines = render_strings_file().decode("utf-8").split("\r\n")
        self.assertEqual("", lines[-1])
        self.assertEqual(
            [mercenary.type.name_string_id for mercenary in self.mercenaries],
            [int(line.partition(" ")[0]) for line in lines[:-1]],
        )

    def test_dyrrhachiums_prisoners_reads_name_then_units(self) -> None:
        lines = render_strings_file().decode("utf-8").split("\r\n")
        self.assertIn('990003 "Dyrrhachium\'s Prisoners\\nTarkan ×5, Hussar ×2"', lines)

    def test_joans_lone_swordsman_is_named_for_its_champion(self) -> None:
        lines = render_strings_file().decode("utf-8").split("\r\n")
        self.assertIn('990011 "A Single Champion\\nChampion ×1"', lines)

    def test_roman_villagers_list_male_and_female_apart(self) -> None:
        lines = render_strings_file().decode("utf-8").split("\r\n")
        self.assertIn(
            '990002 "Roman Villagers\\nVillager (Male) ×7, Villager (Female) ×5"',
            lines,
        )

    def test_tool_writes_every_language_alike(self) -> None:
        with tempfile.TemporaryDirectory() as checkout:
            write_strings_files(pathlib.Path(checkout))
            written = [
                strings_file(pathlib.Path(checkout), language).read_bytes()
                for language in LANGUAGES
            ]
        self.assertEqual(17, len(LANGUAGES))
        self.assertEqual([render_strings_file()] * len(LANGUAGES), written)
        self.assertFalse(written[0].startswith(b"\xef\xbb\xbf"))
        self.assertEqual(len(self.mercenaries), written[0].count(b"\r\n"))
        self.assertEqual(written[0].count(b"\n"), written[0].count(b"\r\n"))

if __name__ == "__main__":
    unittest.main()
