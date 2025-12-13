import asyncio
from multiprocessing import Process
from typing import Optional
from CommonClient import ClientCommandProcessor, CommonContext, get_base_parser, server_loop
from NetUtils import NetworkItem
import Utils
from kvui import GameManager
from worlds.age2de.campaign.CampaignReader import Campaign, Scenario
from worlds.age2de.campaign.ScenarioPatcher import copy_ai, inject_ap
from worlds.age2de.items import Items
from worlds.age2de.locations.Locations import global_location_id
from worlds.age2de.locations.Scenarios import Age2ScenarioData
from .ApGui import Age2Manager
import worlds.age2de.client.GameClient as GameClient
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
    game_ctx = GameClient.Age2GameContext
    items_handling = 0b111
    
    def __init__(self, server_address: Optional[str], password: Optional[str]):
        super().__init__(server_address, password)
        self.comm_ctx = GameClient.Age2GameContext(True, client_interface=self)
        
    async def server_auth(self, password_requested: bool = False) -> None:
        self.game = Age2World.game
        if password_requested and not self.password:
           await super(Age2Context, self).server_auth(password_requested)
        await self.get_username()
        await self.send_connect() 
    
    def on_package(self, cmd: str, args: dict) -> None:
        if cmd == "ReceivedItems":
            self._handle_received_items(args)
    
    def on_location_received(self, scenario_id: int, location_ids: list[int]) -> None:
        logger.info(f"Found location {scenario_id}:{','.join(map(str, location_ids))}")
        if location_ids is not None:
            Utils.async_start(self.send_msgs([{
                "cmd": "LocationChecks",
                "locations": [global_location_id(scenario_id, location_id) for location_id in location_ids],
            }]))
    
    def _handle_received_items(self, args: dict) -> None:
        received_items: list[NetworkItem] = args["items"]
        for received_item in received_items:
            item_data = Items.ID_TO_ITEM[received_item.item]
            self.game_ctx.unlocked_items.append(item_data)
    
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

        scn = Age2ScenarioData.AP_ATTILA_2

        # copy_ai("C1_Attila_2.aoe2scenario", "C:\\Users\\dmwev\\Games\\Age of Empires 2 DE\\76561199655318799\\resources\\_common\\scenario\\AP_Attila_2.aoe2scenario")
        
        ctx.comm_ctx.unlocked_scenarios = [scn]
        
        asyncio.create_task(GameClient.status_loop(ctx.comm_ctx))

        await ctx.exit_event.wait()
        ctx.comm_ctx.running = False
        ctx.server_address = None

        await ctx.shutdown()

    import colorama

    colorama.init()
    
    asyncio.run(_main(connect, password, name))
    colorama.deinit()