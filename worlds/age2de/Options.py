from dataclasses import dataclass

from Options import PerGameCommonOptions, StartInventoryPool


@dataclass
class Age2Options(PerGameCommonOptions):
    """
    Every option in the Age2DE randomizer
    """
    startInventoryPool: StartInventoryPool 