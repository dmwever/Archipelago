import logging
import tempfile
from pathlib import Path
from typing import Callable, Iterable

from ..AoE2ScenarioParser import settings
from ..AoE2ScenarioParser.datasets.object_support import StartingAge
from ..AoE2ScenarioParser.datasets.players import PlayerId
from ..AoE2ScenarioParser.scenarios.aoe2_de_scenario import AoE2DEScenario

settings.PRINT_STATUS_UPDATES = False

logger = logging.getLogger("Client")

Step = Callable[[AoE2DEScenario], bool]

def rebase_to_dark(scenario: AoE2DEScenario) -> bool:
    player = scenario.player_manager.players[PlayerId.ONE]
    if player.starting_age == StartingAge.DARK_AGE:
        return False
    player.starting_age = StartingAge.DARK_AGE
    return True

def apply(body: bytes, steps: Iterable[Step], name: str = "",
          progress: tuple[int, int] = (0, 0), report: Callable[[str], None] = None) -> bytes:
    steps = tuple(steps)
    if not steps:
        return body
    done, total = progress
    percent = round(done * 100 / total) if total else 100
    (report or logger.info)(f"Parsing {name} ........ {percent}%")
    with tempfile.TemporaryDirectory() as folder:
        source = Path(folder, "in.aoe2scenario")
        source.write_bytes(body)
        scenario: AoE2DEScenario = AoE2DEScenario.from_file(str(source))
        changed = [step(scenario) for step in steps]
        if not any(changed):
            return body
        target = Path(folder, "out.aoe2scenario")
        scenario.write_to_file(str(target))
        return target.read_bytes()
