from typing import Mapping

from ..Options import (Caveman, ExistingTechs, IncludeUniqueUnits, LockTechs, ShuffleAges,
                       ShuffleUniqueTechs, ShuffleVillager, TechBehavior, Techsanity, Unitsanity,
                       UnitsanityItems)

SLOT_ID = "AP_SLOT_ID"
SEED_HIGH = "AP_SEED_HIGH"
SEED_LOW = "AP_SEED_LOW"
TS_MODE = "AP_TS_MODE"
TS_BEHAVIOR = "AP_TS_BEHAVIOR"
TS_LOCK = "AP_TS_LOCK"
TS_UNIQUES = "AP_TS_UNIQUES"
TS_EXISTING = "AP_TS_EXISTING"
SHUFFLE_AGES = "AP_SHUFFLE_AGES"
US_MODE = "AP_US_MODE"
US_ITEMS = "AP_US_ITEMS"
US_VILLAGER = "AP_US_VILLAGER"
US_UNIQUES = "AP_US_UNIQUES"
US_CAVEMAN = "AP_US_CAVEMAN"

UNSET = -1

DEFAULTS: dict[str, int] = {
    SLOT_ID: UNSET,
    SEED_HIGH: UNSET,
    SEED_LOW: UNSET,
    TS_MODE: Techsanity.option_none,
    TS_BEHAVIOR: UNSET,
    TS_LOCK: UNSET,
    TS_UNIQUES: UNSET,
    TS_EXISTING: UNSET,
    SHUFFLE_AGES: 0,  # not UNSET: a seedless install must read this as off
    US_MODE: Unitsanity.option_none,
    US_ITEMS: UNSET,
    US_VILLAGER: UNSET,
    US_UNIQUES: UNSET,
    US_CAVEMAN: 0,  # like SHUFFLE_AGES: off, not unset, so a seedless install is quiet
}

OPTIONS: dict[str, str] = {
    TS_MODE: Techsanity.internal_name,
    TS_BEHAVIOR: TechBehavior.internal_name,
    TS_LOCK: LockTechs.internal_name,
    TS_UNIQUES: ShuffleUniqueTechs.internal_name,
    TS_EXISTING: ExistingTechs.internal_name,
    SHUFFLE_AGES: ShuffleAges.internal_name,
    US_MODE: Unitsanity.internal_name,
    US_ITEMS: UnitsanityItems.internal_name,
    US_VILLAGER: ShuffleVillager.internal_name,
    US_UNIQUES: IncludeUniqueUnits.internal_name,
    US_CAVEMAN: Caveman.internal_name,
}

MAX_LITERAL = 999_999_999
HALF_WIDTH = 16
HALF_MASK = (1 << HALF_WIDTH) - 1


def seed_halves(tag: str) -> tuple[int, int]:
    value = int(tag, 16)
    return value >> HALF_WIDTH, value & HALF_MASK


def options(slot_data: Mapping[str, object] = None) -> dict[str, int]:
    slot_data = {} if slot_data is None else slot_data
    return {name: int(slot_data.get(key, DEFAULTS[name])) for name, key in OPTIONS.items()}


def slot_fields(slot: int, tag: str, slot_data: Mapping[str, object] = None) -> dict[str, int]:
    high, low = seed_halves(tag)
    values = {SLOT_ID: slot, SEED_HIGH: high, SEED_LOW: low}
    values.update(options(slot_data))
    return values


def render(values: Mapping[str, int] = None) -> str:
    values = DEFAULTS if values is None else values
    lines = []
    for name, value in values.items():
        if not isinstance(value, int) or isinstance(value, bool):
            raise TypeError(f"{name} must be an int, not {type(value).__name__}")
        if abs(value) > MAX_LITERAL:
            raise ValueError(
                f"{name} is {value}; XS cannot initialise an int literal beyond "
                f"{MAX_LITERAL}, so split it into parts")
        lines.append(f"extern const int {name} = {value};")
    return "\n".join(lines) + "\n"
