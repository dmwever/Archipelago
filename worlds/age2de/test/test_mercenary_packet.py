"""The finished-mercenary id rides in the first slot of the scenario packet's reserved block.

Two things make that placement load-bearing. AP_Write fills the rest of the block with the loop
counter rather than zeros, so a field taken from there has to be written explicitly on both sides or
it reads back as its own index. And CampaignHandler.find_active_campaign reaches scenario_id with a
hardcoded skip of 18 ints, so anything inserted ahead of it silently repoints that read -- these
tests pin the field's offset and the total width of the fixed header.
"""

import io
import unittest

from ..campaign import XsdatFile
from ..client.GameClient import Age2Packet
from ..client.handlers.CampaignHandler import CampaignHandler
from ..items.Items import Age2ItemData
from ..locations.Campaigns import Age2CampaignData

FIXED_INTS = 49
SCENARIO_ID_OFFSET = 72
RESERVED_AFTER_MERCENARY = 24


def build_packet(scenario_id: int = 101, mercenary_id: int = -1, queue_serial: int = -1,
                 applied_item_count: int = 0, checked_locations_count: int = 0,
                 locations: list[int] = (), current_packet_location_count: int | None = None,
                 trailer: bytes = b"") -> io.BytesIO:
    """A scenario packet exactly as AP_Write lays it out, plus any bytes a host appends after it."""
    if current_packet_location_count is None:
        current_packet_location_count = len(locations)
    fp = io.BytesIO()
    XsdatFile.write_bool(fp, True)          # active
    XsdatFile.write_int(fp, 1234)           # ping
    XsdatFile.write_int(fp, 0)              # world major
    XsdatFile.write_int(fp, 7)              # slot
    XsdatFile.write_int(fp, -1)             # latest message id
    for _ in range(12):
        XsdatFile.write_int(fp, -1)         # item ids
    XsdatFile.write_bool(fp, False)         # completed
    XsdatFile.write_int(fp, scenario_id)
    XsdatFile.write_int(fp, 3)              # world minor
    XsdatFile.write_int(fp, mercenary_id)   # first reserved int
    XsdatFile.write_int(fp, queue_serial)   # second reserved int
    XsdatFile.write_int(fp, applied_item_count)
    XsdatFile.write_int(fp, checked_locations_count)
    XsdatFile.write_int(fp, current_packet_location_count)
    for index in range(RESERVED_AFTER_MERCENARY):
        XsdatFile.write_int(fp, index)      # AP_Write writes the loop counter here, not zeros
    for location in locations:
        XsdatFile.write_int(fp, location)
    fp.write(trailer)
    fp.seek(0)
    return fp


class TestPacketLayout(unittest.TestCase):

    def test_the_fixed_header_is_still_49_ints(self) -> None:
        fp = build_packet()
        self.assertEqual(FIXED_INTS * 4, len(fp.getvalue()),
                         "the reserved block shrank by one to make room, so the width is unchanged")

    def test_scenario_id_stays_at_byte_offset_72(self) -> None:
        fp = build_packet(scenario_id=205)
        fp.seek(SCENARIO_ID_OFFSET)
        self.assertEqual(205, XsdatFile.read_int(fp),
                         "find_active_campaign skips 18 ints to reach this")

    def test_find_active_campaign_still_reads_the_right_scenario(self) -> None:
        """The same hardcoded skip, exercised the way CampaignHandler does it."""
        fp = build_packet(scenario_id=106)
        fp.read(1)
        fp.seek(0)
        XsdatFile.skip_int(fp, 18)
        self.assertEqual(106, XsdatFile.read_int(fp))

    def test_an_idle_packet_reports_no_mercenary(self) -> None:
        self.assertEqual(-1, Age2Packet(build_packet()).completed_mercenary_id)

    def test_a_finished_mercenary_survives_the_reserved_block(self) -> None:
        wanted = Age2ItemData.AP_JOAN_5_LOYALISTS
        packet = Age2Packet(build_packet(mercenary_id=wanted.id))
        self.assertEqual(wanted.id, packet.completed_mercenary_id,
                         "the loop counter filling the rest of the block must not bleed into this")

    def test_the_consumed_queue_serial_survives_the_reserved_block(self) -> None:
        packet = Age2Packet(build_packet(queue_serial=7))
        self.assertEqual(7, packet.acked_queue_serial,
                         "the loop counter filling the rest of the block must not bleed into this")

    def test_the_location_tail_still_starts_after_the_header(self) -> None:
        packet = Age2Packet(build_packet(mercenary_id=4008, locations=[20101, 20102]))
        self.assertEqual([20101, 20102], packet.location_ids,
                         "a mis-sized reserved block would swallow or invent locations")


