"""disconnect awaited game_loop with no bound.

status_loop can block on a file the game still holds. Unbounded, that stalls disconnect and
everything queued behind it - connection_closed calls disconnect from server_loop's finally, so
a stuck loop took reconnect with it.
"""
import asyncio
import unittest
from unittest import mock

from ..client.GameClient import Age2GameContext, DefaultClientInterface


class TestDisconnectBound(unittest.TestCase):
    def context(self) -> Age2GameContext:
        ctx = Age2GameContext(DefaultClientInterface())
        ctx.client_status.user_folder = ''   # skip flush_files, which wants a real folder
        return ctx

    def test_a_stuck_game_loop_does_not_block_disconnect(self) -> None:
        async def scenario() -> bool:
            ctx = self.context()
            ctx.game_loop = asyncio.ensure_future(asyncio.Event().wait())
            with mock.patch("worlds.age2de.client.GameClient.GAME_LOOP_SHUTDOWN_SECONDS", 0.05):
                await ctx.disconnect()
            await asyncio.sleep(0)
            return ctx.game_loop.cancelled()

        self.assertTrue(asyncio.run(scenario()),
                        "disconnect waited on the game loop forever")

    def test_a_finished_game_loop_is_awaited_normally(self) -> None:
        async def scenario() -> None:
            ctx = self.context()

            async def done() -> None:
                return None

            ctx.game_loop = asyncio.ensure_future(done())
            await ctx.disconnect()
            self.assertFalse(ctx.game_loop.cancelled())

        asyncio.run(scenario())

    def test_a_raising_game_loop_still_disconnects(self) -> None:
        async def scenario() -> None:
            ctx = self.context()

            async def boom() -> None:
                raise RuntimeError("status loop fell over")

            ctx.game_loop = asyncio.ensure_future(boom())
            await ctx.disconnect()   # must not propagate
            self.assertFalse(ctx.running)

        asyncio.run(scenario())


if __name__ == "__main__":
    unittest.main()
