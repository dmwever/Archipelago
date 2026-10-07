from dataclasses import dataclass

from ..Scenarios import Age2ScenarioData


@dataclass(frozen=True)
class MilestoneCapability:
    explore: int = 0
    kill: int = 0
    raze: int = 0
    own: int = 0
    convert: int = 0


SCENARIO_TO_CAPABILITY: dict[Age2ScenarioData, MilestoneCapability] = {

    Age2ScenarioData.AP_ATTILA_1: MilestoneCapability(
        explore=50, kill=25, raze=25, own=20),

    Age2ScenarioData.AP_ATTILA_2: MilestoneCapability(
        explore=50, kill=50, raze=50, own=20),

    Age2ScenarioData.AP_ATTILA_3: MilestoneCapability(
        explore=25, kill=10, raze=5, own=5, convert=5),

    Age2ScenarioData.AP_ATTILA_4: MilestoneCapability(
        explore=50, kill=1, raze=1, own=5),

    Age2ScenarioData.AP_ATTILA_5: MilestoneCapability(
        explore=50, kill=10, raze=25, own=20),

    Age2ScenarioData.AP_ATTILA_6: MilestoneCapability(
        explore=35, kill=50, raze=25, own=30),

    Age2ScenarioData.AP_JOAN_1: MilestoneCapability(
        explore=25, kill=25, raze=10, own=3),

    Age2ScenarioData.AP_JOAN_2: MilestoneCapability(
        explore=35, kill=10, raze=0, own=5),

    Age2ScenarioData.AP_JOAN_3: MilestoneCapability(
        explore=5, kill=0, raze=0, own=20),

    Age2ScenarioData.AP_JOAN_4: MilestoneCapability(
        explore=50, kill=50, raze=5, own=20, convert=5),

    Age2ScenarioData.AP_JOAN_5: MilestoneCapability(
        explore=50, kill=100, raze=100, own=60),

    Age2ScenarioData.AP_JOAN_6: MilestoneCapability(
        explore=25, kill=1, raze=1, own=2),
}

NOTHING = MilestoneCapability()


def capability(scenario: Age2ScenarioData) -> MilestoneCapability:
    if scenario in SCENARIO_TO_CAPABILITY:
        return SCENARIO_TO_CAPABILITY[scenario]
    return NOTHING
