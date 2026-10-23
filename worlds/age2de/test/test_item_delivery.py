"""Item delivery over items.xsdat.

The window is addressed, not positional: it carries the cursor it was written for, and the game
applies it only when that matches its own, all of it or none. Re-reading a window it has already
applied is a no-op, because the base no longer matches.

That makes the cursor the whole protocol. The game owns it, a loaded save rewinds it, and the
client streams from wherever the packet says it is. FakeGame below stands in for AP.xs's ReadItems
so a full delivery can be driven without the game running.
"""

import asyncio
import os
import shutil
import struct
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from ..campaign import XsdatFile
from ..client import GameClient
from ..client.GameClient import (
    AGE2_USER_PROFILE,
    Age2GameContext,
    DefaultClientInterface,
)
from ..client.handlers.StorageHandler import StorageHandler
from ..items import Items
from ..items.Items import Age2ItemData


def read_ints(path: str) -> list[int]:
    if not os.path.exists(path):
        return []
    with open(path, "rb") as fp:
        data = fp.read()
    return [struct.unpack("<i", data[i:i + 4])[0] for i in range(0, len(data), 4)]


class FakeGame:
    """The XS side of the handshake, as AP.xs implements it once the window gained a base."""

    def __init__(self) -> None:
        self.applied_item_count = 0
        self.granted: list[int] = []
        self.ignored: list[list[int]] = []

    def read_items(self, folder: str) -> None:
        data = read_ints(folder + "items.xsdat")
        if not data:
            return
        base, entries = data[0], data[1:]
        if base != self.applied_item_count:
            self.ignored.append(entries)
            return
        self.granted.extend(entries)
        self.applied_item_count += len(entries)


