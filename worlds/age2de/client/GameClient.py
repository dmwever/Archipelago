import asyncio
import logging
from dataclasses import dataclass, field
from enum import Enum
import os
import struct
from typing import List, Protocol


from .handlers.CampaignHandler import CampaignHandler
from .handlers.MessageHandler import MessageHandler

from ..campaign import XsdatFile
from ..items import Items
from ..items.Items import Age2ItemData, ScenarioItem
from ..locations.Campaigns import Age2CampaignData

logger = logging.getLogger("Client")

AGE2_USER_PROFILE = "/profile/"
AP_VERSION = 6.5
WORLD_ID = 2

class APClientInterface(Protocol):
    def on_location_received(self, scenario_id: int, location_ids: list[int]):
        """Called when a new location is received"""
        pass
    def fetch_locations_collected(self, location_status: dict[int, int], new_scenario_id: int):
        """Called when a new location is received"""
        pass


class DefaultClientInterface:
    def on_location_received(self, mission_id: int, location_ids: list[int]) -> None:
        pass

    def fetch_locations_collected(self, location_status: dict[int, int], new_mission_id: int) -> None:
        for k in location_status:
            location_status[k] = 0


class Age2Packet:
    active: bool = 0
    current_ping_id: int = -1
    ap_version: float = 0.0
    world_id: int = -1
    latest_message_id: int = -1
    item_ids = [-1 for _ in range(12)]
    location_ids: List[int]
    
    def __init__(self, fp = None):
        self.location_ids = []
        if not fp:
            return
        self.active = XsdatFile.read_bool(fp)
        self.current_ping_id = XsdatFile.read_int(fp)
        self.ap_version = XsdatFile.read_float(fp)
        self.world_id = XsdatFile.read_int(fp)
        self.latest_message_id = XsdatFile.read_int(fp)
        for num in range(len(self.item_ids)):
            self.item_ids[num] = XsdatFile.read_int(fp)
        XsdatFile.skip_int(fp, 31)
        while True:
            data = fp.read(4)
            if not data:
                break
            s = struct.unpack("<i", data)
            self.location_ids.append(s[0])

class PacketStatus(Enum):
    ACTIVE = 0
    UPDATE = 1
    REPEAT = 2
    INACTIVE = 3
    WRONG_VERSION = 4
    WRONG_WORLD = 5
    ERROR = 6

@dataclass
class ClientStatus:
    unlocked_items: list[Age2ItemData] = field(default_factory=list[Age2ItemData])
    acked_items: int = 0
    user_folder: str = ''

@dataclass
class Age2GameContext:
    running: bool = True
    game_loop: asyncio.Task[None] = None
    paused: bool = False
    packet_repeat_count: int = 0
    current_packet: Age2Packet = Age2Packet()
    client_status: ClientStatus = None
    campaign_handler: CampaignHandler = CampaignHandler([Age2CampaignData.ATTILA])
    message_handler: MessageHandler = MessageHandler()
    client_interface: APClientInterface = field(default_factory=DefaultClientInterface)

def update_game_user_folder(ctx: Age2GameContext, folder: str):
    ctx.client_status.user_folder = folder
    ctx.message_handler.set_user_folder(user_folder(ctx))
    ctx.campaign_handler.set_user_folder(user_folder(ctx))

def read_packet(ctx: Age2GameContext) -> Age2Packet:
    try:
        with open(user_folder(ctx) + ctx.campaign_handler.active_scenario.data.xsdat_read_name, "rb") as fp:
            return Age2Packet(fp)
    except Exception as ex:
        print(ex)
        return Age2Packet()

def update_packet(ctx: Age2GameContext, new_pkt: Age2Packet) -> PacketStatus:
    status: PacketStatus
    
    if (new_pkt.ap_version != AP_VERSION):
        status = PacketStatus.WRONG_VERSION
    elif (new_pkt.world_id != WORLD_ID):
        status = PacketStatus.WRONG_WORLD
    elif (not new_pkt.active):
        status = PacketStatus.INACTIVE
    elif (ctx.current_packet.current_ping_id == new_pkt.current_ping_id):
        status = PacketStatus.REPEAT
    elif (ctx.current_packet.latest_message_id != new_pkt.latest_message_id):
        status = PacketStatus.UPDATE
    elif (len(ctx.current_packet.location_ids) != 0):
        status = PacketStatus.UPDATE
    else:
        status = PacketStatus.ACTIVE
    ctx.current_packet = new_pkt
    return status

