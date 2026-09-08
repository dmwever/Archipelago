import os
import struct
import tempfile
import unittest
from pathlib import Path

from ..campaign import CampaignWriter
from ..campaign.CampaignReader import (
    RGE_DE2_MAX_CHAR,
    RGE_STRING_ID,
    Campaign,
)
from ..campaign.CampaignWriter import HEADER_SIZE
from ..client.handlers.InstallHandler import InstallHandler
from ..generation import Identity, SlotData
from ..locations.Campaigns import Age2CampaignData

SEED = "56761350679959987564"
VERSION = 808463922
DEPENDENCIES = (6, 2, 3, 4, 5, 6, 7)

AGEIPELAGO_BUNDLES = Path(
    os.environ.get("AGEIPELAGO_PATH", "C:/Users/dmwev/Documents/GitHub/Ageipelago")
) / "age 2 files/resources/_common/campaign"


def build_fixture(display_name: str, scenarios, junk_after_name: bytes = b"") -> bytes:
    name = display_name.encode("utf-8")
    name_field = name + b"\x00" + junk_after_name
    name_field += b"\x00" * (RGE_DE2_MAX_CHAR - len(name_field))

    entries = []
    for file_name, body in scenarios:
        encoded = file_name.encode("utf-8")
        entries.append((
            struct.pack("<HH", RGE_STRING_ID, len(encoded)) + encoded
            + struct.pack("<HH", RGE_STRING_ID, len(encoded)) + encoded,
            body,
        ))

    table_size = sum(8 + len(tail) for tail, _ in entries)
    offset = HEADER_SIZE + table_size

    table = b""
    for tail, body in entries:
        table += struct.pack("<ii", len(body), offset) + tail
        offset += len(body)

    header = (struct.pack("<i", VERSION) + struct.pack("<7i", *DEPENDENCIES)
              + name_field + struct.pack("<i", len(entries)))
    return header + table + b"".join(body for _, body in entries)


def pack(campaign: Campaign, display_name: str = None) -> bytes:
    with tempfile.TemporaryDirectory() as work:
        target = Path(work) / "out.aoe2campaign"
        CampaignWriter.write(campaign, target, display_name)
        return target.read_bytes()


def parse_table(data: bytes) -> dict:
    version, = struct.unpack_from("<i", data, 0)
    dependencies = struct.unpack_from("<7i", data, 4)
    name_field = data[32:32 + RGE_DE2_MAX_CHAR]
    count, = struct.unpack_from("<i", data, 32 + RGE_DE2_MAX_CHAR)
    off = HEADER_SIZE
    entries = []
    for _ in range(count):
        size, offset = struct.unpack_from("<ii", data, off)
        off += 8
        _, name_len = struct.unpack_from("<HH", data, off)
        off += 4
        name = data[off:off + name_len].decode("utf-8")
        off += name_len
        _, file_len = struct.unpack_from("<HH", data, off)
        off += 4
        file_name = data[off:off + file_len].decode("utf-8")
        off += file_len
        entries.append({"size": size, "offset": offset, "name": name, "file_name": file_name})
    return {"version": version, "dependencies": dependencies, "name_field": name_field,
            "entries": entries, "table_end": off}


AWKWARD = [
    ("A.aoe2scenario", b"\x01" * 7),
    ("a_much_longer_scenario_name_here.aoe2scenario", b"\x02" * 4096),
    ("Mid.aoe2scenario", b"\x03"),
]


