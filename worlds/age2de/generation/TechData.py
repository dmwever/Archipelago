from dataclasses import dataclass
from typing import Iterable

from . import SlotData
from ..items.Items import Age, Age2ItemData, Tech

# Mirrors of Tech_Constants.xs. A row past the capacity is dropped by addTech
# without a word, and an item id outside the band never reaches techByItem.
TECH_CAPACITY = 400
TECH_ITEM_OFFSET = 3600

NO_ITEM = -1
ANY_CIV = -1

# The file name is fixed, so a stale TechData.xs from another seed would load
# silently. These are checked against AP_SEED_HIGH / AP_SEED_LOW in SlotData.xs.
SEED_HIGH = "AP_TECH_SEED_HIGH"
SEED_LOW = "AP_TECH_SEED_LOW"

AGE_ORDER: dict[Age, int] = {Age.DARK: 0, Age.FEUDAL: 1, Age.CASTLE: 2, Age.IMPERIAL: 3}

TECH_ITEMS: tuple[Age2ItemData, ...] = tuple(sorted(
    (item for item in Age2ItemData if isinstance(item.type, Tech)), key=lambda item: item.id))


@dataclass(frozen=True)
class Row:
    item_id: int
    tech: Tech
    is_location: bool


def rows(location_ids: Iterable[int], grant_age: Age = None,
         civs: Iterable[int] = ()) -> list[Row]:
    """The seed's pool as locations, plus the grant-only rows a rebased scenario needs.

    location_ids are tech item ids the server knows about. grant_age is the deepest
    vanilla age among the installed scenarios, or None when nothing was rebased and
    the engine has already researched everything below it.
    """
    wanted = set(location_ids)
    playable = set(civs)
    out: list[Row] = []
    for item in TECH_ITEMS:
        tech = item.type
        if item.id in wanted:
            wanted.discard(item.id)
            out.append(Row(item.id, tech, True))
        elif (grant_age is not None
              and AGE_ORDER[tech.age] < AGE_ORDER[grant_age]
              and (tech.civ == ANY_CIV or tech.civ in playable)):
            out.append(Row(NO_ITEM, tech, False))
    if wanted:
        raise ValueError(
            "No tech carries item id " + ", ".join(str(id) for id in sorted(wanted)))
    if len(out) > TECH_CAPACITY:
        raise ValueError(
            f"{len(out)} techs is past the XS capacity of {TECH_CAPACITY}; raise "
            "TECH_CAPACITY in Tech_Constants.xs to match")
    return out


def render(table: Iterable[Row] = (), tag: str = None) -> str:
    high, low = (SlotData.UNSET, SlotData.UNSET) if tag is None else SlotData.seed_halves(tag)
    lines = [f"extern const int {SEED_HIGH} = {high};",
             f"extern const int {SEED_LOW} = {low};",
             "",
             "void LoadTechTable() {"]
    for row in table:
        tech = row.tech
        lines.append(
            f"    addTech({row.item_id}, {tech.game_id}, {tech.effect_id}, {tech.civ}, "
            f"{int(tech.is_upgrade)}, {int(tech.is_unique)}, {AGE_ORDER[tech.age]}, "
            f"{int(row.is_location)});")
    lines.append("}")
    return "\n".join(lines) + "\n"
