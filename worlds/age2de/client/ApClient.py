import asyncio
import copy
import os
import logging
from typing import ClassVar, Optional
import typing
from CommonClient import ClientCommandProcessor, CommonContext, get_base_parser, server_loop
from NetUtils import ClientStatus, JSONMessagePart, JSONtoTextParser, NetworkItem
import Utils
from ..items import Items
from ..locations.Scenarios import Age2ScenarioData
from ..locations.Campaigns import Age2CampaignData
from .ApGui import Age2Manager
import worlds.age2de.client.GameClient as GameClient
from .. import Age2Settings, Age2World

logger = logging.getLogger("Client")


def set_user_folder(settings: Age2Settings):
    settings.user_folder = settings.user_folder.browse()

class Age2CommandProcessor(ClientCommandProcessor):
    ctx: 'Age2Context'
    
    def _cmd_connect_to_game(self) -> None:
        """
        Connect to Game: Starts up the game-to-client connection.
        """
        started: bool = self.ctx.try_startup_game_connection()
        if started:
            self.output(f"Game loop started.")
        self.output(f"Game loop already is running.")
    
    def _cmd_set_user_folder(self) -> None:
        """
        Set User Folder: Lets the user assign their local age2de user folder.
        Usually located at:
            "C:/Users/<USER>/Games/Age of Empires 2 DE/<STRING_OF_NUMBERS>/"
        Select the <STRING_OF_NUMBERS> folder as the user folder.
        """
        set_user_folder(self.ctx.settings)
        self.ctx.game_ctx.update_game_user_folder(self.ctx.game_ctx, self.ctx.settings.user_folder)
        self.output(f"User folder now assigned to {self.ctx.game_ctx.client_status.user_folder}")
    
    def _cmd_refresh(self) -> None:
        """
        Refresh: disconnects and reconnects to the campaign or scenario. Usually only needed when quickly switching between campaigns or standalone scenarios.
        """
        self.output(f"Disconnecting from {self.ctx.game_ctx.campaign_handler.active_file}")
        self.ctx.game_ctx.campaign_handler.active_file = None
    
    def _cmd_debug(self, key: str) -> bool:
        """Debug: prints current value of age2 game client"""
        parts = key.split('.')
        current: dict|list|object = self.ctx.game_ctx
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
    settings: ClassVar[Age2Settings] = Age2World.settings
    scenario_completion_key: str
    
    def __init__(self, server_address: Optional[str], password: Optional[str]):
        super().__init__(server_address, password)
        self.game_ctx = GameClient.Age2GameContext(client_interface=self)
        self.game_ctx.update_game_user_folder(self.settings.user_folder)
        self.age2_json_text_parser = Age2JSONtoTextParser(self)
        self.scenario_completion_key = f"{self.team}_{self.slot}_scenario_complete"
        
    async def server_auth(self, password_requested: bool = False) -> None:
        self.game = Age2World.game
        if password_requested and not self.password:
           await super(Age2Context, self).server_auth(password_requested)
        await self.get_username()
        await self.send_connect()
    
    def on_print_json(self, args):
        if (not self.is_uninteresting_item_send(args)) and (not self.is_connection_change(args)) and not self.is_echoed_chat(args):
            text = self.age2_json_text_parser(copy.deepcopy(args["data"]))
            if not text.startswith(
                    self.player_names[self.slot] + ":"):  # TODO: Remove string heuristic in the future.
                self.game_ctx.message_handler.add_message(text)
        return super().on_print_json(args)
    
    def on_package(self, cmd: str, args: dict) -> None:
        if cmd == "Connected":
            self._handle_connected()
                
        if cmd == "ReceivedItems":
            self._handle_received_items(args)
            
        if cmd == "SetReply":
            self._handle_set_reply(args)

    def _handle_connected(self):
        self.game_ctx.flush_files()
        self.try_startup_game_connection()
        Utils.async_start(self.send_msgs([
        {
            "cmd": "Set",
            "key": self.scenario_completion_key,
            "default": 0,
            "want_reply": True,
            "operations": [
                {"operation": "default", "value": 0}
            ]
        }
        ]))
            
        self.set_notify(self.scenario_completion_key)

    def _handle_received_items(self, args: dict) -> None:
        received_items: list[NetworkItem] = args["items"]
        for received_item in received_items:
            item_data = Items.ID_TO_ITEM[received_item.item]
            if item_data.item_name == "Victory":
                Utils.async_start(self.send_msgs([{"cmd": "StatusUpdate", "status": ClientStatus.CLIENT_GOAL}]))
            if item_data.type_data is Items.Campaign:
                self.game_ctx.campaign_handler.unlock_campaign(item_data.type.vanilla_campaign)
            if item_data.type_data is Items.ProgressiveScenario:
                self.game_ctx.campaign_handler.unlock_progressive_scenario(item_data.type.vanilla_campaign)
            self.game_ctx.client_status.unlocked_items.append(item_data)

    def _handle_set_reply(self, args: dict) -> None:
        for (scenario_data, managed_scenario) in self.game_ctx.campaign_handler.scenarios.items():
            completed: int = self.stored_data.get(self.scenario_completion_key)
            managed_scenario.completed = completed & (1 << scenario_data.completion_bit) != 0

    def on_scenario_completion(self, scenario: Age2ScenarioData) -> None:
        Utils.async_start(self.send_msgs([
            {
                "cmd": "Set",
                "key": self.scenario_completion_key,
                "default": False,
                "want_reply": True,
                "operations": [
                    {"operation": "or", "value": 1 << scenario.completion_bit}
                ]
            }
        ]))

    def on_location_received(self, location_ids: list[int]) -> None:
        if location_ids is not None:
            Utils.async_start(self.send_msgs([{
                "cmd": "LocationChecks",
                "locations": [location_id for location_id in location_ids],
            }]))

    def try_startup_game_connection(self) -> bool:
        if self.game_ctx.game_loop is None or self.game_ctx.game_loop.done():
            self.game_ctx.game_loop = asyncio.create_task(GameClient.status_loop(self.game_ctx))
            return True
        return False

class Age2JSONtoTextParser(JSONtoTextParser):
    color: str = "white"
    color_codes = {
        # not exact color names, close enough but decent looking
        "black": "<GREY>",
        "red": "<RED>",
        "green": "<GREEN>",
        "yellow": "<YELLOW>",
        "blue": "<BLUE>",
        "magenta": "<PURPLE>",
        "cyan": "<AQUA>",
        "slateblue": "<BLUE>",
        "plum": "<PURPLE>",
        "salmon": "<ORANGE>",
        "white": "",
        "orange": "<ORANGE>",
    }
    
    def __call__(self, input_object: typing.List[JSONMessagePart]) -> str:
        text = super().__call__(input_object)
        return self.color_codes[self.color] + text
    
    def _handle_color(self, node: JSONMessagePart):
        if node["type"] == "item_id" or node["type"] == "hint_status":
            self.color = node["color"].split(";")[0]
        return self._handle_text(node)

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
        
        await ctx.exit_event.wait()
        ctx.game_ctx.running = False
        ctx.game_ctx.campaign_handler.deactivate_scenario()
        ctx.game_ctx.flush_files()
        ctx.server_address = None
        ctx.game_ctx.game_loop.cancel("Shutting down game loop")

        await ctx.shutdown()

    import colorama

    colorama.init()
    
    asyncio.run(_main(connect, password, name))
    colorama.deinit()