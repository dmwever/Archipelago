from dataclasses import dataclass
from typing import Iterable

from ....Options import Unitsanity, UnitsanityItems
from ....generation import SlotData
from ....items.Items import Age2ItemData
from ....locations.Civilizations import Age2CivData
from ....locations.UnitLines import Age2UnitLineData
from ....locations.Units import Age2UnitData
from ....locations.connections.CivilizationUnits import CIV_TO_UNITS
from ....locations.connections.UnitBuildings import BUILDING_TO_UNITS_ITEM


@dataclass(frozen=True)
class Row:
    unit: Age2UnitData
    is_location: bool
    items: tuple[int, ...]

    @property
    def location_id(self) -> int:
        return self.unit.id if self.is_location else UnitData.NO_LOCATION


class UnitData:
    UNIT_CAPACITY = 400

    NO_LOCATION = -1
    MAX_ITEMS = 3          # the most upgrade tokens any one unit carries
    MAX_VARIANTS = 16      # the villager takes the most forms

    SEED_HIGH = "US_SEED_HIGH"
    SEED_LOW = "US_SEED_LOW"

    def __init__(self, locations: Iterable[Age2UnitData | Age2UnitLineData] = (),
                 civs: Iterable[Age2CivData] = (), mode: int = Unitsanity.option_none,
                 items_mode: int = UnitsanityItems.option_unit_line, tag: str = None):
        self._locations = set(locations)
        self._civs = tuple(civs)
        self._mode = mode
        self._items_mode = items_mode
        self._tag = tag

    def trainable(self) -> set[Age2UnitData]:
        return {unit for civ in self._civs for unit in CIV_TO_UNITS[civ]}

    def unit_locations(self) -> set[Age2UnitData]:
        return {place for place in self._locations if isinstance(place, Age2UnitData)}

    def wanted(self) -> set[Age2UnitData]:
        units = set(self.unit_locations())
        for place in self._locations:
            if isinstance(place, Age2UnitLineData):
                units |= set(place.units)
        return {unit for unit in units if unit in self.trainable()}

    def items_for(self, unit: Age2UnitData) -> tuple[int, ...]:
        if self._mode == Unitsanity.option_none:
            return ()
        if self._items_mode == UnitsanityItems.option_unit_line:
            item = unit.line.item
            return (item.id,) if item is not None else ()
        if self._items_mode == UnitsanityItems.option_upgrades:
            return tuple(token.id for token in unit.upgrade_tokens or ())
        return tuple(BUILDING_TO_UNITS_ITEM[building].id for building in unit.buildings or ()
                     if building in BUILDING_TO_UNITS_ITEM)

    def rows(self) -> list[Row]:
        locations = self.unit_locations()
        wanted = self.wanted()
        out: list[Row] = []
        for unit in Age2UnitData:
            if unit not in wanted:
                continue
            items = self.items_for(unit)
            if len(items) > self.MAX_ITEMS:
                raise ValueError(
                    f"{unit.unit_name} needs {len(items)} items; raise MAX_ITEMS here and "
                    "UNIT_ITEM_CAPACITY in Unitsanity.xs to match")
            out.append(Row(unit, unit in locations, items))
        stranded = {place for place in self._locations
                    if isinstance(place, Age2UnitData) and place not in wanted}
        if stranded:
            raise ValueError(
                "unit locations no civilization in the seed can field: "
                + ", ".join(sorted(unit.unit_name for unit in stranded)))
        if len(out) > self.UNIT_CAPACITY:
            raise ValueError(
                f"{len(out)} units is past the XS capacity of {self.UNIT_CAPACITY}; raise "
                "UNIT_CAPACITY in Unit_Constants.xs to match")
        return out

    def render(self) -> str:
        high, low = ((SlotData.UNSET, SlotData.UNSET) if self._tag is None
                     else SlotData.seed_halves(self._tag))
        lines = [f"extern const int {self.SEED_HIGH} = {high};",
                 f"extern const int {self.SEED_LOW} = {low};",
                 "",
                 "void LoadUnitTable() {"]
        body = len(lines)
        for row in self.rows():
            unit = row.unit
            lines.append(
                f"    addUnit({row.location_id}, {unit.game_id}, {unit.line.id}, "
                f"{unit.age.value}, {unit.tier}, {int(row.is_location)});")
            for item_id in row.items:
                lines.append(f"    addUnitItem({unit.game_id}, {item_id});")
            for variant in unit.variant_game_ids or ():
                lines.append(f"    addUnitVariant({unit.game_id}, {variant});")
        if len(lines) == body:
            lines.append("    return;")
        lines.append("}")
        return "\n".join(lines) + "\n"
