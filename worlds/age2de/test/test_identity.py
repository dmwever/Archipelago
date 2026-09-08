import io
import unittest

from ..campaign import XsdatFile
from ..client.GameClient import AP_VERSION_F32, Age2Packet, PacketStatus
from ..client.handlers.CampaignHandler import CampaignHandler
from ..generation import Identity
from ..locations.Campaigns import Age2CampaignData
from ..locations.Scenarios import Age2ScenarioData

SEED_A = "56761350679959987564"
SEED_B = "31415926535897932384"

FIXED_CLIENT_FILES = [
    "AP.xsdat", "items.xsdat", "free_items.xsdat", "locations.xsdat",
    "startup.xsdat", "buildings.xsdat", "messages.xsdat",
    "ATT1.xsdat", "JOAN6.xsdat",
]


class TestSeedTag(unittest.TestCase):
    def test_deterministic(self):
        self.assertEqual(Identity.seed_tag(SEED_A, 3), Identity.seed_tag(SEED_A, 3))

    def test_seed_separates(self):
        self.assertNotEqual(Identity.seed_tag(SEED_A, 3), Identity.seed_tag(SEED_B, 3))

    def test_slot_separates(self):
        self.assertNotEqual(Identity.seed_tag(SEED_A, 3), Identity.seed_tag(SEED_A, 5))

    def test_tag_shape(self):
        tag = Identity.seed_tag(SEED_A, 3)
        self.assertEqual(len(tag), Identity.TAG_LENGTH)
        self.assertEqual(tag, tag.lower())
        int(tag, 16)


class TestTaggedFileNames(unittest.TestCase):
    def test_round_trip(self):
        tag = Identity.seed_tag(SEED_A, 3)
        for stem in ("AP Attila the Hun", "AP_Attila_1"):
            name = Identity.xsdat_name(stem, tag)
            self.assertTrue(name.startswith(stem))
            self.assertEqual(Identity.tag_of(name), tag)

    def test_fixed_client_files_carry_no_tag(self):
        for name in FIXED_CLIENT_FILES:
            self.assertEqual(Identity.tag_of(name), "", name)

    def test_untagged_stem_passes_through(self):
        self.assertEqual(Identity.xsdat_name("AP_Attila_1", ""), "AP_Attila_1.xsdat")

    def test_slot_three_cannot_see_slot_five(self):
        three = CampaignHandler(list(Age2CampaignData))
        three.set_tag(Identity.seed_tag(SEED_A, 3))
        five = CampaignHandler(list(Age2CampaignData))
        five.set_tag(Identity.seed_tag(SEED_A, 5))

        for data in list(Age2CampaignData) + list(Age2ScenarioData):
            self.assertNotEqual(three.read_name(data), five.read_name(data), data)

    def test_handler_names_match_the_helper(self):
        tag = Identity.seed_tag(SEED_A, 3)
        handler = CampaignHandler(list(Age2CampaignData))
        handler.set_tag(tag)
        self.assertEqual(
            handler.read_name(Age2CampaignData.ATTILA),
            Identity.xsdat_name(Age2CampaignData.ATTILA.file_stem, tag))


def write_game_packet(slot_id: int, scenario_id: int, ap_version: float = 7.0,
                      location_ids=()) -> bytes:
    fp = io.BytesIO()
    XsdatFile.write_bool(fp, True)
    XsdatFile.write_int(fp, 1234)
    XsdatFile.write_float(fp, ap_version)
    XsdatFile.write_int(fp, slot_id)
    XsdatFile.write_int(fp, -1)
    for _ in range(12):
        XsdatFile.write_int(fp, -1)
    XsdatFile.write_int(fp, 0)
    XsdatFile.write_int(fp, scenario_id)
    for i in range(30):
        XsdatFile.write_int(fp, i)
    for location_id in location_ids:
        XsdatFile.write_int(fp, location_id)
    return fp.getvalue()


class TestPacketLayout(unittest.TestCase):
    def test_scenario_id_stays_at_offset_72(self):
        packet = write_game_packet(slot_id=3, scenario_id=101)
        fp = io.BytesIO(packet)
        XsdatFile.skip_int(fp, 18)
        self.assertEqual(fp.tell(), 72)
        self.assertEqual(XsdatFile.read_int(fp), 101)

    def test_reserved_block_is_still_thirty_ints(self):
        packet = write_game_packet(slot_id=3, scenario_id=101, location_ids=(10100, 10101))
        parsed = Age2Packet(io.BytesIO(packet))
        self.assertEqual(parsed.location_ids, [10100, 10101])

    def test_reads_the_slot_back(self):
        parsed = Age2Packet(io.BytesIO(write_game_packet(slot_id=5, scenario_id=206)))
        self.assertEqual(parsed.slot_id, 5)
        self.assertEqual(parsed.scenario_id, 206)
        self.assertEqual(parsed.ap_version, AP_VERSION_F32)


def context_for_slot(slot_id: int):
    from ..client.GameClient import Age2GameContext, ClientStatus, DefaultClientInterface
    ctx = Age2GameContext(client_interface=DefaultClientInterface())
    ctx.client_status = ClientStatus(unlocked_items=[], slot_id=slot_id)
    return ctx


class TestSlotMismatch(unittest.TestCase):
    def test_matching_slot_is_accepted(self):
        ctx = context_for_slot(3)
        packet = Age2Packet(io.BytesIO(write_game_packet(slot_id=3, scenario_id=101)))
        self.assertNotEqual(ctx.update_packet(packet), PacketStatus.WRONG_SLOT)

    def test_foreign_slot_is_rejected(self):
        ctx = context_for_slot(3)
        packet = Age2Packet(io.BytesIO(write_game_packet(slot_id=5, scenario_id=101)))
        self.assertEqual(ctx.update_packet(packet), PacketStatus.WRONG_SLOT)

    def test_stale_protocol_is_rejected_before_the_slot(self):
        ctx = context_for_slot(3)
        packet = Age2Packet(io.BytesIO(
            write_game_packet(slot_id=2, scenario_id=101, ap_version=6.5)))
        self.assertEqual(ctx.update_packet(packet), PacketStatus.WRONG_VERSION)

    def test_mismatch_is_reported_once(self):
        ctx = context_for_slot(3)
        reported = []
        ctx.report_packet_mismatch_once("slot", "first")
        reported.append(ctx.reported_packet_mismatch)
        ctx.report_packet_mismatch_once("slot", "second")
        self.assertEqual(reported, ["slot"])
        self.assertEqual(ctx.reported_packet_mismatch, "slot")
