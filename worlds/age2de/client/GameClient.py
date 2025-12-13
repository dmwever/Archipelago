import asyncio
from asyncio.log import logger
from dataclasses import dataclass, field
from enum import Enum
import os
import struct
from typing import List, Protocol

from worlds.age2de.campaign import XsdatReader
from worlds.age2de.items.Items import Age2Item
from worlds.age2de.locations.Scenarios import Age2ScenarioData

AGE2_USER_PROFILE = os.path.join(os.environ["USERPROFILE"], "Games\\Age of Empires 2 DE\\76561199655318799\\profile\\")
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
        self.active = XsdatReader.read_bool(fp)
        self.current_ping_id = XsdatReader.read_int(fp)
        self.ap_version = XsdatReader.read_float(fp)
        self.world_id = XsdatReader.read_int(fp)
        self.latest_message_id = XsdatReader.read_int(fp)
        for num in range(len(self.item_ids)):
            self.item_ids[num] = XsdatReader.read_int(fp)
        XsdatReader.skip_int(fp, 31)
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
class Age2GameContext:
    running: bool = True
    paused: bool = False
    packet_repeat_count: int = 0
    current_packet: Age2Packet = Age2Packet()
    client_interface: APClientInterface = field(default_factory=DefaultClientInterface)
    unlocked_scenarios: list[Age2ScenarioData] = field(default_factory=list[Age2ScenarioData])
    unlocked_items: list[Age2Item] = field(default_factory=list[Age2Item])
    acked_items: list[Age2Item] = field(default_factory=list[Age2Item])
    current_scenario: Age2ScenarioData = None

def find_active_scenario(ctx: Age2GameContext) -> Age2ScenarioData:
    for scenario in ctx.unlocked_scenarios:
        try:
            with open(AGE2_USER_PROFILE + scenario.xsdat_name, "rb") as fp:
                active = fp.peek(1)[:1]
                if (active != b'\x00'):
                    return scenario
                else:
                    print("Not active")
        except:
            pass
    return None

def deactivate_scenario(scn: Age2ScenarioData) -> bool:
    try:
        with open(AGE2_USER_PROFILE + scn.xsdat_name, "wb") as fp:
            fp.write(struct.pack("<?", False))
    except Exception as ex:
        logger.exception(ex)
        print(f"{scn.fileName} unsuccessfully deactivated. .xsdat file may have been locked.")

def read_packet(scn: Age2ScenarioData) -> Age2Packet:
    try:
        with open(AGE2_USER_PROFILE + scn.xsdat_name, "rb") as fp:
            return Age2Packet(fp)
    except Exception as ex:
        logger.exception(ex)
        print(f"Age2Packet not properly opened. Sent from {scn.name}")
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

async def short_sleep() -> None:
    await asyncio.sleep(0.25)
    await asyncio.sleep(0.25)


async def long_sleep() -> None:
    # Note(mm): One big sleep messes with the standalone stdout reader
    # 2s
    await asyncio.sleep(0.2)
    await asyncio.sleep(0.2)
    await asyncio.sleep(0.2)
    await asyncio.sleep(0.2)
    await asyncio.sleep(0.2)
    await asyncio.sleep(0.2)
    await asyncio.sleep(0.2)
    await asyncio.sleep(0.2)
    await asyncio.sleep(0.2)
    await asyncio.sleep(0.2)


async def status_loop(ctx: Age2GameContext):
    while ctx.running:
        # Check all unlocked scenarios every 2 seconds to find active scenario.
        if not ctx.current_scenario:
            scn = find_active_scenario(ctx)
            if not scn:
                print("No active scenario found. Make sure the game is running and the scenario is unpaused.")
                await long_sleep()
                continue
            ctx.current_scenario = scn
        
        # Check all unlocked scenarios every 2.5 seconds after scenario stops updating packet in case user has switched scenarios.
        if ctx.paused and ctx.packet_repeat_count % 5 == 0:
            scn = find_active_scenario(ctx)
            if not scn:
                print("No active scenario found. Make sure the game is running and the scenario is unpaused.")
                await short_sleep()
                continue
            if scn != ctx.current_scenario:
                ctx.current_scenario = scn
        
        packet: Age2Packet
        try:
            packet = read_packet(ctx.current_scenario)
        except Exception as ex:
            logger.exception(ex)
            await long_sleep()
            continue
        
        packetStatus = update_packet(ctx, packet)
        
        if packetStatus == PacketStatus.REPEAT:
            ctx.packet_repeat_count += 1
            print("REPEAT")
            print(ctx.packet_repeat_count)
        
            if ctx.packet_repeat_count == 10:
                print("The Current scenario has been paused or disconnected. Checking additional scenarios for active flag.")
                ctx.paused = True
            
            if ctx.packet_repeat_count == 120:
                print("The Current scenario has stopped sending signals. Deactivating Scenario.")
                deactivate_scenario(ctx.current_scenario)
                ctx.current_scenario = None
                ctx.paused = False
                await long_sleep()
                continue
            
            await short_sleep()
            continue
        else:
            ctx.packet_repeat_count = 0
            ctx.paused = False
            
        if packetStatus == PacketStatus.INACTIVE:
            print("The Current Scenario is no longer active.")
            deactivate_scenario(ctx.current_scenario)
            ctx.current_scenario = None
            await long_sleep()
            continue
        if packetStatus == PacketStatus.WRONG_VERSION:
            print("The Scenario is expecting a different version of the AP Client.")
            deactivate_scenario(ctx.current_scenario)
            ctx.current_scenario = None
            await long_sleep()
            continue
        if packetStatus == PacketStatus.WRONG_WORLD:
            print("The Scenario is expecting a different world ID.")
            deactivate_scenario(ctx.current_scenario)
            ctx.current_scenario = None
            await long_sleep()
            continue
        if packetStatus == PacketStatus.UPDATE:
            ctx.client_interface.on_location_received(ctx.current_scenario.value, ctx.current_packet.location_ids)
            print("UPDATE")
            
        if packetStatus == PacketStatus.ACTIVE:
            print("ACTIVE")
            print(packet.current_ping_id)
        
        await short_sleep()