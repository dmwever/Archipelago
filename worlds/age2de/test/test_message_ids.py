"""The game shows a message only if its id is greater than the scenario's saved `lastMessageId`,
and every packet reports that id back. The client numbers its own messages, so it must keep every
id it writes above the id the game last showed: after a client restart against a save, after a
scenario switch, and on every confirm. A message the game skipped is renumbered and resent, never
dropped.

`FakeGame` copies `ReadMessages` in AP.xs: it reads messages.xsdat only while AP.xsdat says
"Send Messages", shows each message whose id beats `lastMessageId`, and raises it.
"""

import os
import tempfile
import unittest

from ..campaign import XsdatFile
from ..client.handlers.MessageHandler import MessageHandler


class FakeGame:
    def __init__(self, last_message_id: int = -1) -> None:
        self.last_message_id = last_message_id
        self.shown: list[tuple[int, str]] = []

    def read_messages(self, folder: str) -> None:
        for message_id, text in read_message_file(folder):
            if self.last_message_id < message_id:
                self.last_message_id = message_id
                self.shown.append((message_id, text))


def read_message_file(folder: str) -> list[tuple[int, str]]:
    path = folder + "messages.xsdat"
    if not os.path.exists(path):
        return []
    with open(path, "rb") as fp:
        return [(XsdatFile.read_int(fp), XsdatFile.read_string(fp).decode())
                for _ in range(XsdatFile.read_int(fp))]


class MessageIdTestBase(unittest.TestCase):
    def setUp(self) -> None:
        self._folder = tempfile.TemporaryDirectory()
        self.folder = self._folder.name + "/"
        self.addCleanup(self._folder.cleanup)
        self.handler = MessageHandler()
        self.handler.set_user_folder(self.folder)

    def tick(self, game: FakeGame, game_reads: bool = True) -> None:
        """One status tick: write, let the game read if told to, then read its packet."""
        self.handler.try_write_to_folder()
        if game_reads and self.handler.is_message_sending():
            game.read_messages(self.folder)
        self.handler.confirm_messages_recieved(game.last_message_id)

    def settle(self, game: FakeGame, ticks: int = 5) -> None:
        for _ in range(ticks):
            self.tick(game)

    def switch_scenario(self) -> None:
        """GameClient.flush_files on a scenario switch."""
        self.handler.try_flush_from_folder()

    def written_ids(self) -> list[int]:
        return [message_id for message_id, _ in read_message_file(self.folder)]


class TestScenarioRoundTrip(MessageIdTestBase):
    def test_return_to_a_shows_the_next_message_and_never_replays_b(self) -> None:
        a = FakeGame()
        for n in range(21):
            self.handler.add_message(f"a{n}")
        self.settle(a)
        self.assertEqual([i for i, _ in a.shown], list(range(21)))

        self.switch_scenario()
        b = FakeGame()
        self.handler.add_message("Client Connected!")
        for n in range(4):
            self.handler.add_message(f"b{n}")
        self.settle(b)
        self.assertEqual(b.shown, [(21, "Client Connected!"), (22, "b0"), (23, "b1"),
                                   (24, "b2"), (25, "b3")])

        self.switch_scenario()
        a.shown.clear()
        self.handler.add_message("back in a")
        self.settle(a)
        self.assertEqual(a.shown, [(26, "back in a")])


class TestRestartAgainstSave(MessageIdTestBase):
    def test_first_messages_go_out_above_the_saved_id(self) -> None:
        game = FakeGame(last_message_id=40)
        self.handler.add_message("Client Connected!")
        self.handler.add_message("Received Loom")
        self.settle(game)
        self.assertEqual(game.shown, [(41, "Client Connected!"), (42, "Received Loom")])

    def test_nothing_is_cleared_before_the_game_shows_it(self) -> None:
        game = FakeGame(last_message_id=40)
        self.handler.add_message("Client Connected!")
        self.handler.add_message("Received Loom")
        for _ in range(3):
            self.tick(game, game_reads=False)
        self.assertTrue(self.handler.is_message_sending())
        self.assertEqual(self.written_ids(), [41, 42])

        self.tick(game)
        self.assertEqual([i for i, _ in game.shown], [41, 42])
        self.settle(game)
        self.assertFalse(self.handler.is_message_sending())
        self.assertEqual([i for i, _ in game.shown], [41, 42])


class TestOffByOne(MessageIdTestBase):
    def test_next_message_after_confirm_is_one_above_the_game(self) -> None:
        game = FakeGame(last_message_id=7)
        self.handler.confirm_messages_recieved(7)
        self.handler.add_message("next")
        self.settle(game)
        self.assertEqual(game.shown, [(8, "next")])


class TestCounterNeverGoesDown(MessageIdTestBase):
    def test_a_lower_game_id_does_not_lower_the_counter(self) -> None:
        game = FakeGame()
        for n in range(10):
            self.handler.add_message(f"m{n}")
        self.settle(game)

        self.switch_scenario()
        fresh = FakeGame(last_message_id=3)
        self.handler.add_message("after")
        self.settle(fresh)
        self.assertEqual(fresh.shown, [(10, "after")])


class TestRenumberingInFlight(MessageIdTestBase):
    def test_a_batch_the_game_skipped_is_resent_above_its_id_in_order(self) -> None:
        a = FakeGame()
        self.handler.add_message("a0")
        self.settle(a)

        # Switch to a save that has already shown 100 before the batch reaches it.
        self.handler.add_message("one")
        self.handler.add_message("two")
        self.handler.try_write_to_folder()
        self.assertEqual(self.written_ids(), [1, 2])
        self.switch_scenario()
        b = FakeGame(last_message_id=100)
        self.handler.add_message("three")
        self.settle(b)
        self.assertEqual(b.shown, [(101, "one"), (102, "two"), (103, "three")])

    def test_a_batch_partly_below_the_game_is_renumbered_whole(self) -> None:
        a = FakeGame()
        self.handler.add_message("a0")
        self.settle(a)

        self.handler.add_message("one")
        self.handler.add_message("two")
        self.handler.try_write_to_folder()
        self.switch_scenario()
        b = FakeGame(last_message_id=1)
        self.tick(b, game_reads=False)
        self.settle(b)
        self.assertEqual(b.shown, [(2, "one"), (3, "two")])

    def test_a_batch_ending_on_the_new_saves_id_is_not_taken_as_shown(self) -> None:
        a = FakeGame()
        self.handler.add_message("a0")
        self.settle(a)

        self.handler.add_message("one")
        self.handler.add_message("two")
        self.handler.try_write_to_folder()
        self.assertEqual(self.written_ids(), [1, 2])
        self.switch_scenario()
        b = FakeGame(last_message_id=2)
        self.tick(b, game_reads=False)
        self.settle(b)
        self.assertEqual(b.shown, [(3, "one"), (4, "two")])


if __name__ == "__main__":
    unittest.main()
