from typing import Mapping

SLOT_ID = "AP_SLOT_ID"
SEED_HIGH = "AP_SEED_HIGH"
SEED_LOW = "AP_SEED_LOW"

UNSET = -1
DEFAULTS: dict[str, int] = {SLOT_ID: UNSET, SEED_HIGH: UNSET, SEED_LOW: UNSET}

MAX_LITERAL = 999_999_999
HALF_WIDTH = 16
HALF_MASK = (1 << HALF_WIDTH) - 1


def seed_halves(tag: str) -> tuple[int, int]:
    value = int(tag, 16)
    return value >> HALF_WIDTH, value & HALF_MASK


def fields(slot: int, tag: str) -> dict[str, int]:
    high, low = seed_halves(tag)
    return {SLOT_ID: slot, SEED_HIGH: high, SEED_LOW: low}


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
