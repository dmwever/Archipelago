import asyncio
import copy
import os
import logging
from typing import ClassVar, Optional
import typing
from CommonClient import ClientCommandProcessor, CommonContext, get_base_parser, server_loop
from NetUtils import ClientStatus, JSONMessagePart, JSONtoTextParser, NetworkItem
import Utils
from ..generation import Identity, WorldVersion
from .handlers.InstallHandler import InstallError
from ..items import Items
from ..locations.Scenarios import Age2ScenarioData
from ..locations.Campaigns import Age2CampaignData
from .ApGui import Age2Manager
from .DataStorage import DataStorage
import worlds.age2de.client.GameClient as GameClient
from .. import Age2Settings, Age2World

logger = logging.getLogger("Client")


def set_user_folder(settings: Age2Settings):
    settings.user_folder = settings.user_folder.browse()


class Age2CommandProcessor(ClientCommandProcessor):
    ctx: 'Age2Context'
    
    def _cmd_set_user_folder(self) -> None:
        """
        Set User Folder: Lets the user assign their local age2de user folder.
        Usually located at:
            "C:/Users/<USER>/Games/Age of Empires 2 DE/<STRING_OF_NUMBERS>/"
        Select the <STRING_OF_NUMBERS> folder as the user folder.
        """
        set_user_folder(self.ctx.settings)
        if self.ctx.game_ctx != None:
            self.ctx.game_ctx.update_game_user_folder(self.ctx.settings.user_folder)
        self.output(f"User folder now assigned to {self.ctx.settings.user_folder}")

    def _cmd_install(self) -> None:
        """
        Install: Sets your Age2 install up for this seed and slot.

        Writes a seed-tagged copy of each campaign you enabled, plus SlotData.xs.
        Run it once per seed, after connecting.
        """
        ctx = self.ctx
        status = ctx.game_ctx.client_status
        if not status.tag or status.slot_id < 0:
            self.output("Connect to your multiworld first, so the install knows your seed and slot.")
            return
        if not ctx.settings.user_folder:
            self.output("Set your Age2 user folder first with /set_user_folder.")
            return
        if not ctx.seed_is_compatible():
            self.output(WorldVersion.describe(ctx.seed_world_version, Age2World.world_version))
            self.output("Nothing was written.")
            return

        campaigns = ctx.game_ctx.campaign_handler.included_campaigns()
        if not campaigns:
            self.output("This slot has no campaigns to install.")
            return

        raw_name = ctx.player_names[ctx.slot]
        if status.player_name != raw_name:
            self.output(f'Your name "{raw_name}" contains characters that cannot be used in a '
                        f'file name. Your campaigns are installed as "{status.player_name}".')

        try:
            ctx.game_ctx.install_handler.setup(
                campaigns, status.slot_id, status.tag, status.player_name)
            written = ctx.game_ctx.install_handler.install()
        except InstallError as ex:
            self.output(str(ex))
            return

        for path in written:
            self.output(f"Wrote {path}")
        self.output(f"Installed slot {status.slot_id}, seed tag {status.tag}.")

    def _cmd_mercenaries(self) -> None:
        """
        Mercenaries: Lists this seed's mercenaries and where each one stands.

        Missing has not been found, Unlocked is waiting behind the pavilion,
        In-Pavilion is selectable right now, and Used has been spent.
        """
        ctx = self.ctx
        if ctx.data_storage is None:
            self.output("Connect to your multiworld first, so the client knows this seed.")
            return
        handler = ctx.game_ctx.mercenary_handler
        for mercenary in ctx.data_storage.mercenaries:
            self.output(f"{handler.status(mercenary):<12}{mercenary.item_name}")

    def _cmd_scenarios(self) -> None:
        """
        Scenarios: Lists this seed's scenarios and where each one stands.

        Missing means its campaign has not been found, Unlocked means the campaign
        is held but this chapter is not reachable yet, Available is selectable now,
        Active is the one being played, and Completed is finished.
        """
        ctx = self.ctx
        if ctx.data_storage is None:
            self.output("Connect to your multiworld first, so the client knows this seed.")
            return
        handler = ctx.game_ctx.campaign_handler
        for scenario in ctx.data_storage.scenarios:
            status = handler.status(scenario)
            self.output(f"{status:<16}{scenario.campaign.campaign_name}: {scenario.scenario_name}")


