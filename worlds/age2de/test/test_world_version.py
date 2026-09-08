import os
import re
import unittest
from pathlib import Path

from Utils import Version

from .. import Age2World
from ..generation import WorldVersion


class TestCompatibilityRule(unittest.TestCase):
    def test_identical_is_compatible(self):
        self.assertTrue(WorldVersion.compatible(Version(0, 2, 3), Version(0, 2, 3)))

    def test_build_may_differ(self):
        self.assertTrue(WorldVersion.compatible(Version(0, 2, 0), Version(0, 2, 3)))
        self.assertTrue(WorldVersion.compatible(Version(0, 2, 9), Version(0, 2, 1)))

    def test_minor_is_the_breaking_axis(self):
        self.assertFalse(WorldVersion.compatible(Version(0, 1, 9), Version(0, 2, 0)))
        self.assertFalse(WorldVersion.compatible(Version(0, 2, 3), Version(0, 3, 0)))

    def test_major_must_match(self):
        self.assertFalse(WorldVersion.compatible(Version(0, 2, 3), Version(1, 2, 3)))

    def test_unknown_is_incompatible(self):
        self.assertFalse(WorldVersion.compatible(WorldVersion.UNKNOWN, Age2World.world_version))


class TestParse(unittest.TestCase):
    def test_string(self):
        self.assertEqual(WorldVersion.parse("0.2.3"), Version(0, 2, 3))

    def test_list_is_padded(self):
        self.assertEqual(WorldVersion.parse([0, 2]), Version(0, 2, 0))

    def test_version_passes_through(self):
        self.assertEqual(WorldVersion.parse(Version(0, 2, 3)), Version(0, 2, 3))

    def test_missing_or_junk_is_unknown(self):
        for value in (None, "", "nonsense", "0.x.3", {}):
            self.assertEqual(WorldVersion.parse(value), WorldVersion.UNKNOWN, value)


class TestManifestIsTheSourceOfTruth(unittest.TestCase):
    def test_world_version_comes_from_the_manifest(self):
        self.assertEqual(Age2World.world_version, Version(0, 2, 3))

    def test_slot_data_is_not_hardcoded(self):
        import inspect
        source = inspect.getsource(Age2World.fill_slot_data)
        self.assertIn("self.world_version", source)
        for stale in ("version_public", "version_major", "version_minor"):
            self.assertNotIn(stale, source)

    def test_a_seed_from_this_world_is_compatible_with_this_client(self):
        emitted = WorldVersion.parse(Age2World.world_version.as_simple_string())
        self.assertTrue(WorldVersion.compatible(emitted, Age2World.world_version))


class TestDescribe(unittest.TestCase):
    def test_names_both_versions(self):
        message = WorldVersion.describe(Version(0, 2, 3), Version(0, 3, 0))
        self.assertIn("0.2.3", message)
        self.assertIn("0.3.0", message)


AGEIPELAGO_XS = Path(
    os.environ.get("AGEIPELAGO_PATH", "C:/Users/dmwev/Documents/GitHub/Ageipelago")
) / "age 2 files/resources/_common/xs/AP.xs"


@unittest.skipUnless(AGEIPELAGO_XS.is_file(), "no local Ageipelago checkout")
class TestApXsDeclaresTheSameVersion(unittest.TestCase):
    def declared(self) -> Version:
        source = AGEIPELAGO_XS.read_text(encoding="utf-8")
        found = {}
        for name in ("worldMajor", "worldMinor"):
            match = re.search(r"^int %s = (\d+);" % name, source, re.M)
            self.assertIsNotNone(match, f"{name} not declared in AP.xs")
            found[name] = int(match.group(1))
        return Version(found["worldMajor"], found["worldMinor"], 0)

    def test_ap_xs_matches_the_manifest(self):
        self.assertTrue(
            WorldVersion.compatible(self.declared(), Age2World.world_version),
            f"AP.xs declares {self.declared().as_simple_string()} but archipelago.json says "
            f"{Age2World.world_version.as_simple_string()}; bump AP.xs when the world minor changes")
