import unittest

from ..generation import Identity, SlotData, TechData
from ..items.Items import CATEGORY_TO_ITEMS, Age, Age2ItemData, Tech
from ..locations.Civilizations import Age2CivData

# Genie civilization ids, the space Tech.civ is in.
HUNS = Age2CivData.HUNS.game_id
FRANKS = Age2CivData.FRANKS.game_id

SEED_CIVS = {HUNS, FRANKS}
RESEARCHABLE = [item for item in CATEGORY_TO_ITEMS[Tech]
                if item.type.civ in (TechData.ANY_CIV, HUNS, FRANKS)]
UPGRADES = [item.id for item in RESEARCHABLE if item.type.is_upgrade]
GENERIC = [item.id for item in CATEGORY_TO_ITEMS[Tech] if item.type.civ == TechData.ANY_CIV]


def row_for(table, item_id):
    return next(row for row in table if row.item_id == item_id)


class TestTechCatalogue(unittest.TestCase):
    def test_every_tech_item_is_in_the_band(self):
        for item in CATEGORY_TO_ITEMS[Tech]:
            self.assertGreaterEqual(item.id, TechData.TECH_ITEM_OFFSET, item.item_name)
            offset = item.id - TechData.TECH_ITEM_OFFSET
            self.assertLess(offset, TechData.TECH_CAPACITY, item.item_name)

    def test_every_tech_carries_an_age_xs_understands(self):
        for item in CATEGORY_TO_ITEMS[Tech]:
            self.assertIn(item.type.age.value, range(len(Age)), item.item_name)

    def test_the_catalogue_fits_the_xs_capacity(self):
        self.assertLessEqual(len(CATEGORY_TO_ITEMS[Tech]), TechData.TECH_CAPACITY)


class TestRowSelection(unittest.TestCase):
    def test_locations_only_when_nothing_was_rebased(self):
        table = TechData.rows([3600, 3649], civ_ids=SEED_CIVS)
        self.assertEqual([row.item_id for row in table], [3600, 3649])
        self.assertTrue(all(row.is_location for row in table))

    def test_grant_only_rows_sit_below_the_grant_age(self):
        table = TechData.rows([], grant_age=Age.CASTLE, civ_ids=SEED_CIVS)
        self.assertTrue(table)
        for row in table:
            self.assertEqual(row.item_id, TechData.NO_ITEM)
            self.assertFalse(row.is_location)
            self.assertLess(row.tech.age.value,
                            Age.CASTLE.value)

    def test_grant_only_rows_skip_other_civs_uniques(self):
        table = TechData.rows([], grant_age=Age.IMPERIAL, civ_ids={FRANKS})
        for row in table:
            self.assertIn(row.tech.civ, (TechData.ANY_CIV, FRANKS))

    def test_a_location_is_never_also_a_grant_only_row(self):
        table = TechData.rows(UPGRADES, grant_age=Age.IMPERIAL, civ_ids=SEED_CIVS)
        ids = [row.item_id for row in table if row.is_location]
        self.assertEqual(sorted(ids), sorted(UPGRADES))
        self.assertEqual(len(ids), len(set(ids)))

    def test_units_and_lock_technologies_matches_the_measured_shape(self):
        table = TechData.rows(UPGRADES, grant_age=Age.IMPERIAL, civ_ids=SEED_CIVS)
        locations = [row for row in table if row.is_location]
        grant_only = [row for row in table if not row.is_location]
        self.assertEqual(len(locations), 43)
        self.assertEqual(len(grant_only), 52)

    def test_a_location_no_civilization_can_research_is_refused(self):
        plumed = Age2ItemData.TECH_ELITE_PLUMED_ARCHER_MAYANS
        with self.assertRaises(ValueError):
            TechData.rows([plumed.id], civ_ids=SEED_CIVS)

    def test_an_unknown_item_id_is_refused(self):
        with self.assertRaises(ValueError):
            TechData.rows([3600, 999999], civ_ids=SEED_CIVS)

    def test_rows_are_ordered_by_item_id(self):
        table = TechData.rows(GENERIC, civ_ids=SEED_CIVS)
        self.assertEqual([row.item_id for row in table],
                         sorted(row.item_id for row in table))


