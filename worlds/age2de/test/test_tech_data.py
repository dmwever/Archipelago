import unittest

from ..client.handlers.install import TechData
from ..generation import Identity, SlotData
from ..items.Items import CATEGORY_TO_ITEMS, Age2ItemData, Tech
from ..locations.Ages import Age2AgeData
from ..locations.Civilizations import Age2CivData
from ..locations.Techs import Age2TechData, TechOption, researchable

# Genie civilization ids, the space Tech.civ is in.
HUNS = Age2CivData.HUNS.game_id
FRANKS = Age2CivData.FRANKS.game_id

SEED_CIVS = tuple(Age2CivData)
RESEARCHABLE = researchable(SEED_CIVS)
UPGRADES = [tech for tech in RESEARCHABLE if tech.item.type.is_upgrade]
GENERIC = [tech for tech in RESEARCHABLE if not tech.item.type.is_upgrade]


def row_for(table, item_id):
    return next(row for row in table if row.item_id == item_id)


class TestTechCatalogue(unittest.TestCase):
    def test_a_location_and_its_item_share_an_id(self):
        # rows() hands XS an item id for a location it was given; the two spaces
        # are only interchangeable while every pair is written with one number.
        for tech in Age2TechData:
            self.assertEqual(tech.id, tech.item.id, tech.name)

    def test_a_location_and_its_item_agree_on_the_age(self):
        for tech in Age2TechData:
            self.assertIs(tech.age, tech.item.type.age, tech.name)

    def test_every_tech_carries_an_age_xs_understands(self):
        for tech in Age2TechData:
            self.assertIn(tech.age, Age2AgeData, tech.name)

    def test_the_catalogue_fits_the_xs_capacity(self):
        self.assertLessEqual(len(Age2TechData), TechData.TECH_CAPACITY)


class TestRowSelection(unittest.TestCase):
    def test_locations_only_when_nothing_was_rebased(self):
        table = TechData.rows(
            [Age2TechData.ELITE_TARKAN_HUNS, Age2TechData.BEARDED_AXE_FRANKS], civs=SEED_CIVS)
        self.assertEqual([row.item_id for row in table], [3600, 3649])
        self.assertTrue(all(row.is_location for row in table))

    def test_grant_only_rows_sit_below_the_grant_age(self):
        table = TechData.rows((), grant_age=Age2AgeData.CASTLE, civs=SEED_CIVS)
        self.assertTrue(table)
        for row in table:
            self.assertEqual(row.item_id, TechData.NO_ITEM)
            self.assertFalse(row.is_location)
            self.assertLess(row.tech.age, Age2AgeData.CASTLE)

    def test_grant_only_rows_skip_other_civs_uniques(self):
        table = TechData.rows((), grant_age=Age2AgeData.IMPERIAL, civs=[Age2CivData.FRANKS])
        for row in table:
            self.assertIn(row.tech.item.type.civ, (-1, FRANKS))

    def test_a_location_is_never_also_a_grant_only_row(self):
        table = TechData.rows(UPGRADES, grant_age=Age2AgeData.IMPERIAL, civs=SEED_CIVS)
        ids = [row.tech for row in table if row.is_location]
        self.assertEqual(sorted(ids), sorted(UPGRADES))
        self.assertEqual(len(ids), len(set(ids)))

    def test_units_and_lock_technologies_matches_the_measured_shape(self):
        table = TechData.rows(UPGRADES, grant_age=Age2AgeData.IMPERIAL, civs=SEED_CIVS)
        locations = [row for row in table if row.is_location]
        grant_only = [row for row in table if not row.is_location]
        self.assertEqual(len(locations), 23)
        self.assertEqual(len(grant_only), 48)

    def test_a_location_no_civilization_can_research_is_refused(self):
        plumed = Age2TechData.ELITE_PLUMED_ARCHER_MAYANS
        with self.assertRaises(ValueError):
            TechData.rows([plumed], civs=SEED_CIVS)

    def test_an_unknown_item_id_is_refused(self):
        with self.assertRaises(ValueError):
            TechData.rows([Age2TechData.ELITE_TARKAN_HUNS, 999999], civs=SEED_CIVS)

    def test_rows_are_ordered_by_item_id(self):
        table = TechData.rows(GENERIC, civs=SEED_CIVS)
        self.assertEqual([row.item_id for row in table],
                         sorted(row.item_id for row in table))