class Age2Context(CommonContext):
    game = Age2World.game
    command_processor = Age2CommandProcessor
    game_ctx: GameClient.Age2GameContext
    items_handling = 0b111
    settings: ClassVar[Age2Settings] = Age2World.settings
    scenario_completion_key: str
    mercenaries_used_key: str
    data_storage: DataStorage = None
    installed_seed_name: str = ''
    seed_world_version = WorldVersion.UNKNOWN
    
    def __init__(self, server_address: Optional[str], password: Optional[str]):
        super().__init__(server_address, password)
        self.age2_json_text_parser = Age2JSONtoTextParser(self)
        self.game_ctx = GameClient.Age2GameContext(client_interface=self)
        
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
        if cmd == "RoomInfo":
            self.installed_seed_name = args.get("seed_name", "")

        if cmd == "Connected":
            self._handle_connected(args['slot_data'])
                
        if cmd == "ReceivedItems":
            self._handle_received_items(args)
            
        if cmd == "SetReply":
            self._handle_set_reply(args)

    def _handle_connected(self, slot_data):
        self.scenario_completion_key = f"{self.team}_{self.slot}_scenario_complete"
        self.mercenaries_used_key = f"{self.team}_{self.slot}_mercenaries_used"
        self.seed_world_version = WorldVersion.parse(slot_data.get(WorldVersion.SLOT_DATA_KEY))
        if not self.seed_is_compatible():
            logger.warning(WorldVersion.describe(self.seed_world_version, Age2World.world_version))
        self.seed_name = self.installed_seed_name
        tag = Identity.seed_tag(self.installed_seed_name, self.slot)
        logger.info("Playthrough tag for slot %s: %s", self.slot, tag)
        player_name = Identity.sanitize_player(self.player_names[self.slot])
        self.game_ctx.connect(
            self.checked_locations, slot_data, self.settings.user_folder, self.slot, tag,
            player_name)
        self.data_storage = DataStorage(self.game_ctx.campaign_handler.included_campaigns())
        Utils.async_start(self.send_msgs([
        {
            "cmd": "Set",
            "key": self.scenario_completion_key,
            "default": 0,
            "want_reply": True,
            "operations": [
                {"operation": "default", "value": 0}
            ]
        },
        {
            "cmd": "Set",
            "key": self.mercenaries_used_key,
            "default": 0,
            "want_reply": True,
            "operations": [
                {"operation": "default", "value": 0}
            ]
        }
        ]))

        self.set_notify(self.scenario_completion_key)
        self.set_notify(self.mercenaries_used_key)

    def seed_is_compatible(self) -> bool:
        return WorldVersion.compatible(self.seed_world_version, Age2World.world_version)

    def _handle_received_items(self, args: dict) -> None:
        received_items: list[NetworkItem] = args["items"]
        if args.get("index", -1) == 0:
            self.game_ctx.client_status.unlocked_items.clear()
        for received_item in received_items:
            if received_item.item not in Items.ID_TO_ITEM:
                logger.warning("Ignoring unknown item id %s from the server.", received_item.item)
                continue
            item_data = Items.ID_TO_ITEM[received_item.item]
            if item_data.item_name == "Victory":
                Utils.async_start(self.send_msgs([{"cmd": "StatusUpdate", "status": ClientStatus.CLIENT_GOAL}]))
            self.game_ctx.client_status.unlocked_items.append(item_data)
        status = self.game_ctx.client_status
        if status.acked_items > len(status.unlocked_items):
            status.acked_items = len(status.unlocked_items)

    def _handle_set_reply(self, args: dict) -> None:
        if args["key"] == self.scenario_completion_key:
            self._handle_scenario_completion_reply()
        if args["key"] == self.mercenaries_used_key:
            self._handle_mercenaries_used_reply()

    def _handle_scenario_completion_reply(self) -> None:
        completed: int = self.stored_data.get(self.scenario_completion_key)
        finished = self.data_storage.completed_scenarios(completed)
        for (scenario_data, managed_scenario) in self.game_ctx.campaign_handler.scenarios.items():
            managed_scenario.completed = scenario_data in finished

    def _handle_mercenaries_used_reply(self) -> None:
        used: int = self.stored_data.get(self.mercenaries_used_key)
        for mercenary in self.data_storage.used_mercenaries(used):
            self.game_ctx.mercenary_handler.use_mercenary(mercenary)
            
    def on_scenario_completion(self, scenario: Age2ScenarioData) -> None:
        Utils.async_start(self.send_msgs([
            {
                "cmd": "Set",
                "key": self.scenario_completion_key,
                "default": 0,
                "want_reply": True,
                "operations": [
                    {"operation": "or", "value": 1 << self.data_storage.scenario_bit(scenario)}
                ]
            }
        ]))

    def on_mercenary_used(self, mercenary: Items.Age2ItemData) -> None:
        Utils.async_start(self.send_msgs([
            {
                "cmd": "Set",
                "key": self.mercenaries_used_key,
                "default": 0,
                "want_reply": True,
                "operations": [
                    {"operation": "or", "value": 1 << self.data_storage.mercenary_bit(mercenary)}
                ]
            }
        ]))

    def on_location_received(self, location_ids: list[int]) -> None:
        if location_ids is not None:
            Utils.async_start(self.send_msgs([{
                "cmd": "LocationChecks",
                "locations": [location_id for location_id in location_ids],
            }]))

    def on_goal(self) -> None:
        Utils.async_start(self.send_msgs([{"cmd": "StatusUpdate", "status": ClientStatus.CLIENT_GOAL}]))
    
    async def connection_closed(self):
        await super().connection_closed()
        await self.game_ctx.disconnect()

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
        await ctx.game_ctx.disconnect()
        
        await ctx.shutdown()

    import colorama

    colorama.init()
    
    asyncio.run(_main(connect, password, name))
    colorama.deinit()