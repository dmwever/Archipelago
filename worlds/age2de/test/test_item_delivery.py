"""Item delivery over items.xsdat.

The window is addressed, not positional: it carries the cursor it was written for, and the game
applies it only when that matches its own, all of it or none. Re-reading a window it has already
applied is a no-op, because the base no longer matches.

That makes the cursor the whole protocol. The game owns it, a loaded save rewinds it, and the
client streams from wherever the packet says it is. FakeGame below stands in for AP.xs's ReadItems
so a full delivery can be driven without the game running.
"""

import os
import struct
import tempfile
import unittest

from ..campaign import XsdatFile
from ..client.GameClient import (
    AGE2_USER_PROFILE,
    Age2GameContext,
    DefaultClientInterface,
)
from ..items import Items
from ..items.Items import Age2ItemData

ITEM_WINDOW = 12


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
        # These exercise the window, not the gate on it. TestOneShotSkipping covers that.
        self.ctx.client_status.record_known = True
        self.folder = self.ctx.profile_folder()
        self.game = FakeGame()

    # -- helpers ---------------------------------------------------------

    def unlock(self, *items: Age2ItemData) -> None:
        self.ctx.client_status.unlocked_items.extend(items)

    def full_tick(self) -> None:
        """The item phase of status_loop, in the same order, plus the game's response."""
        self.sync(self.game.applied_item_count)
        # ping_game arms ReadItems only while a window is outstanding.
        if self.ctx.item_handler.in_flight():
            self.game.read_items(self.folder)

    def sync(self, applied: int = 0) -> None:
        """One delivery pass, gated and recorded the way status_loop does it.

        The handler reports what it paid out and the context records it -- the same shape as the
        mercenary path, where the handler never touches the record or the server itself.
        """
        if not self.ctx.client_status.record_known:
            return
        delivered = self.ctx.item_handler.try_sync_items(
            self.ctx.client_status.unlocked_items, applied, self.ctx.spent_items())
        if self.ctx.mark_items_spent(delivered):
            self.ctx.client_interface.on_item_spent(self.ctx.client_status.spent_mask)

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
        self.unlock(*list(Age2ItemData)[:100])

        self.send()

        written = self.sent_items()
        self.assertEqual(0, written[0], "the window is addressed to the cursor it starts at")
        self.assertEqual(Items.ITEM_WINDOW, len(written) - 1)

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
            if self.ctx.item_handler.current_item_index() >= len(items):
                break
        self.assertEqual(len(items), self.game.applied_item_count)

        self.game.applied_item_count = 5
        self.game.granted.clear()
        for _ in range(10):
            self.full_tick()
            if self.ctx.item_handler.current_item_index() >= len(items):
                break

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
            if self.ctx.item_handler.current_item_index() >= len(items):
                break

        self.assertEqual(self.game.ignored, [], "the game discarded ids it was sent")
        self.assertEqual(
            self.game.granted,
            [item.id for item in items],
            "not every unlocked item reached the game",
        )
        self.assertEqual(self.ctx.item_handler.current_item_index(), len(items))

    def test_duplicate_ids_in_one_window(self) -> None:
        """Filler resources repeat; acking must count them, not collapse them."""
        wood = Age2ItemData.FILLER_WOOD_SMALL
        self.unlock(*([wood] * 5))

        for _ in range(20):
            self.full_tick()
            if self.ctx.item_handler.current_item_index() >= 5:
                break

        self.assertEqual(self.game.granted, [wood.id] * 5)
        self.assertEqual(self.ctx.item_handler.current_item_index(), 5)

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
        self.assertEqual(self.ctx.item_handler.current_item_index(), 2)


