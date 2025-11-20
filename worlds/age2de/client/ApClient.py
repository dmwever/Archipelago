import asyncio
from typing import Optional
from CommonClient import ClientCommandProcessor, CommonContext, get_base_parser, server_loop
import Utils
from kvui import GameManager
from .ApGui import Age2Manager
from .GameClient import Age2GameContext
from .. import Age2World, logger

class Age2CommandProcessor(ClientCommandProcessor):
    ctx: 'Age2Context'
    
    def _cmd_debug(self, key: str) -> bool:
        """Debug: prints current value of age2 game client"""
        parts = key.split('.')
        current: dict|list|object = self.ctx.game_client
        for part in parts:
            if part.isnumeric():
                part = int(part)
            if isinstance(current, dict):
                current = current[part]
            elif isinstance(current, list):
                current = current[int(part)]
            else:
                current = getattr(current, part)
        logger.info(current)
        return True


class Age2Context(CommonContext):
    game = Age2World.game
    command_processor = Age2CommandProcessor
    game_ctx = Age2GameContext
    
    def __init__(self, server_address: Optional[str], password: Optional[str]):
        super().__init__(server_address, password)
        
    async def server_auth(self, password_requested: bool = False) -> None:
        self.game = Age2World.game
        if password_requested and not self.password:
           await super(Age2Context, self).server_auth(password_requested)
        await self.get_username()
        await self.send_connect() 
    
    def on_package(self, cmd: str, args: dict) -> None:
        if cmd == "Connected":
            self._handle_connected(args)
        elif cmd == "ReceivedItems":
            self._handle_received_items(args)
            
    def _handle_connected(self, args: dict) -> None:
        self.generator_version = (args["slot_data"]["version_major"], args["slot_data"]["version_minor"])
        
    def _handle_received_items(self, args: dict):
        pass
    
    
def main(connect: Optional[str] = None, password: Optional[str] = None, name: Optional[str] = None):
    Utils.init_logging("Age of Empires II: DE Client")

    async def _main(connect: Optional[str], password: Optional[str], name: Optional[str]):
        parser = get_base_parser()
        parser.add_argument("age2de_folder", default="", type=str, nargs="?", help="Path to age2de folder")
        args = parser.parse_args()
        ctx = Age2Context(connect, password)

        # if args.age2de_folder:
        #     parent_dir: str = os.path.dirname(args.age2de_folder)
        #     target_name: str = os.path.basename(args.age2de_folder)
        #     target_path: str = os.path.join(parent_dir, target_name)
        #     if not os.path.exists(target_path):
        #         os.makedirs(target_path, exist_ok=True)
        #         logger.info("Extracting campaign files to %s", target_path)
        #         with zipfile.ZipFile(args.age2de_folder, "r") as zip_ref:
        #             for member in zip_ref.namelist():
        #                 zip_ref.extract(member, target_path)
        ctx.auth = name
        ctx.server_task = asyncio.create_task(
            server_loop(ctx), name="ServerLoop")
        Age2Manager.start_ap_ui(ctx)
        await asyncio.sleep(1)

        await ctx.exit_event.wait()
        ctx.server_address = None

        await ctx.shutdown()

    import colorama

    colorama.init()
    asyncio.run(_main(connect, password, name))
    colorama.deinit()
