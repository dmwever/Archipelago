import io
import time
import unittest

from ..campaign import XsdatFile
from ..client.GameClient import (AP_WORLD_VERSION, MISSING_GRACE_SECONDS, Age2Packet,
                                 PacketStatus)
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
        handler.set_player_name("Dave")
        self.assertEqual(
            handler.campaign_read_name(Age2CampaignData.ATTILA),
            Identity.campaign_xsdat_name(Age2CampaignData.ATTILA.file_stem, tag, "Dave"))


class TestSourceNames(unittest.TestCase):
    def test_the_source_bundle_carries_the_template_suffix(self):
        self.assertEqual(Identity.source_campaign_file_name("AP Joan of Arc"),
                         "AP Joan of Arc Template.aoe2campaign")

    def test_the_player_copy_drops_the_template_suffix(self):
        tag = Identity.seed_tag(SEED_A, 3)
        installed = Identity.campaign_file_name("AP Joan of Arc", tag, "Dave")
        self.assertEqual(installed, f"AP Joan of Arc_Dave_{tag}.aoe2campaign")
        self.assertNotIn(Identity.SOURCE_SUFFIX, installed)

    def test_the_engine_xsdat_drops_the_template_suffix(self):
        tag = Identity.seed_tag(SEED_A, 3)
        written = Identity.campaign_xsdat_name("AP Joan of Arc", tag, "Dave")
        self.assertNotIn(Identity.SOURCE_SUFFIX, written)
        self.assertEqual(Identity.tag_of(written), tag)


class TestPlayerNames(unittest.TestCase):
    def test_the_player_sits_before_the_tag(self):
        tag = Identity.seed_tag(SEED_A, 3)
        self.assertEqual(Identity.campaign_stem("AP Joan of Arc", tag, "Dave"),
                         f"AP Joan of Arc_Dave_{tag}")

    def test_the_tag_survives_a_player_segment(self):
        """The whole reason the player goes before the tag rather than after it."""
        tag = Identity.seed_tag(SEED_A, 3)
        name = Identity.campaign_xsdat_name("AP Joan of Arc", tag, "Dave")
        self.assertEqual(Identity.tag_of(name), tag)

    def test_campaigns_carry_the_player_but_scenarios_do_not(self):
        tag = Identity.seed_tag(SEED_A, 3)
        handler = CampaignHandler(list(Age2CampaignData))
        handler.set_tag(tag)
        handler.set_player_name("Dave")
        self.assertIn("Dave", handler.campaign_read_name(Age2CampaignData.ATTILA))
        self.assertNotIn("Dave", handler.read_name(Age2ScenarioData.AP_ATTILA_1))


class TestSanitizePlayer(unittest.TestCase):
    def test_a_clean_name_is_untouched(self):
        for name in ("Dave", "Dave Smith", "Dave-Smith_1"):
            self.assertEqual(Identity.sanitize_player(name), name)

    def test_reserved_characters_are_dropped(self):
        self.assertEqual(Identity.sanitize_player('Da:ve|B'), "DaveB")
        self.assertEqual(Identity.sanitize_player('a<b>c"d/e\\f|g?h*i'), "abcdefghi")

    def test_control_characters_are_dropped(self):
        self.assertEqual(Identity.sanitize_player("Da\x00v\x1fe"), "Dave")

    def test_whitespace_is_collapsed_and_trimmed(self):
        self.assertEqual(Identity.sanitize_player("  Dave   Smith  "), "Dave Smith")
        self.assertEqual(Identity.sanitize_player("Dave\tSmith"), "Dave Smith")

    def test_trailing_dots_and_spaces_go(self):
        """Windows will not open a file whose name ends in a dot or a space."""
        self.assertEqual(Identity.sanitize_player("Dave..."), "Dave")
        self.assertEqual(Identity.sanitize_player(".Dave."), "Dave")

    def test_a_name_of_only_forbidden_characters_is_empty(self):
        for name in ('///', '<>:"|?*', "...", "   ", ""):
            self.assertEqual(Identity.sanitize_player(name), "", name)

    def test_non_latin_names_survive(self):
        for name in ("Ярослав", "田中", "Ægir"):
            self.assertEqual(Identity.sanitize_player(name), name)

    def test_the_result_is_usable_in_a_file_name(self):
        tag = Identity.seed_tag(SEED_A, 3)
        safe = Identity.sanitize_player('Da:ve|B')
        name = Identity.campaign_file_name("AP Joan of Arc", tag, safe)
        self.assertNotIn(":", name)
        self.assertNotIn("|", name)


