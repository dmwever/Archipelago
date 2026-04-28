import asyncio
import logging
from dataclasses import dataclass, field
from enum import Enum
import os
import struct
from typing import List, Protocol

from worlds.age2de.client.handlers.BuildingHandler import BuildingHandler
from worlds.age2de.locations.Buildings import Age2BuildingData
from ..locations.Scenarios import Age2ScenarioData


from .handlers.CampaignHandler import CampaignHandler
from .handlers.MessageHandler import MessageHandler

from ..campaign import XsdatFile
from ..items import Items
from ..items.Items import Age2ItemData, ScenarioItem
from ..locations.Campaigns import Age2CampaignData
from worlds.age2de.locations import Scenarios

logger = logging.getLogger("Client")

AGE2_USER_PROFILE = "/profile/"
AP_VERSION = 6.5
WORLD_ID = 2

class APClientInterface(Protocol):
    def on_scenario_completion(self, scenario_id: Age2ScenarioData):
        pass
    
    def on_location_received(self, location_ids: list[int]):
        """Called when a new location is received"""
        pass
    def fetch_locations_collected(self, location_status: dict[int, int], new_scenario_id: int):
        """Called when a new location is received"""
        pass


class DefaultClientInterface:
    def on_scenario_completion(self, scenario_id: Age2ScenarioData) -> None:
        pass
    
    def on_location_received(self, location_ids: list[int]) -> None:
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
    completed: bool = False
    scenario_id: int = 0
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
        self.completed = XsdatFile.read_bool(fp)
        self.scenario_id = XsdatFile.read_int(fp)
        XsdatFile.skip_int(fp, 30)
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

class Age2GameContext:
    running: bool = True
    game_loop: asyncio.Task[None] = None
    paused: bool = False
    packet_repeat_count: int = 0
    current_packet: Age2Packet = Age2Packet()
    client_status: ClientStatus = None
    campaign_handler: CampaignHandler = CampaignHandler([campaign for campaign in Age2CampaignData])
    building_handler: BuildingHandler = BuildingHandler([building for building in Age2BuildingData])
    message_handler: MessageHandler = MessageHandler()
    client_interface: APClientInterface = field(default_factory=DefaultClientInterface)

    def __init__(self, client_interface):
        self.running = True
        self.client_interface = client_interface
        self.client_status = ClientStatus(unlocked_items=[])
        self.message_handler.add_message("Client Connected!")

    def update_game_user_folder(self, folder: str):
        self.client_status.user_folder = folder
        self.message_handler.set_user_folder(self.user_folder())
        self.building_handler.set_user_folder(self.user_folder())
        self.campaign_handler.set_user_folder(self.user_folder())

    def read_packet(self) -> Age2Packet:
        try:
            with open(self.user_folder() + self.campaign_handler.active_file.data.campaign.xsdat_read_name, "rb") as fp:
                return Age2Packet(fp)
        except Exception as ex:
            print(ex)
            return Age2Packet()

    def update_packet(self, new_pkt: Age2Packet) -> PacketStatus:
        status: PacketStatus
        
        if (new_pkt.ap_version != AP_VERSION):
            status = PacketStatus.WRONG_VERSION
        elif (new_pkt.world_id != WORLD_ID):
            status = PacketStatus.WRONG_WORLD
        elif (not new_pkt.active):
            status = PacketStatus.INACTIVE
        elif (self.current_packet.current_ping_id == new_pkt.current_ping_id):
            status = PacketStatus.REPEAT
        elif (self.current_packet.latest_message_id != new_pkt.latest_message_id):
            status = PacketStatus.UPDATE
        elif (len(self.current_packet.location_ids) != 0):
            status = PacketStatus.UPDATE
        else:
            status = PacketStatus.ACTIVE
        self.current_packet = new_pkt
        return status

    def ack_locations(self) -> None:
        try:
            with open(self.user_folder() + "locations.xsdat", "wb") as fp:
                XsdatFile.write_int(fp, len(self.current_packet.location_ids))
                for location_id in self.current_packet.location_ids:
                    XsdatFile.write_int(fp, location_id)
        except Exception as ex:
            print(ex)

    def ack_items(self) -> None:
        for item in self.current_packet.item_ids:
            if item != -1 and self.client_status.acked_items < len(self.client_status.unlocked_items):
                self.client_status.acked_items += 1

    def send_items(self) -> None:
        num_items = len(self.client_status.unlocked_items) - self.client_status.acked_items
        if num_items > 12:
            num_items = 12
        if num_items > 0:
            try:
                with open(self.user_folder() + "items.xsdat", "wb") as fp:
                    XsdatFile.write_int(fp, num_items)
                    for item in self.client_status.unlocked_items[self.client_status.acked_items:self.client_status.acked_items+num_items]:
                        XsdatFile.write_int(fp, item.id)
            except Exception as ex:
                print(ex)

    def sync_starting_resources(self) -> None:
        item_ids: list[int] = []
        for item in list(filter(lambda x: x in Items.CATEGORY_TO_ITEMS[Items.StartingResources], self.client_status.unlocked_items)):
            item_ids.append(item.id)
        for item in list(filter(lambda x: x in Items.CATEGORY_TO_ITEMS[Items.TCResources], self.client_status.unlocked_items)):
            item_ids.append(item.id)
        try:
            with open(self.user_folder() + "startup.xsdat", "wb") as fp:
                for id in item_ids:
                    XsdatFile.write_int(fp, id)
        except Exception as ex:
            print(ex)

    def user_folder(self):
        return self.client_status.user_folder + AGE2_USER_PROFILE
            
    def free_items(self) -> None:
        try:
            with open(self.user_folder() + "free_items.xsdat", "wb") as fp:
                for item in self.current_packet.item_ids:
                    if item != -1:
                        XsdatFile.write_int(fp, item)
        except Exception as ex:
            print(ex)

    def flush_files(self) -> None:
        try:
            self.message_handler.try_flush_from_folder()
            self.campaign_handler.try_flush_from_folder()
            
            if os.path.exists(self.user_folder() + "AP.xsdat"):
                os.remove(self.user_folder() + "AP.xsdat")
            if os.path.exists(self.user_folder() + "items.xsdat"):
                os.remove(self.user_folder() + "items.xsdat")
            if os.path.exists(self.user_folder() + "free_items.xsdat"):
                os.remove(self.user_folder() + "free_items.xsdat")
            if os.path.exists(self.user_folder() + "locations.xsdat"):
                os.remove(self.user_folder() + "locations.xsdat")
            if os.path.exists(self.user_folder() + "startup.xsdat"):
                os.remove(self.user_folder() + "startup.xsdat")
            if os.path.exists(self.user_folder() + "buildings.xsdat"):
                os.remove(self.user_folder() + "buildings.xsdat")
        except Exception as ex:
            print(ex)

    def ping_game(self) -> None:
        try:
            with open(self.user_folder() + "AP.xsdat", "wb") as fp:
                XsdatFile.write_int(fp, self.current_packet.current_ping_id)
                XsdatFile.write_float(fp, AP_VERSION)
                XsdatFile.write_int(fp, WORLD_ID)
                XsdatFile.write_bool(fp, self.client_status.acked_items < len(self.client_status.unlocked_items)) # Send Items
                XsdatFile.write_bool(fp, not all(x == -1 for x in self.current_packet.item_ids)) # Free items
                XsdatFile.write_bool(fp, len(self.current_packet.location_ids) != 0) # Free Locations
                XsdatFile.write_bool(fp, False) # Send Units
                XsdatFile.write_bool(fp, self.message_handler.is_message_sending()) # Send Messages
                XsdatFile.write_bool(fp, self.campaign_handler.active_file.completed)
        except Exception as ex:
            print(ex)

