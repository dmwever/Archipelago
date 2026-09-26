import unittest

from ..Options import Unitsanity, UnitsanityItems
from ..client.handlers.install.UnitData import UnitData
from ..locations.Civilizations import Age2CivData
from ..locations.UnitLines import Age2UnitLineData
from ..locations.Units import Age2UnitData
from ..locations.connections.CivilizationUnits import CIV_TO_UNITS

TAG = "a1b2c3d4"
FRANKS = (Age2CivData.FRANKS,)


def table(places, mode=Unitsanity.option_all,
          items=UnitsanityItems.option_unit_line, civs=FRANKS, tag=TAG):
    return UnitData(places, civs, mode, items, tag)


class TestWhichUnitsGetARow(unittest.TestCase):
    """Locking happens per genie id, so the table is not the list of checks."""

    def test_a_line_location_gives_every_tier_a_row(self):
        rows = table([Age2UnitLineData.MILITIA_LINE]).rows()
        self.assertEqual({row.unit for row in rows},
                         {unit for unit in Age2UnitLineData.MILITIA_LINE.units
                          if unit in CIV_TO_UNITS[Age2CivData.FRANKS]})
        # None of them is itself a check...
        self.assertTrue(all(not row.is_location for row in rows))
        # ...but every one completes the line's, because owning a Long Swordsman is owning the
        # Militia line. Without this the game sends nothing at all in unit_line mode.
        self.assertTrue(all(row.location_id == Age2UnitLineData.MILITIA_LINE.id
                            for row in rows))

    def test_a_unit_outside_any_line_location_completes_nothing(self):
        """A row exists so the unit can be locked; it just is not a check."""
        rows = table([Age2UnitData.MILITIA]).rows()
        militia = next(row for row in rows if row.unit is Age2UnitData.MILITIA)
        self.assertEqual(militia.location_id, Age2UnitData.MILITIA.id)
        self.assertFalse(militia.line_is_location)

    def test_a_unit_location_is_a_check(self):
        rows = table([Age2UnitData.MILITIA]).rows()
        self.assertEqual(len(rows), 1)
        self.assertTrue(rows[0].is_location)
        self.assertEqual(rows[0].location_id, Age2UnitData.MILITIA.id)

    def test_a_tier_the_civilisation_lacks_gets_no_row(self):
        """The Huns have no Champion, so their Militia line stops at Two-Handed."""
        units = {row.unit for row in
                 table([Age2UnitLineData.MILITIA_LINE], civs=(Age2CivData.HUNS,)).rows()}
        self.assertNotIn(Age2UnitData.CHAMPION, units)
        self.assertIn(Age2UnitData.TWO_HANDED_SWORDSMAN, units)

    def test_a_location_no_civilisation_can_field_is_refused(self):
        """Loudly, rather than emitting a row the game can never use."""
        with self.assertRaises(ValueError):
            table([Age2UnitData.LONGBOWMAN], civs=(Age2CivData.HUNS,)).rows()


class TestTheItemRequirementIsResolvedHere(unittest.TestCase):
    """Whichever mode produced them, XS sees only a list of item ids - it never branches on
    unitsanity_items, because the installer has already decided."""

    def test_line_mode_gives_the_line_item(self):
        rows = table([Age2UnitData.MAN_AT_ARMS],
                     items=UnitsanityItems.option_unit_line).rows()
        self.assertEqual(rows[0].items, (Age2UnitData.MAN_AT_ARMS.line.item.id,))

    def test_upgrades_mode_gives_the_tokens(self):
        rows = table([Age2UnitData.MAN_AT_ARMS],
                     items=UnitsanityItems.option_upgrades).rows()
        self.assertEqual(set(rows[0].items),
                         {token.id for token in Age2UnitData.MAN_AT_ARMS.upgrade_tokens})
        self.assertGreater(len(rows[0].items), 1)

    def test_buildings_mode_gives_the_building_item(self):
        rows = table([Age2UnitData.MAN_AT_ARMS],
                     items=UnitsanityItems.option_buildings).rows()
        self.assertEqual(len(rows[0].items), 1)

    def test_unitsanity_off_needs_no_items(self):
        rows = table([Age2UnitData.MAN_AT_ARMS], mode=Unitsanity.option_none).rows()
        self.assertEqual(rows[0].items, ())

    def test_no_unit_carries_more_items_than_xs_expects(self):
        data = table([], items=UnitsanityItems.option_upgrades, civs=tuple(Age2CivData))
        for civ in Age2CivData:
            for unit in CIV_TO_UNITS[civ]:
                with self.subTest(unit=unit.unit_name):
                    self.assertLessEqual(len(data.items_for(unit)), UnitData.MAX_ITEMS)


class TestRender(unittest.TestCase):

    def test_a_seedless_table_is_the_stub(self):
        """What ships in the repo, and what an install with unitsanity off writes."""
        expected = "\n".join(["extern const int US_SEED_HIGH = -1;",
                              "extern const int US_SEED_LOW = -1;",
                              "",
                              "void LoadUnitTable() {",
                              "    return;",
                              "}"]) + "\n"
        self.assertEqual(UnitData().render(), expected)

    def test_the_seed_tag_is_rendered(self):
        """A table from another seed must be refusable, which is what the tag is for."""
        rendered = table([Age2UnitData.MILITIA]).render()
        self.assertNotIn("US_SEED_HIGH = -1", rendered)
        self.assertIn("addUnit(", rendered)

    def test_variants_are_emitted(self):
        """A Sicilian Spearman is a different genie id at the Donjon, and the game has to know
        both or it counts only half of them."""
        rendered = table([Age2UnitData.SPEARMAN]).render()
        for variant in Age2UnitData.SPEARMAN.variant_game_ids:
            self.assertIn(f"addUnitVariant({Age2UnitData.SPEARMAN.game_id}, {variant});",
                          rendered)

    def test_every_row_is_one_addUnit_call(self):
        data = table([Age2UnitLineData.MILITIA_LINE, Age2UnitLineData.KNIGHT_LINE])
        self.assertEqual(data.render().count("    addUnit("), len(data.rows()))
