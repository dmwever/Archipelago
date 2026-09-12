from dataclasses import dataclass
from typing import Iterable

from . import SlotData
from ..items.Items import CATEGORY_TO_ITEMS, Age2ItemData, Tech
from ..locations.Ages import Age2AgeData
from ..locations.Civilizations import Age2CivData
from ..locations.Techs import Age2TechData, TechOption

TECH_CAPACITY = 400
TECH_ITEM_OFFSET = 3600

NO_ITEM = -1
ANY_CIV = -1

SEED_HIGH = "TS_SEED_HIGH"
SEED_LOW = "TS_SEED_LOW"


@dataclass(frozen=True)
class Row:
    item_id: int
    tech: Tech
    is_location: bool


def researchable(civs: Iterable[Age2CivData] = ()) -> list[Age2ItemData]:
    """The tech items some civilization in the seed can research.

    Read the way buildings are: a unique or regional tech counts if any civ
    includes it, a shared one is gone only if every civ excludes it.
    """
    civs = tuple(civs)
    owned = {tech.id for civ in civs for tech in civ.included_techs}
    missing = (set.intersection(*({tech.id for tech in civ.excluded_techs} for civ in civs))
               if civs else set())
    out = []
    for item in CATEGORY_TO_ITEMS[Tech]:
        if item.type.is_unique or TechOption.regional in Age2TechData(item.id).tech_options:
            if item.id in owned:
                out.append(item)
        elif item.id not in missing:
            out.append(item)
    return out


def rows(location_ids: Iterable[int], grant_age: Age2AgeData = None,
         civs: Iterable[Age2CivData] = ()) -> list[Row]:
    """The seed's pool as locations, plus the grant-only rows a rebased scenario needs."""
    wanted = set(location_ids)
    allowed = {item.id for item in researchable(civs)}
    depth = None if grant_age is None else grant_age.tier
    out: list[Row] = []
    for item in CATEGORY_TO_ITEMS[Tech]:
        tech = item.type
        researchable_here = item.id in allowed
        if item.id in wanted:
            wanted.discard(item.id)
            if not researchable_here:
                raise ValueError(
                    f"{item.item_name} is a location, but no civilization in the seed "
                    "can research it")
            out.append(Row(item.id, tech, True))
        elif depth is not None and researchable_here and tech.age.tier < depth:
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
            f"{int(tech.is_upgrade)}, {int(tech.is_unique)}, {tech.age.tier}, "
            f"{int(row.is_location)});")
    lines.append("}")
    return "\n".join(lines) + "\n"