class TestBundleRoundTrip(unittest.TestCase):
    def setUp(self):
        self.fixture = build_fixture("Fixture Campaign", AWKWARD, junk_after_name=b"\x7f\x00\xff")
        self.path = Path(self.__class__.__name__ + ".aoe2campaign")

    def read_fixture(self) -> Campaign:
        self.path.write_bytes(self.fixture)
        try:
            return Campaign(str(self.path))
        finally:
            self.path.unlink()

    def test_write_with_no_changes_is_byte_identical(self):
        rebuilt = pack(self.read_fixture())
        self.assertEqual(len(rebuilt), len(self.fixture))
        self.assertEqual(rebuilt, self.fixture)

    def test_junk_after_the_name_terminator_survives(self):
        campaign = self.read_fixture()
        self.assertEqual(campaign.header.name, "Fixture Campaign")
        self.assertEqual(pack(campaign)[32:32 + RGE_DE2_MAX_CHAR],
                         self.fixture[32:32 + RGE_DE2_MAX_CHAR])

    def test_retagged_offsets_and_sizes_are_consistent(self):
        tag = Identity.seed_tag(SEED, 3)
        campaign = self.read_fixture()
        expected_name = Identity.tagged("Fixture Campaign", tag)
        rebuilt = pack(campaign, expected_name)

        parsed = parse_table(rebuilt)
        self.assertEqual(parsed["version"], VERSION)
        self.assertEqual(parsed["dependencies"], DEPENDENCIES)
        self.assertEqual(len(parsed["entries"]), len(AWKWARD))
        self.assertEqual(parsed["name_field"].split(b"\x00")[0].decode("utf-8"), expected_name)
        self.assertEqual(set(parsed["name_field"][len(expected_name.encode()):]), {0})

        expected_offset = parsed["table_end"]
        for entry, original in zip(parsed["entries"], campaign.scenarios):
            self.assertEqual(entry["file_name"], original.file_name)
            self.assertEqual(entry["name"], original.name)
            self.assertEqual(entry["size"], original.size)
            self.assertEqual(entry["offset"], expected_offset)
            self.assertEqual(rebuilt[entry["offset"]:entry["offset"] + entry["size"]],
                             original.body)
            expected_offset += entry["size"]
        self.assertEqual(expected_offset, len(rebuilt))

    def test_retagging_leaves_the_scenario_entries_alone(self):
        tag = Identity.seed_tag(SEED, 3)
        rebuilt = pack(self.read_fixture(), Identity.tagged("Fixture Campaign", tag))
        entries = parse_table(rebuilt)["entries"]
        self.assertEqual([entry["file_name"] for entry in entries],
                         [file_name for file_name, _ in AWKWARD])
        self.assertEqual([entry["name"] for entry in entries],
                         [file_name for file_name, _ in AWKWARD])

    def test_retagging_changes_only_the_name_field(self):
        tag = Identity.seed_tag(SEED, 3)
        rebuilt = pack(self.read_fixture(), Identity.tagged("Fixture Campaign", tag))
        self.assertEqual(len(rebuilt), len(self.fixture))
        self.assertEqual(rebuilt[:32], self.fixture[:32])
        self.assertEqual(rebuilt[32 + RGE_DE2_MAX_CHAR:], self.fixture[32 + RGE_DE2_MAX_CHAR:])
        self.assertNotEqual(rebuilt[32:32 + RGE_DE2_MAX_CHAR],
                            self.fixture[32:32 + RGE_DE2_MAX_CHAR])

    def test_scenario_size_matches_the_packed_entry(self):
        for scn in self.read_fixture().scenarios:
            self.assertEqual(CampaignWriter._scenario_size(scn),
                             len(CampaignWriter._pack_scenario_header(scn, 0)))

    def test_reader_does_not_share_scenarios_between_bundles(self):
        first = self.read_fixture()
        self.fixture = build_fixture("Second", [("Only.aoe2scenario", b"\x09" * 12)])
        second = self.read_fixture()
        self.assertEqual(len(first.scenarios), len(AWKWARD))
        self.assertEqual(len(second.scenarios), 1)

    def test_display_name_too_long_is_refused(self):
        with self.assertRaises(ValueError):
            pack(self.read_fixture(), "x" * RGE_DE2_MAX_CHAR)


@unittest.skipUnless(AGEIPELAGO_BUNDLES.is_dir(), "no local Ageipelago checkout")
class TestRealBundles(unittest.TestCase):
    def test_write_with_no_changes_is_byte_identical(self):
        for data in Age2CampaignData:
            path = AGEIPELAGO_BUNDLES / (data.file_stem + ".aoe2campaign")
            if not path.is_file():
                self.skipTest(f"{path} not present")
            with self.subTest(campaign=data.campaign_name):
                original = path.read_bytes()
                self.assertEqual(pack(Campaign(str(path))), original)


class TestSlotDataFile(unittest.TestCase):
    def test_default_is_all_unset(self):
        self.assertEqual(
            SlotData.render(),
            "extern const int AP_SLOT_ID = -1;\n"
            "extern const int AP_SEED_HIGH = -1;\n"
            "extern const int AP_SEED_LOW = -1;\n")

    def test_seed_halves_reconstruct_the_tag(self):
        tag = Identity.seed_tag(SEED, 3)
        high, low = SlotData.seed_halves(tag)
        self.assertEqual((high << 16) | low, int(tag, 16))

    def test_halves_fit_the_xs_literal_ceiling(self):
        for slot in (1, 2, 250):
            for seed in (SEED, "1", "99999999999999999999"):
                values = SlotData.fields(slot, Identity.seed_tag(seed, slot))
                for name, value in values.items():
                    self.assertLessEqual(abs(value), SlotData.MAX_LITERAL, name)

    def test_oversized_literal_is_refused(self):
        with self.assertRaises(ValueError):
            SlotData.render({"AP_X": SlotData.MAX_LITERAL + 1})

    def test_slot_and_seed_are_rendered(self):
        rendered = SlotData.render(SlotData.fields(3, Identity.seed_tag(SEED, 3)))
        self.assertIn("extern const int AP_SLOT_ID = 3;", rendered)
        self.assertNotIn("-1", rendered)


class TestInstallPaths(unittest.TestCase):
    ROOT = "C:/Games/AoE2/12345"

    def handler(self) -> InstallHandler:
        handler = InstallHandler()
        handler.set_user_folder(self.ROOT)
        return handler

    def test_constructs_without_a_user_folder(self):
        InstallHandler()

    def test_paths_hang_off_the_user_folder(self):
        handler = self.handler()
        self.assertEqual(handler.campaign_dir().as_posix(),
                         self.ROOT + "/resources/_common/campaign")
        self.assertEqual(handler.xs_dir().as_posix(), self.ROOT + "/resources/_common/xs")
        self.assertEqual(handler.slot_data_path().as_posix(),
                         self.ROOT + "/resources/_common/xs/SlotData.xs")

    def test_source_and_installed_names_differ_by_the_tag(self):
        tag = Identity.seed_tag(SEED, 3)
        handler = self.handler()
        handler.setup([Age2CampaignData.ATTILA], 3, tag)
        included = handler._included_campaigns[0]
        self.assertEqual(handler.source_path(included).name, "AP Attila the Hun.aoe2campaign")
        self.assertEqual(handler.install_path(included).name,
                         f"AP Attila the Hun_{tag}.aoe2campaign")
        self.assertEqual(included.display_name, f"AP Attila the Hun_{tag}")
        self.assertEqual(handler.source_path(included).parent,
                         handler.install_path(included).parent)