def ack_locations(ctx: Age2GameContext) -> None:
    try:
        with open(user_folder(ctx) + "locations.xsdat", "wb") as fp:
            XsdatFile.write_int(fp, len(ctx.current_packet.location_ids))
            for location_id in ctx.current_packet.location_ids:
                XsdatFile.write_int(fp, location_id)
    except Exception as ex:
        print(ex)

def ack_items(ctx: Age2GameContext) -> None:
    for item in ctx.current_packet.item_ids:
        if item != -1 and ctx.client_status.acked_items < len(ctx.client_status.unlocked_items):
            ctx.client_status.acked_items += 1

def send_items(ctx: Age2GameContext) -> None:
    num_items = len(ctx.client_status.unlocked_items) - ctx.client_status.acked_items
    if num_items > 12:
        num_items = 12
    if num_items > 0:
        try:
            with open(user_folder(ctx) + "items.xsdat", "wb") as fp:
                XsdatFile.write_int(fp, num_items)
                for item in ctx.client_status.unlocked_items[ctx.client_status.acked_items:ctx.client_status.acked_items+num_items]:
                    XsdatFile.write_int(fp, item.id)
        except Exception as ex:
            print(ex)

def sync_starting_resources(ctx: Age2GameContext) -> None:
    item_ids: list[int] = []
    for item in list(filter(lambda x: x in Items.CATEGORY_TO_ITEMS[Items.StartingResources], ctx.client_status.unlocked_items)):
        item_ids.append(item.id)
    for item in list(filter(lambda x: x in Items.CATEGORY_TO_ITEMS[Items.TCResources], ctx.client_status.unlocked_items)):
        item_ids.append(item.id)
    try:
        with open(user_folder(ctx) + "startup.xsdat", "wb") as fp:
            for id in item_ids:
                XsdatFile.write_int(fp, id)
    except Exception as ex:
        print(ex)

def user_folder(ctx: Age2GameContext):
    return ctx.client_status.user_folder + AGE2_USER_PROFILE
        
def free_items(ctx: Age2GameContext) -> None:
    try:
        with open(user_folder(ctx) + "free_items.xsdat", "wb") as fp:
            for item in ctx.current_packet.item_ids:
                if item != -1:
                    XsdatFile.write_int(fp, item)
    except Exception as ex:
        print(ex)

def flush_files(ctx: Age2GameContext) -> None:
    try:
        ctx.message_handler.try_flush_from_folder()
        ctx.campaign_handler.try_flush_from_folder()
        
        if os.path.exists(user_folder(ctx) + "AP.xsdat"):
            os.remove(user_folder(ctx) + "AP.xsdat")
        if os.path.exists(user_folder(ctx) + "items.xsdat"):
            os.remove(user_folder(ctx) + "items.xsdat")
        if os.path.exists(user_folder(ctx) + "free_items.xsdat"):
            os.remove(user_folder(ctx) + "free_items.xsdat")
        if os.path.exists(user_folder(ctx) + "locations.xsdat"):
            os.remove(user_folder(ctx) + "locations.xsdat")
        if os.path.exists(user_folder(ctx) + "startup.xsdat"):
            os.remove(user_folder(ctx) + "startup.xsdat")
    except Exception as ex:
        print(ex)

