from dataclasses import dataclass
from typing import Iterable

from ....Options import ExistingTechs
from ....generation import SlotData
from ....locations.Ages import Age2AgeData
from ....locations.Civilizations import Age2CivData
from ....locations.Techs import Age2TechData
from ....locations.connections.CivilizationTechs import CIV_TO_TECHS


@dataclass(frozen=True)
class Row:
    tech: Age2TechData
    is_location: bool

    @property
    def item_id(self) -> int:
        """The id XS unlocks against, which is an item id, not this location's."""
        return self.tech.item.id if self.is_location else TechData.NO_ITEM


class TechData:

    TECH_CAPACITY = 400

    NO_ITEM = -1
    NO_PREREQUISITE = -1

    SEED_HIGH = "TS_SEED_HIGH"
    SEED_LOW = "TS_SEED_LOW"

    def __init__(self, locations: Iterable[Age2TechData] = (),
                 grant_age: Age2AgeData = None, civs: Iterable[Age2CivData] = (),
                 tag: str = None):
        self._locations = set(locations)
        self._grant_age = grant_age
        self._civs = tuple(civs)
        self._tag = tag
    
    @staticmethod
    def rebases(existing: int) -> bool:
        """Whether the installed scenario has to start in the Dark Age, so that the
        engine auto-researches nothing and XS can grant the right state."""
        return existing != ExistingTechs.option_vanilla


    def rows(self) -> list[Row]:
        """The seed's pool as locations, plus the grant-only rows a rebased scenario needs."""
        wanted = set(self._locations)
        allowed = {tech for civ in self._civs for tech in CIV_TO_TECHS[civ]}
        out: list[Row] = []
        for tech in Age2TechData:
            if tech in wanted:
                wanted.discard(tech)
                if tech not in allowed:
                    raise ValueError(
                        f"{tech.location_name} is a location, but no civilization in "
                        "the seed can research it")
                out.append(Row(tech, True))
            elif (self._grant_age is not None and tech in allowed
                    and tech.age < self._grant_age):
                out.append(Row(tech, False))
        if wanted:
            raise ValueError("Not a technology location: "
                             + ", ".join(sorted(str(tech) for tech in wanted)))
        if len(out) > self.TECH_CAPACITY:
            raise ValueError(
                f"{len(out)} techs is past the XS capacity of {self.TECH_CAPACITY}; raise "
                "TECH_CAPACITY in Tech_Constants.xs to match")
        return out


    def render(self) -> str:
        high, low = ((SlotData.UNSET, SlotData.UNSET) if self._tag is None
                     else SlotData.seed_halves(self._tag))
        lines = [f"extern const int {self.SEED_HIGH} = {high};",
                 f"extern const int {self.SEED_LOW} = {low};",
                 "",
                 "void LoadTechTable() {"]
        body = len(lines)
        for row in self.rows():
            tech = row.tech.item.type
            lines.append(
                f"    addTech({row.item_id}, {tech.game_id}, {tech.effect_id}, {tech.civ}, "
                f"{int(tech.is_upgrade)}, {int(tech.is_unique)}, {row.tech.age.value}, "
                f"{int(row.is_location)}, {row.tech.prerequisiteId});")
        if len(lines) == body:
            lines.append("    return;")
        lines.append("}")
        return "\n".join(lines) + "\n"
