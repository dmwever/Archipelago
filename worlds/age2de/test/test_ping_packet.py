"""The ping packet carries the seed, and both halves of it have to agree on the order.

A slot id identifies a player within a multiworld, not the multiworld itself, and every solo seed
is slot 1 - so the slot check alone passes when one seed is installed and another is hosted. The
seed halves close that, but only while GameClient.ping_game writes them in the order AP_Read reads
them, and nothing but these tests holds the two files in step.
"""

import os
import re
import unittest
from pathlib import Path

from ..generation import SlotData

AGEIPELAGO_XS = Path(
    os.environ.get("AGEIPELAGO_PATH", "C:/Users/dmwev/Documents/GitHub/Ageipelago")
) / "age 2 files/resources/_common/xs/AP.xs"

CLIENT = Path(__file__).resolve().parent.parent / "client/GameClient.py"

PING_FIELDS = ["scenario_id", "current_ping_id", "major", "minor", "slot_id", "high", "low"]


class TestSeedHalves(unittest.TestCase):
    def test_halves_round_trip(self):
        high, low = SlotData.seed_halves("deadbeef")
        self.assertEqual((high << SlotData.HALF_WIDTH) | low, 0xDEADBEEF)

    def test_halves_fit_the_wire(self):
        for tag in ("ffffffff", "00000001", "a1b2c3d4"):
            with self.subTest(tag):
                high, low = SlotData.seed_halves(tag)
                self.assertLessEqual(max(high, low), SlotData.HALF_MASK)
                self.assertGreaterEqual(min(high, low), 0)


class TestTheClientWritesTheSeed(unittest.TestCase):
    def body(self) -> str:
        source = CLIENT.read_text(encoding="utf-8")
        start = source.index("def ping_game")
        return source[start:source.index("\n\nasync def", start)]

    def test_the_seed_follows_the_slot_id(self):
        written = re.findall(r"write_int\(fp, ([^)]+)\)", self.body())
        self.assertIn("high", written, "ping_game never writes the seed")
        self.assertEqual(written.index("high"), written.index("self.client_status.slot_id") + 1,
                         "the seed must follow the slot id, as AP_Read expects")
        self.assertEqual(written.index("low"), written.index("high") + 1)

    def test_an_unconnected_client_sends_unset(self):
        self.assertIn("SlotData.UNSET", CLIENT.read_text(encoding="utf-8"),
                      "a client with no tag must send UNSET, not crash or send a stale seed")


@unittest.skipUnless(AGEIPELAGO_XS.is_file(), "no local Ageipelago checkout")
class TestTheGameReadsTheSeed(unittest.TestCase):
    def body(self) -> str:
        source = AGEIPELAGO_XS.read_text(encoding="utf-8")
        start = source.index("void AP_Read()")
        return source[start:source.index("\nvoid ", start + 10)]

    def test_the_seed_is_compared(self):
        body = self.body()
        self.assertIn("AP_SEED_HIGH", body, "AP_Read never compares the seed")
        self.assertIn("AP_SEED_LOW", body)

    def test_the_seed_is_read_after_the_slot_id(self):
        body = self.body()
        self.assertLess(body.index("check_slotId"), body.index("check_seedHigh"),
                        "the game must read the seed after the slot id, as the client writes it")
        self.assertLess(body.index("check_seedHigh"), body.index("check_seedLow"))

    def test_the_mismatch_stops_the_read(self):
        guard = self.body()
        guard = guard[guard.index("check_seedHigh"):]
        self.assertIn("ReportMismatch", guard.split("int items")[0],
                      "a seed mismatch must report and return before any rule is enabled")
