import asyncio
from asyncio.log import logger
from dataclasses import dataclass
import os
from typing import Optional, Protocol
import zipfile

from CommonClient import get_base_parser, server_loop
import Utils


class APClientInterface(Protocol):
    def on_location_received(self, scenario_id: int, location_ids: list[int]):
        """Called when a new location is received"""
        pass
    def fetch_locations_collected(self, location_status: dict[int, int], new_scenario_id: int):
        """Called when a new location is received"""
        pass

@dataclass
class Age2GameContext:
    running: bool
    ap_client: APClientInterface