class TestRender(unittest.TestCase):
    def test_an_empty_table_still_defines_the_function(self):
        self.assertTrue(TechData.render().endswith("void LoadTechTable() {\n}\n"))

    def test_a_location_row_carries_every_addtech_argument(self):
        tarkan = Age2ItemData.TECH_ELITE_TARKAN_HUNS
        rendered = TechData.render(TechData.rows([tarkan.id], civ_ids=SEED_CIVS))
        tech: Tech = tarkan.type
        self.assertIn(
            f"    addTech({tarkan.id}, {tech.game_id}, {tech.effect_id}, {tech.civ}, "
            f"1, 1, {tech.age.value}, 1);", rendered)

    def test_a_grant_only_row_has_no_item_and_is_not_a_location(self):
        table = TechData.rows([], grant_age=Age.FEUDAL, civ_ids={FRANKS})
        rendered = TechData.render(table).splitlines()
        body = [line for line in rendered if line.startswith("    addTech(")]
        self.assertTrue(body)
        for line in body:
            self.assertTrue(line.startswith("    addTech(-1, "), line)
            self.assertTrue(line.endswith(", 0);"), line)

    def test_booleans_render_as_xs_ints(self):
        rendered = TechData.render(TechData.rows(GENERIC, civ_ids=SEED_CIVS))
        self.assertNotIn("True", rendered)
        self.assertNotIn("False", rendered)


SEED = "0123456789abcdef"


class TestSeedGuard(unittest.TestCase):
    def test_an_uninstalled_table_matches_an_uninstalled_slot_data(self):
        rendered = TechData.render()
        self.assertIn(f"extern const int {TechData.SEED_HIGH} = {SlotData.UNSET};", rendered)
        self.assertIn(f"extern const int {TechData.SEED_LOW} = {SlotData.UNSET};", rendered)

    def test_the_guard_matches_the_slot_data_halves(self):
        tag = Identity.seed_tag(SEED, 3)
        high, low = SlotData.seed_halves(tag)
        rendered = TechData.render((), tag)
        self.assertIn(f"extern const int {TechData.SEED_HIGH} = {high};", rendered)
        self.assertIn(f"extern const int {TechData.SEED_LOW} = {low};", rendered)
        slot_data = SlotData.render(SlotData.fields(3, tag))
        self.assertIn(f"extern const int {SlotData.SEED_HIGH} = {high};", slot_data)
        self.assertIn(f"extern const int {SlotData.SEED_LOW} = {low};", slot_data)

    def test_a_different_seed_gives_a_different_guard(self):
        one = TechData.render((), Identity.seed_tag(SEED, 3))
        two = TechData.render((), Identity.seed_tag(SEED, 4))
        self.assertNotEqual(one, two)

    def test_the_guard_precedes_the_table(self):
        rendered = TechData.render(TechData.rows([3600], civ_ids=SEED_CIVS), Identity.seed_tag(SEED, 3))
        self.assertLess(rendered.index(TechData.SEED_HIGH), rendered.index("LoadTechTable"))


class TestCivIds(unittest.TestCase):
    def test_game_ids_match_the_unique_techs_that_name_the_civ(self):
        for civ in Age2CivData:
            named = {item.type.civ for item in CATEGORY_TO_ITEMS[Tech]
                     if item.type.is_unique
                     and item.item_name.endswith(f"({civ.campaign_name})")}
            self.assertEqual(named, {civ.game_id}, civ.campaign_name)

    def test_the_world_id_is_not_the_game_id(self):
        # Age2CivData numbers the civs this world ships; Tech.civ is in genie's
        # space, where 1 is Britons. Passing one for the other is silent.
        self.assertNotEqual(Age2CivData.FRANKS.value, Age2CivData.FRANKS.game_id)