async def short_sleep() -> None:
    await asyncio.sleep(0.5)


async def long_sleep() -> None:
    await asyncio.sleep(2)


async def status_loop(ctx: Age2GameContext):
    while ctx.running:
        # Check all unlocked scenarios every 2 seconds to find active scenario.
        if not ctx.campaign_handler.active_file:
            logger.info("Searching for active scenario.")
            ctx.campaign_handler.find_active_campaign()
            if not ctx.campaign_handler.has_active_scenario():
                ctx.campaign_handler.find_active_scenario()
                if not ctx.campaign_handler.has_active_scenario():
                    logger.info("No active scenario found. Make sure the game is running and the scenario is unpaused.")
                    await long_sleep()
                    continue
                else:
                    logger.info("Connected!")
            else:
                logger.info("Connected!")
        
        # Check all unlocked scenarios every 2.5 seconds after scenario stops updating packet in case user has switched scenarios.
        if ctx.paused and ctx.packet_repeat_count % 5 == 0:
            logger.info("Searching for an active scenario. The game may be paused.")
            ctx.campaign_handler.find_active_campaign()
            if not ctx.campaign_handler.has_active_scenario():
                ctx.campaign_handler.find_active_scenario()
                if not ctx.campaign_handler.has_active_scenario():
                    await short_sleep()
                    continue
        
        packet: Age2Packet
        try:
            packet = ctx.read_packet()
        except Exception as ex:
            logger.exception(ex)
            await long_sleep()
            continue
        
        packetStatus = ctx.update_packet(packet)
        
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
            ctx.client_interface.on_location_received(ctx.current_packet.location_ids)
            ctx.ack_locations()
            
        if packetStatus == PacketStatus.ACTIVE:
            pass
        
        if (any(x != -1 for x in ctx.current_packet.item_ids)):
            ctx.ack_items()
        
        if (ctx.client_status.acked_items < len(ctx.client_status.unlocked_items)):
            ctx.send_items()
            ctx.sync_starting_resources()
            ctx.campaign_handler.sync_scenario_items(list(set(ctx.client_status.unlocked_items).intersection(Items.CATEGORY_TO_ITEMS[ScenarioItem])))
        
        if ctx.message_handler.is_packet_up_to_date(packet.latest_message_id):
            ctx.message_handler.confirm_messages_recieved(packet.latest_message_id)
        
        if packet.completed == True and not ctx.campaign_handler.is_active_scenario_complete():
            ctx.campaign_handler.complete_active_scenario()
            ctx.client_interface.on_scenario_completion(Scenarios.scenario_from_id[packet.scenario_id])
        
        ctx.building_handler.try_sync_buildings(ctx.client_status.unlocked_items)
        ctx.message_handler.try_write_to_folder()
        ctx.free_items()
        ctx.ping_game()
        
        await short_sleep()