import enum

class ScenarioPlayer(enum.Enum):
    """A player in one scenario, named for what the campaign calls it. Each scenario declares its
    own enumeration of these; a neutral or ignored slot has no member."""

    def __init__(self, slot: int, player_name: str) -> None:
        self.slot = slot
        """Its slot in the scenario, P2 to P8."""
        self.player_name = player_name
        """How it reads mid-sentence: "can defeat the Jin"."""
