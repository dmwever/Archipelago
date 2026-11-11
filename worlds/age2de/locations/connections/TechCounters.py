"""Counters that only answer some targets once a tech is researched."""
from ..Techs import Age2TechData
from ..UnitLines import Age2UnitLineData
from .UnitRoles import FAITH_LINES


REDEMPTION_TARGETS = (
    Age2UnitLineData.BATTERING_RAM_LINE,
    Age2UnitLineData.MANGONEL_LINE,
    Age2UnitLineData.ROCKET_CART_LINE,
    Age2UnitLineData.SCORPION_LINE,
    Age2UnitLineData.SIEGE_TOWER_LINE,
    # Converts with Redemption too, but monks are not listed as countering it.
    Age2UnitLineData.BOMBARD_CANNON_LINE,
    Age2UnitLineData.TREBUCHET_LINE,
    Age2UnitLineData.TRACTION_TREBUCHET_LINE,
    Age2UnitLineData.ORGAN_GUN_LINE,
    Age2UnitLineData.HUSSITE_WAGON_LINE,
)
"""What a monk can only convert once Redemption is researched."""

TECH_COUNTERS: tuple[tuple[tuple[Age2UnitLineData, ...], tuple[Age2UnitLineData, ...],
                           Age2TechData], ...] = (
    (FAITH_LINES, REDEMPTION_TARGETS, Age2TechData.REDEMPTION),
)
"""(counters, targets, tech): those counters answer those targets only once the tech is
researched."""


for _counters, _targets, _tech in TECH_COUNTERS:
    for _target in _targets:
        for _counter in _counters:
            _target.counter_techs[_counter] = _tech