def ping_game(ctx: Age2GameContext) -> None:
    try:
        with open(user_folder(ctx) + "AP.xsdat", "wb") as fp:
            XsdatFile.write_int(fp, ctx.current_packet.current_ping_id)
            XsdatFile.write_float(fp, AP_VERSION)
            XsdatFile.write_int(fp, WORLD_ID)
            XsdatFile.write_bool(fp, ctx.client_status.acked_items < len(ctx.client_status.unlocked_items)) # Send Items
            XsdatFile.write_bool(fp, not all(x == -1 for x in ctx.current_packet.item_ids)) # Free items
            XsdatFile.write_bool(fp, len(ctx.current_packet.location_ids) != 0) # Free Locations
            XsdatFile.write_bool(fp, False) # Send Units
            XsdatFile.write_bool(fp, ctx.message_handler.is_message_sending()) # Send Messages
    except Exception as ex:
        print(ex)

async def short_sleep() -> None:
    await asyncio.sleep(0.5)


async def long_sleep() -> None:
    await asyncio.sleep(2)


async def status_loop(ctx: Age2GameContext):
    while ctx.running:
        # Check all unlocked scenarios every 2 seconds to find active scenario.
        if not ctx.campaign_handler.active_scenario:
            logger.info("Searching for active scenario.")
            scn = ctx.campaign_handler.find_active_scenario()
            if not ctx.campaign_handler.has_active_scenario():
                logger.info("No active scenario found. Make sure the game is running and the scenario is unpaused.")
                await long_sleep()
                continue
        
        # Check all unlocked scenarios every 2.5 seconds after scenario stops updating packet in case user has switched scenarios.
        if ctx.paused and ctx.packet_repeat_count % 5 == 0:
            logger.info("Searching for an active scenario. The game may be paused.")
            scn = ctx.campaign_handler.find_active_scenario()
            if not ctx.campaign_handler.has_active_scenario():
                await short_sleep()
                continue
        
        packet: Age2Packet
        try:
            packet = read_packet(ctx)
        except Exception as ex:
            logger.exception(ex)
            await long_sleep()
            continue
        
        packetStatus = update_packet(ctx, packet)
        
        if packetStatus == PacketStatus.REPEAT:
            ctx.packet_repeat_count += 1
        
            if ctx.packet_repeat_count == 10:
                logger.info("The current scenario has stopped sending signals for 5 seconds. The game may be paused.")
                ctx.paused = True
            
            if ctx.packet_repeat_count == 120:
                logger.warning("The current scenario has stopped sending signals for 60 seconds. The scenario has been disconnected.")
                ctx.campaign_handler.deactivate_scenario()
                ctx.paused = False
                await long_sleep()
                continue
            
            await short_sleep()
            continue
        else:
            ctx.packet_repeat_count = 0
            ctx.paused = False
            
        if packetStatus == PacketStatus.INACTIVE:
            logger.info("The Current Scenario is no longer active.")
            ctx.campaign_handler.deactivate_scenario()
            await long_sleep()
            continue
        if packetStatus == PacketStatus.WRONG_VERSION:
            logger.warning("The Scenario is expecting a different version of the AP Client.")
            ctx.campaign_handler.deactivate_scenario()
            await long_sleep()
            continue
        if packetStatus == PacketStatus.WRONG_WORLD:
            logger.warning("The Scenario is expecting a different world ID.")
            ctx.campaign_handler.deactivate_scenario()
            await long_sleep()
            continue
        if packetStatus == PacketStatus.UPDATE:
            ctx.client_interface.on_location_received(ctx.campaign_handler.active_scenario.data.value, ctx.current_packet.location_ids)
            ack_locations(ctx)
            
        if packetStatus == PacketStatus.ACTIVE:
            pass
        
        if (any(x != -1 for x in ctx.current_packet.item_ids)):
            ack_items(ctx)
        
        if (ctx.client_status.acked_items < len(ctx.client_status.unlocked_items)):
            send_items(ctx)
            sync_starting_resources(ctx)
            ctx.campaign_handler.sync_scenario_items(list(set(ctx.client_status.unlocked_items).intersection(Items.CATEGORY_TO_ITEMS[ScenarioItem])))
        
        if ctx.message_handler.is_packet_up_to_date(packet.latest_message_id):
            ctx.message_handler.confirm_messages_recieved(packet.latest_message_id)
            
        ctx.message_handler.try_write_to_folder()
        free_items(ctx)
        ping_game(ctx)
        
        await short_sleep()