class TestOneShotSkipping(TestItemDelivery):
    """Filler resources and traps add rather than set, so a replayed stream must not re-send them.

    The window is positional, so they are replaced in place by SKIP_ITEM_ID, not dropped.
    """

    FILLER = Age2ItemData.FILLER_WOOD_SMALL
    TRAP = Age2ItemData.TRAP_WOLOLO
    FLAG = Age2ItemData.FISH_TRAP

    def test_nothing_is_sent_before_the_stored_mark_has_come_back(self) -> None:
        self.ctx.client_status.record_known = False
        self.unlock(self.TRAP)

        self.send()

        self.assertEqual([], self.sent_items(),
                         "sending before the mark lands is exactly the reconnect trap bug")
        self.assertFalse(self.ctx.item_handler.in_flight())

    def test_a_rewound_cursor_skips_the_one_shots_it_already_paid(self) -> None:
        self.unlock(self.FILLER, self.FLAG, self.TRAP, self.FLAG, self.FILLER, self.TRAP, self.FLAG)
        # The reconnect case: the record survived, the cursor did not. Only the filler at 0
        # and 4 and the trap at 2 can carry a bit; flags are replayable and never spend.
        self.ctx.client_status.spent_mask = (1 << 0) | (1 << 2) | (1 << 4)

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
        self.ctx.client_status.spent_mask = 0b1111111

        self.send()

        self.assertEqual([Items.SKIP_ITEM_ID] * 7, self.sent_window())

    def test_forward_delivery_never_skips_anything(self) -> None:
        """The mark only ever reaches the cursor, so a window is always entirely unpaid."""
        items = [self.FILLER, self.TRAP, self.FLAG] * 5
        self.unlock(*items)

        for _ in range(30):
            self.full_tick()
            if self.ctx.item_handler.current_item_index() >= len(items):
                break

        self.assertEqual([item.id for item in items], self.game.granted,
                         "a first delivery was skipped as though it had already been paid")
        spent = self.ctx.client_status.spent_mask
        for index, item in enumerate(items):
            one_shot = item in Items.ONE_SHOT_ITEMS
            self.assertEqual(one_shot, bool((spent >> index) & 1),
                             f"index {index} ({item.item_name}) should "
                             f"{'be' if one_shot else 'not be'} spent")

    def test_the_mark_follows_the_cursor_and_is_reported_once_per_move(self) -> None:
        reported: list[int] = []
        self.ctx.client_interface.on_item_spent = reported.append
        self.unlock(*[self.FLAG] * 20)

        for _ in range(30):
            self.full_tick()
            if self.ctx.item_handler.current_item_index() >= 20:
                break

        self.assertEqual(0, self.ctx.client_status.spent_mask,
                         "flag items are replayable, so none of them is ever spent")
        self.assertEqual([], reported, "nothing was spent, so nothing to report")


