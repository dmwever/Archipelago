"""One bad tick must not end the loop.

status_tick works off a packet the game wrote, so an id this apworld does not know -- a newer
install, a half-written file -- arrives as an exception rather than a value. Nothing restarts the
loop short of a reconnect, so an unguarded tick means the client goes quiet and stays quiet.
"""

import asyncio
import unittest
from unittest import mock

from ..client import GameClient
from ..client.GameClient import Age2GameContext, DefaultClientInterface


class TestTheLoopSurvivesABadTick(unittest.TestCase):
    def context(self) -> Age2GameContext:
        ctx = Age2GameContext(DefaultClientInterface())
        ctx.client_status.user_folder = ''   # skip flush_files, which wants a real folder
        ctx.running = True
        return ctx

    def test_a_raising_tick_is_logged_and_the_loop_goes_on(self) -> None:
        ctx = self.context()
        ticks: list[int] = []

        async def tick(_ctx: Age2GameContext) -> None:
            ticks.append(len(ticks))
            if len(ticks) == 1:
                raise KeyError(4021)   # the shape of an unknown mercenary id
            ctx.running = False

        async def scenario() -> None:
            with mock.patch.object(GameClient, "status_tick", tick), \
                 mock.patch.object(GameClient, "long_sleep", lambda: asyncio.sleep(0)):
                with self.assertLogs("Client", level="ERROR"):
                    await GameClient.status_loop(ctx)

        asyncio.run(scenario())

        self.assertEqual(2, len(ticks), "the loop ended on the first bad tick")

    def test_a_clean_tick_is_not_logged(self) -> None:
        ctx = self.context()

        async def tick(_ctx: Age2GameContext) -> None:
            ctx.running = False

        async def scenario() -> None:
            with mock.patch.object(GameClient, "status_tick", tick):
                await GameClient.status_loop(ctx)

        with mock.patch.object(GameClient.logger, "exception") as logged:
            asyncio.run(scenario())

        logged.assert_not_called()


if __name__ == "__main__":
    unittest.main()
