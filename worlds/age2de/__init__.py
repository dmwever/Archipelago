# world/age2DE/__init__.py

import logging
from typing import Any
from worlds.LauncherComponents import Component, SuffixIdentifier, Type, components, launch as launch_subprocess
from .World import Age2World

logger = logging.getLogger(__name__)

def run_client(*args: Any):
    print("Running Age of Empires II: Definitive Edition Client")
    from .client.ApClient import main  # lazy import

    launch_subprocess(main, name="Age2Client")

components.append(
    Component(
        "Age of Empires II: DE Client",
        func=run_client,
        component_type=Type.CLIENT,
        file_identifier=SuffixIdentifier(".apcivvi"),
    )
)