class TestItemDelivery(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        os.makedirs(self._tmp.name + AGE2_USER_PROFILE, exist_ok=True)

        self.ctx = Age2GameContext(DefaultClientInterface())
        # Goes through the real setter so the storage handler writes into the temp folder
        # too; sync() below records what each pass paid out, on every tick.
        self.ctx.update_game_user_folder(self._tmp.name)
        self.folder = self.ctx.profile_folder()
        self.game = FakeGame()
        # These exercise the window, not the gate on it. TestOneShotSkipping covers that.
        self.ctx.reconcile_spent(0)

    # -- helpers ---------------------------------------------------------

    def reconnect(self) -> None:
        """A first connect: no local record, and the server has not answered yet."""
        self.ctx.storage_handler.state_path().unlink(missing_ok=True)
        self.ctx.storage_handler = StorageHandler()
        self.ctx.update_game_user_folder(self._tmp.name)

    def unlock(self, *items: Age2ItemData) -> None:
        self.ctx.client_status.unlocked_items.extend(items)

    def full_tick(self) -> None:
        """The item phase of status_loop, in the same order, plus the game's response."""
        self.sync(self.game.applied_item_count)
        # ping_game arms ReadItems only while a window is outstanding.
        if self.ctx.item_handler.in_flight():
            self.game.read_items(self.folder)

    def sync(self, applied: int = 0) -> None:
        """One delivery pass, gated and recorded the way status_loop does it."""
        record = self.ctx.storage_handler
        if not record.is_up_to_date():
            return
        record.try_flush()
        delivered = self.ctx.item_handler.try_sync_delivered(
            self.ctx.client_status.unlocked_items, applied)
        if record.mark_spent(delivered):
            self.ctx.client_interface.on_item_spent(record.spent_mask())
        self.ctx.item_handler.try_write_to_file(self.ctx.spent_items())

    def send(self, applied: int = 0) -> None:
        self.sync(applied)

    def spent(self, mask: int) -> None:
        """Put a record in place the way a connect does: save it, then reconcile."""
        self.ctx.storage_handler.try_save(mask)
        self.ctx.reconcile_spent(0)

    def sent_items(self) -> list[int]:
        return read_ints(self.folder + "items.xsdat")

    def sent_window(self) -> list[int]:
        """The entries, without the base that addresses them."""
        return self.sent_items()[1:]

    # -- tests -----------------------------------------------------------

    def test_the_window_carries_the_cursor_it_was_written_for(self) -> None:
        items = list(Age2ItemData)[:100]
        self.unlock(*items)

        self.send(40)

        written = self.sent_items()
        self.assertEqual(40, written[0], "the window is addressed to the cursor it starts at")
        self.assertEqual([item.id for item in items[40:]], written[1:],
                         "the window is everything from the cursor on, uncapped")

    def test_a_window_for_another_cursor_applies_nothing(self) -> None:
        """A leftover file, or one written before a save was loaded, must not be replayed."""
        self.unlock(*list(Age2ItemData)[:20])
        self.send()
        self.game.applied_item_count = 5

        self.game.read_items(self.folder)

        self.assertEqual([], self.game.granted)
        self.assertEqual(5, self.game.applied_item_count)

    def test_re_reading_an_applied_window_is_a_no_op(self) -> None:
        """The cursor moved past the base, so the same file can never be applied twice."""
        self.unlock(*list(Age2ItemData)[:20])
        self.send()
        self.game.read_items(self.folder)
        granted_once = list(self.game.granted)

        self.game.read_items(self.folder)

        self.assertEqual(granted_once, self.game.granted)

    def test_an_empty_file_applies_nothing(self) -> None:
        """A truncated or half-written file has no base to match, and must not advance."""
        open(self.folder + "items.xsdat", "wb").close()

        self.game.read_items(self.folder)

        self.assertEqual([], self.game.granted)
        self.assertEqual(0, self.game.applied_item_count)

    def test_a_rewound_cursor_replays_the_gap(self) -> None:
        """The whole point: a loaded save reports less, and the client streams from there."""
        items = list(Age2ItemData)[:20]
        self.unlock(*items)
        for _ in range(10):
            self.full_tick()
        self.assertEqual(len(items), self.game.applied_item_count)

        self.game.applied_item_count = 5
        self.game.granted.clear()
        for _ in range(10):
            self.full_tick()

        expected = [Items.SKIP_ITEM_ID if item in Items.ONE_SHOT_ITEMS else item.id
                    for item in items[5:]]
        self.assertIn(Items.SKIP_ITEM_ID, expected,
                      "this fixture proves nothing unless the replayed range holds a one-shot")
        self.assertEqual(expected, self.game.granted,
                         "the gap was not replayed, or a one-shot was paid out a second time")

    def test_every_item_is_delivered(self) -> None:
        """20 items across two windows: all 20 reach the game, none skipped."""
        items = list(Age2ItemData)[:20]
        self.unlock(*items)

        for _ in range(30):
            self.full_tick()

        self.assertEqual(self.game.ignored, [], "the game discarded ids it was sent")
        self.assertEqual(
            self.game.granted,
            [item.id for item in items],
            "not every unlocked item reached the game",
        )
        self.assertEqual(self.game.applied_item_count, len(items))

    def test_duplicate_ids_in_one_window(self) -> None:
        """Filler resources repeat; acking must count them, not collapse them."""
        wood = Age2ItemData.FILLER_WOOD_SMALL
        self.unlock(*([wood] * 5))

        for _ in range(20):
            self.full_tick()

        self.assertEqual(self.game.granted, [wood.id] * 5)
        self.assertEqual(self.game.applied_item_count, 5)

    def test_an_unknown_item_id_is_skipped_not_raised(self) -> None:
        """An id this world does not know must not take the connection down with it."""
        from NetUtils import NetworkItem

        from ..client.ApClient import Age2Context

        ap = Age2Context.__new__(Age2Context)
        ap.game_ctx = self.ctx

        known = list(Age2ItemData)[1:3]
        packet = {"index": 0, "items": [NetworkItem(999999, 0, 0, 0)]
                  + [NetworkItem(item.id, 0, 0, 0) for item in known]}

        ap._handle_received_items(packet)

        self.assertEqual(
            self.ctx.client_status.unlocked_items,
            known,
            "an id the world does not know killed the ReceivedItems handler",
        )

    def test_index_zero_resync_does_not_duplicate_the_item_list(self) -> None:
        """A mid-session resend replaces the list; the cursor stays valid over it."""
        from NetUtils import NetworkItem

        from ..client.ApClient import Age2Context

        ap = Age2Context.__new__(Age2Context)
        ap.game_ctx = self.ctx

        items = list(Age2ItemData)[1:5]
        packet = {"index": 0, "items": [NetworkItem(item.id, 0, 0, 0) for item in items]}

        ap._handle_received_items(packet)
        self.assertEqual(len(self.ctx.client_status.unlocked_items), len(items))

        self.send(2)
        ap._handle_received_items(packet)
        self.assertEqual(
            len(self.ctx.client_status.unlocked_items),
            len(items),
            "a resync appended a second copy of every item",
        )
        self.send(2)
        self.assertEqual(2, self.sent_items()[0], "the window lost the cursor over the resync")


class TestOneShotSkipping(TestItemDelivery):
    """Filler resources and traps add rather than set, so a replayed stream must not re-send them.

    The window is positional, so they are replaced in place by SKIP_ITEM_ID, not dropped.
    """

    FILLER = Age2ItemData.FILLER_WOOD_SMALL
    TRAP = Age2ItemData.TRAP_WOLOLO
    FLAG = Age2ItemData.FISH_TRAP

    def test_nothing_is_sent_before_the_stored_mark_has_come_back(self) -> None:
        self.reconnect()
        self.unlock(self.TRAP)

        self.send()

        self.assertEqual([], self.sent_items(),
                         "sending before the mark lands is exactly the reconnect trap bug")
        self.assertFalse(self.ctx.item_handler.in_flight())

    def test_a_rewound_cursor_skips_the_one_shots_it_already_paid(self) -> None:
        self.unlock(self.FILLER, self.FLAG, self.TRAP, self.FLAG, self.FILLER, self.TRAP, self.FLAG)
        # The reconnect case: the record survived, the cursor did not. Only the filler at 0
        # and 4 and the trap at 2 can carry a bit; flags are replayable and never spend.
        self.spent((1 << 0) | (1 << 2) | (1 << 4))

        self.send()

        self.assertEqual(
            [Items.SKIP_ITEM_ID, self.FLAG.id, Items.SKIP_ITEM_ID, self.FLAG.id, Items.SKIP_ITEM_ID,
             self.TRAP.id, self.FLAG.id],
            self.sent_window(),
            "one-shots below the mark skip, flags resend, and anything above the mark is real")

    def test_skipping_does_not_shorten_the_window(self) -> None:
        """The game counts entries, so a dropped one would shift every index after it."""
        items = [self.TRAP] * 7
        self.unlock(*items)
        self.spent(0b1111111)

        self.send()

        self.assertEqual([Items.SKIP_ITEM_ID] * 7, self.sent_window())

    def test_forward_delivery_never_skips_anything(self) -> None:
        """The mark only ever reaches the cursor, so a window is always entirely unpaid."""
        items = [self.FILLER, self.TRAP, self.FLAG] * 5
        self.unlock(*items)

        for _ in range(30):
            self.full_tick()

        self.assertEqual([item.id for item in items], self.game.granted,
                         "a first delivery was skipped as though it had already been paid")
        spent = self.ctx.spent_items()
        for index, item in enumerate(items):
            one_shot = item in Items.ONE_SHOT_ITEMS
            self.assertEqual(one_shot, index in spent,
                             f"index {index} ({item.item_name}) should "
                             f"{'be' if one_shot else 'not be'} spent")

    def test_the_mark_follows_the_cursor_and_is_reported_once_per_move(self) -> None:
        reported: list[int] = []
        self.ctx.client_interface.on_item_spent = reported.append
        self.unlock(*[self.FLAG] * 20)

        for _ in range(30):
            self.full_tick()

        self.assertEqual(0, self.ctx.storage_handler.spent_mask(),
                         "flag items are replayable, so none of them is ever spent")
        self.assertEqual([], reported, "nothing was spent, so nothing to report")


class TestStartingResources(TestItemDelivery):
    """Starting resources pay out once per scenario run, and the window is the only path.

    The cursor starts at 0 in every new scenario, so the window replays the whole stream there:
    that is the starting pile. One received mid-scenario lands at the cursor, and a loaded save
    carries its own cursor, so it is handed only what it never saw. There used to be a second path,
    startup.xsdat, and paying both was a double grant.
    """

    WOOD = Age2ItemData.STARTING_WOOD_SMALL
    TC = Age2ItemData.TOWN_CENTER_WOOD
    FLAG = Age2ItemData.FISH_TRAP

    def deliver(self) -> None:
        for _ in range(10):
            self.full_tick()

    def test_a_status_pass_writes_no_startup_pile(self) -> None:
        self.unlock(self.WOOD, self.TC)

        with mock.patch.object(GameClient, "long_sleep", mock.AsyncMock()):
            asyncio.run(GameClient.status_tick(self.ctx))

        self.assertFalse(os.path.exists(self.folder + "startup.xsdat"),
                         "a second path for starting resources pays them twice")

    def test_a_scenario_start_pays_each_starting_resource_once(self) -> None:
        self.unlock(self.WOOD, self.FLAG, self.TC)

        self.deliver()

        self.assertEqual([self.WOOD.id, self.FLAG.id, self.TC.id], self.game.granted)

    def test_one_received_mid_scenario_lands_immediately(self) -> None:
        self.unlock(self.WOOD)
        self.deliver()

        self.unlock(self.TC)
        self.full_tick()

        self.assertEqual([self.WOOD.id, self.TC.id], self.game.granted)

    def test_the_next_scenario_pays_the_whole_pile_again(self) -> None:
        self.unlock(self.WOOD, self.TC)
        self.deliver()

        self.ctx.item_handler.try_flush_from_folder()   # flush_files, on the switch
        self.game = FakeGame()                          # the next scenario has applied nothing
        self.deliver()

        self.assertEqual([self.WOOD.id, self.TC.id], self.game.granted)

    def test_a_loaded_save_is_handed_only_what_it_never_saw(self) -> None:
        self.unlock(self.WOOD, self.TC, self.WOOD)
        self.game.applied_item_count = 2                # the save had applied the first two

        self.deliver()

        self.assertEqual([self.WOOD.id], self.game.granted)

    def test_starting_resources_are_never_marked_spent(self) -> None:
        """Spending one would skip it in the next scenario, which is owed it again."""
        self.unlock(self.WOOD, self.TC)

        self.deliver()

        self.assertEqual(0, self.ctx.storage_handler.spent_mask())


class TestDecodingTheSpentRecord(TestItemDelivery):
    """spent_indices turns the record back into stream positions, the one decode of the mask.

    Everything downstream -- the mercenary handler in particular -- is handed items, not bits.
    """

    def test_bits_name_the_entries_they_sit_over(self) -> None:
        items = [Age2ItemData.FILLER_WOOD_SMALL, Age2ItemData.FISH_TRAP,
                 Age2ItemData.TRAP_WOLOLO]
        self.unlock(*items)
        self.spent((1 << 0) | (1 << 2))

        self.assertEqual({0, 2}, self.ctx.spent_items())

    def test_an_empty_record_names_nothing(self) -> None:
        self.unlock(Age2ItemData.TRAP_WOLOLO)
        self.assertEqual(set(), self.ctx.spent_items())

    def test_a_bit_past_the_received_stream_names_nothing(self) -> None:
        """A record outlives the apsave, so it can carry bits for a stream that is not back yet."""
        self.unlock(Age2ItemData.TRAP_WOLOLO)
        self.ctx.storage_handler.try_save(1 << 40)

        self.assertEqual(set(), self.ctx.spent_items(),
                         "a bit beyond what has been received cannot name an entry")

    def test_duplicates_are_named_once_each(self) -> None:
        """Filler repeats, so the same id can sit at several indices and spend independently."""
        wood = Age2ItemData.FILLER_WOOD_SMALL
        self.unlock(wood, wood, wood)
        self.spent((1 << 0) | (1 << 2))

        self.assertEqual({0, 2}, self.ctx.spent_items())


class TestReconcilingTheSpentRecord(TestItemDelivery):
    """The local record is authoritative for *spent*, the server for *unlocked*.

    A spend the server never stored must not be handed back, so a local record overrules it even
    when it knows less. A union would make "the server is behind" indistinguishable from "the
    server is ahead", and would mean nothing could ever be un-spent.
    """

    def saved(self, spent: int) -> None:
        """A local record, over a stream long enough for it to survive truncation."""
        self.ctx.client_status.unlocked_items[:] = [Age2ItemData.TRAP_WOLOLO] * 16
        self.ctx.storage_handler.try_save(spent)

    def test_no_local_record_adopts_the_server(self) -> None:
        self.reconnect()
        self.ctx.client_status.unlocked_items[:] = [Age2ItemData.TRAP_WOLOLO] * 16
        self.assertEqual(0b101, self.ctx.reconcile_spent(0b101))
        self.assertEqual(0b101, self.ctx.storage_handler.spent_mask())

    def test_the_local_record_wins_over_a_server_that_is_behind(self) -> None:
        self.saved(0b101)
        self.assertEqual(0b101, self.ctx.reconcile_spent(0b001),
                         "a spend the server never stored must not be handed back")

    def test_the_local_record_wins_even_when_it_knows_less(self) -> None:
        self.saved(0b001)
        self.assertEqual(0b001, self.ctx.reconcile_spent(0b101))

    def test_an_empty_record_is_not_a_missing_record(self) -> None:
        """Both are falsy, and confusing them would silently restore every spend."""
        self.saved(0)
        self.assertEqual(0, self.ctx.reconcile_spent(0b101),
                         "a playthrough that has spent nothing still wins")

    def test_bits_past_the_received_stream_are_dropped(self) -> None:
        """A reset or rolled-back server leaves a record describing a playthrough that is gone.

        The stream is append-only, so a bit still inside it really was spent and is kept; a bit
        past the end names nothing now and would name the wrong entry once the stream refilled.
        """
        self.saved((1 << 1) | (1 << 7))
        self.ctx.client_status.unlocked_items[:] = [Age2ItemData.TRAP_WOLOLO] * 3

        self.assertEqual(1 << 1, self.ctx.reconcile_spent(0),
                         "the surviving prefix was discarded, or the stale bit was kept")

    def test_a_reset_to_an_empty_stream_clears_the_record(self) -> None:
        self.saved((1 << 2) | (1 << 9))
        self.ctx.client_status.unlocked_items.clear()

        self.assertEqual(0, self.ctx.reconcile_spent(0))

    def test_a_full_stream_truncates_nothing(self) -> None:
        self.saved((1 << 2) | (1 << 9))

        self.assertEqual((1 << 2) | (1 << 9), self.ctx.reconcile_spent(0))

    def test_reconciling_opens_the_gate_on_sending(self) -> None:
        self.reconnect()
        self.ctx.client_status.unlocked_items[:] = [Age2ItemData.TRAP_WOLOLO] * 16
        self.assertFalse(self.ctx.storage_handler.is_up_to_date())
        self.ctx.reconcile_spent(0)
        self.assertTrue(self.ctx.storage_handler.is_up_to_date())


class TestFlushingWhatWasSent(TestItemDelivery):
    """flush_files deletes items.xsdat on every scenario switch, and on every save/load.

    The handler suppresses a rewrite when what it is about to write is what it already sent. A
    switch that leaves the item index where it was makes those two identical, so unless the
    deletion withdraws the claim the file is gone and never written again: the new scenario is
    handed nothing, while the client keeps arming ReadItems over a file that is not there.
    """

    def test_a_file_deleted_under_the_handler_is_written_again(self) -> None:
        self.unlock(*list(Age2ItemData)[:20])
        self.send()
        first = self.sent_items()
        self.assertNotEqual([], first, "the fixture never wrote a window to begin with")

        self.ctx.item_handler.try_flush_from_folder()
        self.assertEqual([], self.sent_items(), "the fixture did not delete the window")

        self.send()   # same index, same entries: exactly the suppression case

        self.assertEqual(first, self.sent_items(),
                         "nothing was written again after the file was deleted")

    def test_flushing_withdraws_the_claim_on_the_game(self) -> None:
        """in_flight is what arms ReadItems. Leaving it set over a file that is gone has the
        game open nothing, every tick, for the rest of the session."""
        self.unlock(*list(Age2ItemData)[:20])
        self.send()
        self.assertTrue(self.ctx.item_handler.in_flight())

        self.ctx.item_handler.try_flush_from_folder()

        self.assertFalse(self.ctx.item_handler.in_flight())

    def test_a_switch_before_anything_was_applied_still_delivers(self) -> None:
        """The whole path. Scenario A is offered items and applies none of them, so the index
        is still zero when the switch flushes the file and scenario B starts counting from zero.
        """
        items = list(Age2ItemData)[:20]
        self.unlock(*items)
        self.send()
        self.ctx.item_handler.try_flush_from_folder()   # flush_files, on the switch
        self.game = FakeGame()                          # scenario B has applied nothing

        for _ in range(30):
            self.full_tick()

        self.assertEqual([item.id for item in items], self.game.granted,
                         "the scenario switched to was never handed its items")


class TestNamingACopyToSpend(TestItemDelivery):
    """The record is positional, so spending an item by identity has to pick a copy.

    Mercenaries happen to be unique in the pool, but the mask they write is the one the items
    use, where duplicates are ordinary. list.index picks the first copy every time, so it would
    spend the same bit twice and leave the second copy payable forever.
    """

    MERCENARY = Age2ItemData.AP_ATTILA_1_MANGUDAI

    def test_the_first_unpaid_copy_is_the_one_named(self) -> None:
        wood = Age2ItemData.FILLER_WOOD_SMALL
        self.unlock(wood, wood, wood)

        self.assertEqual(0, self.ctx.unspent_index(wood))
        self.assertTrue(self.ctx.storage_handler.mark_spent({0}))
        self.assertEqual(1, self.ctx.unspent_index(wood),
                         "the copy at 0 is paid for, so naming it again would spend nothing")
        self.assertTrue(self.ctx.storage_handler.mark_spent({1}))
        self.assertEqual(2, self.ctx.unspent_index(wood))

    def test_an_item_with_no_unpaid_copy_names_nothing(self) -> None:
        wood = Age2ItemData.FILLER_WOOD_SMALL
        self.unlock(wood)
        self.spent(1 << 0)

        self.assertEqual(-1, self.ctx.unspent_index(wood))

    def test_an_item_that_never_arrived_names_nothing(self) -> None:
        self.unlock(Age2ItemData.FILLER_WOOD_SMALL)

        self.assertEqual(-1, self.ctx.unspent_index(self.MERCENARY))

    def test_recording_a_position_twice_reports_no_change(self) -> None:
        """on_item_spent fires off the return, so a repeated ack must not announce a spend."""
        self.unlock(self.MERCENARY)

        self.assertTrue(self.ctx.storage_handler.mark_spent({0}))
        self.assertFalse(self.ctx.storage_handler.mark_spent({0}))

    def test_recording_nothing_reports_no_change(self) -> None:
        self.unlock(Age2ItemData.FISH_TRAP)

        self.assertFalse(self.ctx.storage_handler.mark_spent(set()))

    def test_clearing_the_record_unpays_every_item(self) -> None:
        """/install full clears both halves: reset_used for mercenaries, the record here."""
        items = [Age2ItemData.FILLER_WOOD_SMALL] * 3
        self.unlock(*items)
        for _ in range(10):
            self.full_tick()
        self.assertNotEqual(0, self.ctx.storage_handler.spent_mask(),
                            "the fixture never paid for anything")

        self.assertTrue(self.ctx.clear_spent_state())

        self.assertEqual(0, self.ctx.storage_handler.spent_mask())
        self.send()   # the scenario restarts, so the same items go out again
        self.assertEqual([item.id for item in items], self.sent_window(),
                         "a cleared record still skipped items as though they were paid for")


class TestMarkingInOnePass(TestItemDelivery):
    """The pass that sees the game take a one-shot marks it and writes the next window.

    Delivered entries sit below the cursor and the window starts at it, so a mark can never change
    an entry in the window being written. Nothing waits on the disk either: the mark lands in
    memory, the server push persists it, and a failed save is retried on the next tick.
    """

    FILLER = Age2ItemData.FILLER_WOOD_SMALL
    TRAP = Age2ItemData.TRAP_WOLOLO
    FLAG = Age2ItemData.FISH_TRAP

    def block_apdata(self) -> None:
        """A file where the folder should be: no record can be written under it."""
        apdata = Path(self._tmp.name, "APData")
        shutil.rmtree(apdata, ignore_errors=True)
        apdata.write_text("in the way", encoding="utf-8")

    def test_one_sync_marks_the_delivered_and_writes_the_window(self) -> None:
        self.unlock(self.FILLER, self.FILLER, self.TRAP)
        self.full_tick()
        self.assertEqual(3, self.game.applied_item_count, "the fixture never got going")
        self.unlock(self.FILLER)

        self.sync(self.game.applied_item_count)

        self.assertEqual(0b111, self.ctx.storage_handler.spent_mask(),
                         "the pass that saw them delivered did not mark them")
        self.assertEqual([3, self.FILLER.id], self.sent_items(),
                         "the next window waited a tick behind the mark")

    def test_an_unwritable_apdata_folder_still_delivers_every_window(self) -> None:
        items = [self.FILLER, self.TRAP, self.FLAG] * 5
        self.block_apdata()

        with self.assertLogs("Client", level="WARNING"):
            for item in items:
                self.unlock(item)
                self.full_tick()

        self.assertEqual([item.id for item in items], self.game.granted,
                         "a failed save held delivery back")
        expected = sum(1 << index for index, item in enumerate(items)
                       if item in Items.ONE_SHOT_ITEMS)
        self.assertEqual(expected, self.ctx.storage_handler.spent_mask(),
                         "a mark was lost because the disk refused it")

    def test_the_record_reaches_disk_once_the_folder_is_writable(self) -> None:
        self.unlock(self.FILLER, self.TRAP)
        self.block_apdata()
        with self.assertLogs("Client", level="WARNING"):
            self.full_tick()
            self.full_tick()

        Path(self._tmp.name, "APData").unlink()
        self.full_tick()

        reread = StorageHandler()
        reread.set_user_folder(self._tmp.name)
        self.assertEqual(0b11, reread.try_load(), "the failed save was never retried")


if __name__ == "__main__":
    unittest.main()
