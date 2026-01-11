import asyncio
import json
import os
import logging
from tkinter import filedialog
from tkinter import *
from multiprocessing import Process
from typing import Optional
from CommonClient import ClientCommandProcessor, CommonContext, get_base_parser, server_loop
from NetUtils import NetworkItem
import Utils
from kvui import GameManager
from ..campaign.CampaignReader import Campaign, Scenario
from ..campaign.ScenarioPatcher import copy_ai, inject_ap
from ..items import Items
from ..locations.Locations import global_location_id
from ..locations.Scenarios import Age2ScenarioData
from .ApGui import Age2Manager
import worlds.age2de.client.GameClient as GameClient
from .. import Age2Settings, Age2World

logger = logging.getLogger("Client")

def set_user_folder(settings: Age2Settings):
    settings.user_folder = settings.user_folder.browse()

class Age2CommandProcessor(ClientCommandProcessor):
    ctx: 'Age2Context'
    
    def _cmd_set_user_folder(self) -> bool:
        """
        Set User Folder: Lets the user assign their local age2de user folder.
        Usually located at:
            "C:/Users/<USER>/Games/Age of Empires 2 DE/<STRING_OF_NUMBERS>/"
        Select the <STRING_OF_NUMBERS> folder as the user folder.
        """
        set_user_folder(self.ctx.settings)
        self.ctx.game_ctx.client_status.user_folder = self.ctx.settings.user_folder
        self.output(f"User folder now assigned to {self.ctx.game_ctx.client_status.user_folder}")
        return True
    
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
    settings = Age2World.settings
    
    def __init__(self, server_address: Optional[str], password: Optional[str]):
        super().__init__(server_address, password)
        self.game_ctx = GameClient.Age2GameContext(True, client_interface=self)
        self.game_ctx.client_status = GameClient.ClientStatus(unlocked_scenarios=[], unlocked_items=[])
        self.game_ctx.client_status.user_folder = self.settings.user_folder
        self.game_ctx.client_status.receieved_messages[0] = "Client Connected!"
        
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
            self.game_ctx.client_status.unlocked_items.append(item_data)
            if received_item.player == self.slot:
                lastAddedMessageId = list(self.game_ctx.client_status.receieved_messages.keys())[-1]
                self.game_ctx.client_status.receieved_messages[lastAddedMessageId + 1] = f"You have found your {item_data.item_name}"
            else:
                lastAddedMessageId = list(self.game_ctx.client_status.receieved_messages.keys())[-1]
                self.game_ctx.client_status.receieved_messages[lastAddedMessageId + 1] = f"{self.player_names[received_item.player]} has found your {item_data.item_name}"
                

def main(connect: Optional[str] = None, password: Optional[str] = None, name: Optional[str] = None):
    Utils.init_logging("Age of Empires II: DE Client")

    async def _main(connect: Optional[str], password: Optional[str], name: Optional[str]):
        parser = get_base_parser()
        args = parser.parse_args()
        ctx = Age2Context(connect, password)

        ctx.auth = name
        ctx.server_task = asyncio.create_task(
            server_loop(ctx), name="ServerLoop")
        Age2Manager.start_ap_ui(ctx)
        await asyncio.sleep(1)

        scn = Age2ScenarioData.AP_ATTILA_1
        scn2 = Age2ScenarioData.AP_ATTILA_2
                
        # copy_ai("C1_Attila_2.aoe2scenario", "C:\\Users\\dmwev\\Games\\Age of Empires 2 DE\\76561199655318799\\resources\\_common\\scenario\\AP_Attila_2.aoe2scenario")
        
        ctx.game_ctx.client_status.unlocked_scenarios = [scn, scn2]

        asyncio.create_task(GameClient.status_loop(ctx.game_ctx))

        await ctx.exit_event.wait()
        ctx.game_ctx.running = False
        ctx.server_address = None

        await ctx.shutdown()

    import colorama

    colorama.init()
    
    asyncio.run(_main(connect, password, name))
    colorama.deinit()