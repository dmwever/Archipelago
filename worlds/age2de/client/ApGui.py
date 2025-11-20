import asyncio
import logging
from typing import TYPE_CHECKING
from kvui import GameManager, LogtoUI


if TYPE_CHECKING:
    from .ApClient import Age2Context
    
class Age2Manager(GameManager):
    base_title = "Archipelago Age of Empires 2: Definitive Edition Client"
    ctx = 'Age2Context'
    
    def on_start(self) -> None:
        logging.getLogger(__name__).addHandler(LogtoUI(self.log_panels["All"].on_log))
        
    def build(self):
        return super().build()
    
    def start_ap_ui(ctx: 'Age2Context') -> None:
        ctx.ui = Age2Manager(ctx)
        ctx.ui_task = asyncio.create_task(ctx.ui.async_run(), name='UI')