class TestRender(unittest.TestCase):
    def test_an_empty_table_still_has_a_body(self):
        # The game's parser rejects an empty body, though xs-check takes it.
        self.assertTrue(TechData.render().endswith("void LoadTechTable() {\n    return;\n}\n"))

    def test_a_location_row_carries_every_addtech_argument(self):
        tarkan = Age2TechData.ELITE_TARKAN_HUNS
        rendered = TechData.render(TechData.rows([tarkan], civs=SEED_CIVS))
        tech: Tech = tarkan.item.type
        self.assertIn(
            f"    addTech({tarkan.item.id}, {tech.game_id}, {tech.effect_id}, {tech.civ}, "
            f"1, 1, {tarkan.age.value}, 1, {tarkan.prerequisiteId});", rendered)

    def test_a_grant_only_row_has_no_item_and_is_not_a_location(self):
        table = TechData.rows((), grant_age=Age2AgeData.FEUDAL, civs=[Age2CivData.FRANKS])
        rendered = TechData.render(table).splitlines()
        body = [line for line in rendered if line.startswith("    addTech(")]
        self.assertTrue(body)
        for line in body:
            self.assertTrue(line.startswith("    addTech(-1, "), line)
            # isLocation is the eighth of eleven arguments, the requirements last
            fields = line.strip().removeprefix("addTech(").removesuffix(");").split(", ")
            self.assertEqual(len(fields), 9, line)
            self.assertEqual(fields[7], "0", line)

    def test_booleans_render_as_xs_ints(self):
        rendered = TechData.render(TechData.rows(GENERIC, civs=SEED_CIVS))
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
        slot_data = SlotData.render(SlotData.slot_fields(3, tag))
        self.assertIn(f"extern const int {SlotData.SEED_HIGH} = {high};", slot_data)
        self.assertIn(f"extern const int {SlotData.SEED_LOW} = {low};", slot_data)

    def test_a_different_seed_gives_a_different_guard(self):
        one = TechData.render((), Identity.seed_tag(SEED, 3))
        two = TechData.render((), Identity.seed_tag(SEED, 4))
        self.assertNotEqual(one, two)

    def test_the_guard_precedes_the_table(self):
        rendered = TechData.render(TechData.rows([Age2TechData.ELITE_TARKAN_HUNS], civs=SEED_CIVS), Identity.seed_tag(SEED, 3))
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


class TestCivTechLists(unittest.TestCase):
    def test_included_techs_matches_the_unique_techs_the_data_assigns(self):
        for civ in Age2CivData:
            owned = {tech for tech in Age2TechData if tech.item.type.civ == civ.game_id}
            self.assertTrue(owned <= set(civ.included_techs), civ.campaign_name)

    def test_included_and_excluded_never_overlap(self):
        for civ in Age2CivData:
            self.assertFalse(set(civ.included_techs) & set(civ.excluded_techs),
                             civ.campaign_name)

    def test_a_group_tech_is_gated_like_a_unique(self):
        eagle = Age2TechData.EAGLE_WARRIOR
        self.assertFalse(eagle.item.type.is_unique)
        # Neither shipped civ reaches it, so no seed of theirs can hold it.
        with self.assertRaises(ValueError):
            TechData.rows([eagle], civs=SEED_CIVS)

        franks = Age2CivData.FRANKS
        was_in, was_out = franks.included_techs, franks.excluded_techs
        franks.included_techs = was_in + [eagle]
        franks.excluded_techs = [t for t in was_out if t is not eagle]
        self.addCleanup(setattr, franks, "excluded_techs", was_out)
        self.addCleanup(setattr, franks, "included_techs", was_in)

        # Claimed by Franks, so a Frankish seed keeps it...
        TechData.rows([eagle], civs=[franks])
        # ...and a Hunnic one still cannot reach it.
        with self.assertRaises(ValueError):
            TechData.rows([eagle], civs=[Age2CivData.HUNS])

    def test_an_excluded_shared_tech_is_refused(self):
        # Franks lack Bloodlines; Huns have it, so a two-civ seed still keeps it.
        bloodlines = Age2TechData.BLOODLINES
        self.assertIn(bloodlines, Age2CivData.FRANKS.excluded_techs)
        TechData.rows([bloodlines], civs=SEED_CIVS)
        with self.assertRaises(ValueError):
            TechData.rows([bloodlines], civs=[Age2CivData.FRANKS])

    def test_every_excluded_tech_is_a_real_catalogue_entry(self):
        for civ in Age2CivData:
            for tech in civ.excluded_techs:
                self.assertIsInstance(tech, Age2TechData, civ.campaign_name)