if __name__ == "__main__":
    unittest.main()


class TestTheDeliveryCursor(unittest.TestCase):
    """appliedItemCount came out of the reserved block, so it has to be read explicitly."""

    def test_an_idle_packet_reports_an_empty_cursor(self) -> None:
        self.assertEqual(0, Age2Packet(build_packet()).applied_item_count)

    def test_the_cursor_survives_the_reserved_block(self) -> None:
        packet = Age2Packet(build_packet(applied_item_count=137))
        self.assertEqual(137, packet.applied_item_count,
                         "the loop counter filling the rest of the block must not bleed into this")

    def test_taking_a_field_did_not_move_the_scenario_id(self) -> None:
        fp = build_packet(scenario_id=205, applied_item_count=9)
        fp.seek(SCENARIO_ID_OFFSET)
        self.assertEqual(205, XsdatFile.read_int(fp))



class TestTheCheckedLocationsAck(unittest.TestCase):
    """The game reports how many checked ids its last read of locations.xsdat took in.

    It came out of the reserved block, so it has to be read explicitly or it reads back as its own
    loop index. The client compares it with the set it is writing and asks for another read while
    the two disagree, so a stale value here means the game never learns the checked set.
    """

    def test_an_idle_packet_reports_an_empty_checked_set(self) -> None:
        self.assertEqual(0, Age2Packet(build_packet()).checked_locations_count)

    def test_the_ack_survives_the_reserved_block(self) -> None:
        packet = Age2Packet(build_packet(checked_locations_count=12))
        self.assertEqual(12, packet.checked_locations_count,
                         "the loop counter filling the rest of the block must not bleed into this")

    def test_taking_the_ack_did_not_move_the_scenario_id(self) -> None:
        fp = build_packet(scenario_id=205, checked_locations_count=9)
        fp.seek(SCENARIO_ID_OFFSET)
        self.assertEqual(205, XsdatFile.read_int(fp))

    def test_taking_the_ack_did_not_widen_the_fixed_header(self) -> None:
        self.assertEqual(FIXED_INTS * 4, len(build_packet(checked_locations_count=4).getvalue()),
                         "the reserved block must shrink by one to pay for the ack")

    def test_the_ack_does_not_eat_the_location_tail(self) -> None:
        packet = Age2Packet(build_packet(checked_locations_count=3, locations=[20101, 20102]))
        self.assertEqual([20101, 20102], packet.location_ids)


class TestTheCurrentPacketLocationCount(unittest.TestCase):
    """The game says how many location ids follow the header, so the client stops there.

    Anything after them belongs to someone else -- the XS function injector appends its response
    section to this same file -- and reading to EOF would send those bytes as location checks.
    """

    def test_an_idle_packet_carries_no_locations(self) -> None:
        packet = Age2Packet(build_packet())
        self.assertEqual(0, packet.current_packet_location_count)
        self.assertEqual([], packet.location_ids)

    def test_the_count_survives_the_reserved_block(self) -> None:
        packet = Age2Packet(build_packet(locations=[20101, 20102, 20103]))
        self.assertEqual(3, packet.current_packet_location_count,
                         "the loop counter filling the rest of the block must not bleed into this")

    def test_trailing_bytes_are_not_read_as_locations(self) -> None:
        trailer = b"XSIJ" + bytes(range(28))
        packet = Age2Packet(build_packet(locations=[20101, 20102], trailer=trailer))
        self.assertEqual([20101, 20102], packet.location_ids)

    def test_a_truncated_tail_reads_only_what_is_there(self) -> None:
        packet = Age2Packet(build_packet(locations=[20101], current_packet_location_count=3))
        self.assertEqual([20101], packet.location_ids)

    def test_taking_the_count_did_not_move_the_scenario_id(self) -> None:
        fp = build_packet(scenario_id=205, locations=[20101])
        fp.seek(SCENARIO_ID_OFFSET)
        self.assertEqual(205, XsdatFile.read_int(fp))

    def test_taking_the_count_did_not_widen_the_fixed_header(self) -> None:
        self.assertEqual(FIXED_INTS * 4, len(build_packet().getvalue()),
                         "the reserved block must shrink by one to pay for the count")