def write_game_packet(slot_id: int, scenario_id: int, major: int = AP_WORLD_VERSION.major,
                      minor: int = AP_WORLD_VERSION.minor, location_ids=()) -> bytes:
    fp = io.BytesIO()
    XsdatFile.write_bool(fp, True)
    XsdatFile.write_int(fp, 1234)
    XsdatFile.write_int(fp, major)
    XsdatFile.write_int(fp, slot_id)
    XsdatFile.write_int(fp, -1)
    for _ in range(12):
        XsdatFile.write_int(fp, -1)
    XsdatFile.write_int(fp, 0)
    XsdatFile.write_int(fp, scenario_id)
    XsdatFile.write_int(fp, minor)
    for i in range(29):
        XsdatFile.write_int(fp, i)
    for location_id in location_ids:
        XsdatFile.write_int(fp, location_id)
    return fp.getvalue()


def stale_float_packet(protocol: float, slot_id: int, scenario_id: int) -> bytes:
    fp = io.BytesIO()
    XsdatFile.write_bool(fp, True)
    XsdatFile.write_int(fp, 1234)
    XsdatFile.write_float(fp, protocol)
    XsdatFile.write_int(fp, slot_id)
    XsdatFile.write_int(fp, -1)
    for _ in range(12):
        XsdatFile.write_int(fp, -1)
    XsdatFile.write_int(fp, 0)
    XsdatFile.write_int(fp, scenario_id)
    for i in range(30):
        XsdatFile.write_int(fp, i)
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

    def test_reads_the_slot_and_version_back(self):
        parsed = Age2Packet(io.BytesIO(write_game_packet(slot_id=5, scenario_id=206)))
        self.assertEqual(parsed.slot_id, 5)
        self.assertEqual(parsed.scenario_id, 206)
        self.assertEqual(parsed.world_major, AP_WORLD_VERSION.major)
        self.assertEqual(parsed.world_minor, AP_WORLD_VERSION.minor)
        self.assertTrue(parsed.installed_version_matches())


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

    def test_an_older_install_is_rejected_before_the_slot(self):
        ctx = context_for_slot(3)
        packet = Age2Packet(io.BytesIO(write_game_packet(
            slot_id=2, scenario_id=101, minor=AP_WORLD_VERSION.minor - 1)))
        self.assertEqual(ctx.update_packet(packet), PacketStatus.WRONG_VERSION)

    def test_a_newer_install_is_rejected(self):
        ctx = context_for_slot(3)
        packet = Age2Packet(io.BytesIO(write_game_packet(
            slot_id=3, scenario_id=101, minor=AP_WORLD_VERSION.minor + 1)))
        self.assertEqual(ctx.update_packet(packet), PacketStatus.WRONG_VERSION)

    def test_a_different_major_is_rejected(self):
        ctx = context_for_slot(3)
        packet = Age2Packet(io.BytesIO(write_game_packet(
            slot_id=3, scenario_id=101, major=AP_WORLD_VERSION.major + 1)))
        self.assertEqual(ctx.update_packet(packet), PacketStatus.WRONG_VERSION)

    def test_a_float_writing_install_is_rejected(self):
        for protocol in (6.5, 7.0):
            with self.subTest(protocol=protocol):
                ctx = context_for_slot(3)
                packet = Age2Packet(io.BytesIO(stale_float_packet(protocol, 3, 101)))
                self.assertFalse(packet.installed_version_matches())
                self.assertEqual(ctx.update_packet(packet), PacketStatus.WRONG_VERSION)

    def test_the_wire_version_is_the_world_version(self):
        from .. import Age2World
        self.assertEqual(AP_WORLD_VERSION, Age2World.world_version)

    def test_an_install_holds_the_mismatch_report(self):
        ctx = context_for_slot(3)
        ctx.install_handler.installing = True
        ctx.report_install_mismatch_once()
        ctx.missing_since = time.monotonic() - MISSING_GRACE_SECONDS - 1
        ctx.report_install_mismatch_once()
        self.assertFalse(ctx.reported_install_mismatch)
        self.assertEqual(ctx.missing_since, 0.0)

    def test_the_grace_window_restarts_after_an_install(self):
        ctx = context_for_slot(3)
        ctx.install_handler.installing = True
        ctx.missing_since = time.monotonic() - MISSING_GRACE_SECONDS - 1
        ctx.report_install_mismatch_once()
        ctx.install_handler.installing = False
        ctx.report_install_mismatch_once()
        self.assertFalse(ctx.reported_install_mismatch)
        self.assertGreater(ctx.missing_since, 0.0)

    def test_mismatch_is_reported_once(self):
        ctx = context_for_slot(3)
        reported = []
        ctx.report_packet_mismatch_once("slot", "first")
        reported.append(ctx.reported_packet_mismatch)
        ctx.report_packet_mismatch_once("slot", "second")
        self.assertEqual(reported, ["slot"])
        self.assertEqual(ctx.reported_packet_mismatch, "slot")
