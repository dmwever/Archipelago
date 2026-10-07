from typing import Iterable

from ....generation import SlotData
from ....items.Items import Resource
from ....locations.FillerLocations import Age2FillerLocationData, FillerKind


KIND_TO_XS: dict[FillerKind, str] = {
    FillerKind.EXPLORE: "FILLER_EXPLORE",
    FillerKind.OWN_UNITS: "FILLER_OWN_UNITS",
    FillerKind.KILL_UNITS: "FILLER_KILL_UNITS",
    FillerKind.RAZE_BUILDINGS: "FILLER_RAZE_BUILDINGS",
    FillerKind.RESEARCH_TECHS: "FILLER_RESEARCH_TECHS",
    FillerKind.BUILD_BUILDINGS: "FILLER_BUILD_BUILDINGS",
    FillerKind.CONVERT_UNITS: "FILLER_CONVERT_UNITS",
    FillerKind.TRAIN_VILLAGERS: "FILLER_TRAIN_VILLAGERS",
}

RESOURCE_TO_XS: dict[Resource, str] = {
    Resource.FOOD: "FILLER_COLLECT_FOOD",
    Resource.WOOD: "FILLER_COLLECT_WOOD",
    Resource.GOLD: "FILLER_COLLECT_GOLD",
    Resource.STONE: "FILLER_COLLECT_STONE",
}


class FillerData:
    FILLER_CAPACITY = 128

    SEED_HIGH = "FILLER_SEED_HIGH"
    SEED_LOW = "FILLER_SEED_LOW"

    def __init__(self, locations: Iterable[Age2FillerLocationData] = (), tag: str = None):
        self._locations = set(locations)
        self._tag = tag

    @staticmethod
    def kind_of(filler: Age2FillerLocationData) -> str:
        if filler.kind is FillerKind.COLLECT:
            return RESOURCE_TO_XS[filler.resource]
        return KIND_TO_XS[filler.kind]

    def rows(self) -> list[Age2FillerLocationData]:
        wanted = set(self._locations)
        out = [filler for filler in Age2FillerLocationData if filler in wanted]
        wanted.difference_update(out)
        if wanted:
            raise ValueError("Not a milestone location: "
                             + ", ".join(sorted(str(filler) for filler in wanted)))
        if len(out) > self.FILLER_CAPACITY:
            raise ValueError(
                f"{len(out)} milestones is past the XS capacity of {self.FILLER_CAPACITY}; raise "
                "FILLER_CAPACITY in AP_Constants.xs to match")
        return out

    def render(self) -> str:
        high, low = ((SlotData.UNSET, SlotData.UNSET) if self._tag is None
                     else SlotData.seed_halves(self._tag))
        lines = [f"extern const int {self.SEED_HIGH} = {high};",
                 f"extern const int {self.SEED_LOW} = {low};",
                 "",
                 "void LoadFillerTable() {"]
        body = len(lines)
        for filler in self.rows():
            lines.append(
                f"    addFillerLocation({filler.id}, {self.kind_of(filler)}, {filler.threshold});")
        if len(lines) == body:
            lines.append("    return;")
        lines.append("}")
        return "\n".join(lines) + "\n"