class TestRequirements(unittest.TestCase):
    def test_every_tech_knows_its_age(self):
        # The age used to be a requirement id; it lives in tech.age now, and XS
        # maps it back to the age-up tech, so every tech needs a usable one.
        for tech in Age2TechData:
            self.assertIn(tech.age, Age2AgeData, tech.name)

    def test_a_tech_with_no_prerequisite_renders_the_empty_slot(self):
        loom = Age2TechData.LOOM
        self.assertIsNone(loom.prerequisite)
        rendered = TechData.render(TechData.rows([loom], civs=SEED_CIVS))
        row = [l for l in rendered.splitlines() if "addTech(" in l][0]
        self.assertTrue(row.rstrip().endswith(f"{TechData.NO_PREREQUISITE});"), row)

    def test_a_prerequisite_renders_as_its_game_id(self):
        swords = Age2TechData.LONG_SWORDSMAN
        self.assertIs(swords.prerequisite, Age2TechData.MAN_AT_ARMS)
        rendered = TechData.render(TechData.rows([swords], civs=SEED_CIVS))
        row = [l for l in rendered.splitlines() if "addTech(" in l][0]
        self.assertTrue(row.rstrip().endswith(f"{swords.prerequisiteId});"), row)

    def test_every_prerequisite_names_a_real_tech(self):
        for tech in Age2TechData:
            if tech.prerequisite is not None:
                self.assertIsInstance(tech.prerequisite, Age2TechData, tech.name)

    def test_a_prerequisite_is_never_in_a_later_age(self):
        for tech in Age2TechData:
            if tech.prerequisite is not None:
                self.assertLessEqual(tech.prerequisite.age, tech.age, tech.name)


class TestNames(unittest.TestCase):
    """The six Chronicles civilizations rename a dozen standard technologies.
    They are excluded from the catalogue, but the extractor walked the civ files
    alphabetically and ACHAEMENIDS came first, so their names leaked in. These
    pin the standard names."""

    STANDARD = {
        45: "Faith", 47: "Chemistry", 63: "Keep", 93: "Ballistics",
        230: "Block Printing", 231: "Sanctity", 233: "Illumination",
        316: "Redemption", 319: "Atonement", 380: "Heated Shot",
        438: "Theocracy", 439: "Heresy",
    }
    CHRONICLES = {
        "Exorcism", "Flaming Arrows", "Bastion", "Target Practice", "Haruspicy",
        "Amulet Protection", "Purification", "Sacrificial Dedication",
        "Syncretism", "Lighthouse", "Mystery Cults", "Hemlock",
    }

    def test_the_renamed_twelve_use_their_standard_names(self):
        by_game = {tech.item.type.game_id: tech for tech in Age2TechData}
        for game_id, name in self.STANDARD.items():
            tech = by_game[game_id]
            self.assertEqual(tech.item.item_name, name, game_id)
            self.assertEqual(tech.location_name, f"Research {name}", game_id)

    def test_no_chronicles_name_is_used_anywhere(self):
        for tech in Age2TechData:
            self.assertNotIn(tech.item.item_name, self.CHRONICLES, tech.name)

    def test_a_location_name_is_its_item_name(self):
        for tech in Age2TechData:
            self.assertEqual(tech.location_name, f"Research {tech.item.item_name}", tech.name)