class TestDecodingTheSpentRecord(TestItemDelivery):
    """spent_indices turns the record back into stream positions, the one decode of the mask.

    Everything downstream -- the mercenary handler in particular -- is handed items, not bits.
    """

    def test_bits_name_the_entries_they_sit_over(self) -> None:
        items = [Age2ItemData.FILLER_WOOD_SMALL, Age2ItemData.FISH_TRAP,
                 Age2ItemData.TRAP_WOLOLO]
        self.unlock(*items)
        self.ctx.client_status.spent_mask = (1 << 0) | (1 << 2)

        self.assertEqual({0, 2}, self.ctx.spent_items())

    def test_an_empty_record_names_nothing(self) -> None:
        self.unlock(Age2ItemData.TRAP_WOLOLO)
        self.assertEqual(set(), self.ctx.spent_items())

    def test_a_bit_past_the_received_stream_names_nothing(self) -> None:
        """A record outlives the apsave, so it can carry bits for a stream that is not back yet."""
        self.unlock(Age2ItemData.TRAP_WOLOLO)
        self.ctx.client_status.spent_mask = 1 << 40

        self.assertEqual(set(), self.ctx.spent_items(),
                         "a bit beyond what has been received cannot name an entry")

    def test_duplicates_are_named_once_each(self) -> None:
        """Filler repeats, so the same id can sit at several indices and spend independently."""
        wood = Age2ItemData.FILLER_WOOD_SMALL
        self.unlock(wood, wood, wood)
        self.ctx.client_status.spent_mask = (1 << 0) | (1 << 2)

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
        self.ctx.client_status.unlocked_items[:] = [Age2ItemData.TRAP_WOLOLO] * 16
        self.assertEqual(0b101, self.ctx.reconcile_spent(0b101))
        self.assertEqual(0b101, self.ctx.client_status.spent_mask)

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
        self.ctx.client_status.unlocked_items[:] = [Age2ItemData.TRAP_WOLOLO] * 16
        self.ctx.client_status.record_known = False
        self.ctx.reconcile_spent(0)
        self.assertTrue(self.ctx.client_status.record_known)


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
            if self.ctx.item_handler.current_item_index() >= len(items):
                break

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
        self.assertTrue(self.ctx.mark_items_spent({0}))
        self.assertEqual(1, self.ctx.unspent_index(wood),
                         "the copy at 0 is paid for, so naming it again would spend nothing")
        self.assertTrue(self.ctx.mark_items_spent({1}))
        self.assertEqual(2, self.ctx.unspent_index(wood))

    def test_an_item_with_no_unpaid_copy_names_nothing(self) -> None:
        wood = Age2ItemData.FILLER_WOOD_SMALL
        self.unlock(wood)
        self.ctx.client_status.spent_mask = 1 << 0

        self.assertEqual(-1, self.ctx.unspent_index(wood))

    def test_an_item_that_never_arrived_names_nothing(self) -> None:
        self.unlock(Age2ItemData.FILLER_WOOD_SMALL)

        self.assertEqual(-1, self.ctx.unspent_index(self.MERCENARY))

    def test_recording_a_position_twice_reports_no_change(self) -> None:
        """on_item_spent fires off the return, so a repeated ack must not announce a spend."""
        self.unlock(self.MERCENARY)

        self.assertTrue(self.ctx.mark_items_spent({0}))
        self.assertFalse(self.ctx.mark_items_spent({0}))

    def test_recording_nothing_reports_no_change(self) -> None:
        self.unlock(Age2ItemData.FISH_TRAP)

        self.assertFalse(self.ctx.mark_items_spent(set()))

    def test_clearing_the_record_unpays_every_item(self) -> None:
        """/install full clears both halves: reset_used for mercenaries, reset_delivery here."""
        items = [Age2ItemData.FILLER_WOOD_SMALL] * 3
        self.unlock(*items)
        for _ in range(10):
            self.full_tick()
            if self.ctx.item_handler.current_item_index() >= len(items):
                break
        self.assertNotEqual(0, self.ctx.client_status.spent_mask,
                            "the fixture never paid for anything")

        self.assertTrue(self.ctx.clear_spent_state())

        self.assertEqual(0, self.ctx.client_status.spent_mask)
        self.send()   # the scenario restarts, so the same items go out again
        self.assertEqual([item.id for item in items], self.sent_window(),
                         "a cleared record still skipped items as though they were paid for")


class TestRecordingBeforeSkipping(TestItemDelivery):
    """A one-shot is skipped on the strength of the record, so the record has to exist first.

    The pass that notices the game took a one-shot is the pass that would write a file skipping
    it. Writing both at once stakes the skip on a save that has not happened, and a save that
    fails then costs the item outright -- the game never sees it again.
    """

    def test_a_pass_that_pays_out_writes_nothing(self) -> None:
        items = [Age2ItemData.FILLER_WOOD_SMALL] * 12 + [Age2ItemData.FISH_TRAP] * 3
        self.unlock(*items)
        self.full_tick()
        self.assertEqual(12, self.game.applied_item_count, "the fixture never got going")

        self.sync(self.game.applied_item_count)   # the pass that pays out the twelve

        self.assertEqual(0, self.sent_items()[0],
                         "a file went out before the spends it skips were recorded")
        self.assertFalse(self.ctx.item_handler.in_flight())

        self.sync(self.game.applied_item_count)   # now the record carries them

        self.assertEqual(12, self.sent_items()[0], "the tail never went out")

    def test_a_spend_that_did_not_reach_disk_is_not_claimed(self) -> None:
        items = [Age2ItemData.FILLER_WOOD_SMALL] * 3
        self.unlock(*items)
        self.full_tick()
        self.assertEqual(3, self.game.applied_item_count)

        saved = self.ctx.storage_handler.try_save
        self.ctx.storage_handler.try_save = lambda spent: False
        self.sync(self.game.applied_item_count)

        self.assertEqual(0, self.ctx.client_status.spent_mask,
                         "the mask moved past a record that is not on disk")

        self.ctx.storage_handler.try_save = saved
        self.sync(self.game.applied_item_count)

        self.assertEqual(0b111, self.ctx.client_status.spent_mask,
                         "the pass after the failure never tried again")


if __name__ == "__main__":
    unittest.main()
