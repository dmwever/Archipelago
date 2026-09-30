from dataclasses import dataclass
from typing import Iterable

from ....Options import Unitsanity, UnitsanityItems
from ....generation import SlotData
from ....generation.pools.UnitPool import VILLAGER_LINES, UnitLocation
from ....locations.Ages import Age2AgeData
from ....locations.Buildings import Age2BuildingData
from ....locations.Civilizations import Age2CivData
from ....locations.EscortUnits import Age2EscortUnitData
from ....locations.Heroes import Age2HeroData
from ....locations.UnitLines import Age2UnitLineData
from ....locations.Units import Age2UnitData
from ....locations.VillagerJobs import Age2VillagerJobData
from ....locations.connections.CivilizationUnits import CIV_TO_UNITS
from ....locations.connections.UnitBuildings import BUILDING_TO_UNITS_ITEM


PLACES_BY_PRECEDENCE = (Age2UnitData, Age2UnitLineData, Age2VillagerJobData,
                        Age2HeroData, Age2EscortUnitData)


@dataclass(frozen=True)
class Row:
    unit: UnitLocation
    location_id: int
    line_id: int
    age: int
    tier: int
    upgrade_item_id: int
    caveman_exempt: bool
    items: tuple[int, ...]
    variants: tuple[int, ...]


class UnitData:
    UNIT_CAPACITY = 400

    NO_LOCATION = -1
    NO_LINE = -1
    NO_UPGRADE_ITEM = -1
    MAX_ITEMS = 3
    MAX_VARIANTS = 16

    SEED_HIGH = "US_SEED_HIGH"
    SEED_LOW = "US_SEED_LOW"

    def __init__(self, locations: Iterable[UnitLocation] = (),
                 civs: Iterable[Age2CivData] = (), mode: int = Unitsanity.option_none,
                 items_mode: int = UnitsanityItems.option_unit_line, tag: str = None):
        self._locations = set(locations)
        self._civs = tuple(civs)
        self._mode = mode
        self._items_mode = items_mode
        self._tag = tag
        self._trainable = {unit for civ in self._civs for unit in CIV_TO_UNITS[civ]}
        if Age2UnitData.VILLAGER_MALE in self._trainable:
            self._trainable.add(Age2UnitData.VILLAGER_FEMALE)

    def places(self) -> list[UnitLocation]:
        return [place for kind in PLACES_BY_PRECEDENCE for place in kind
                if place in self._locations]

    def civs_build(self, building: Age2BuildingData) -> bool:
        return any(civ.builds(building) for civ in self._civs)

    def is_caveman_exempt(self, unit: Age2UnitData) -> bool:
        return unit.line in VILLAGER_LINES

    def upgrade_item_for(self, unit: Age2UnitData) -> int:
        tech = unit.upgrade_tech
        if tech is None or tech.item is None:
            return self.NO_UPGRADE_ITEM
        return tech.item.id

    def items_for(self, unit: Age2UnitData) -> tuple[int, ...]:
        if unit.line in VILLAGER_LINES:
            return (Age2UnitLineData.VILLAGER_MALE_LINE.item.id,)
        if self._mode == Unitsanity.option_none:
            return ()
        if self._items_mode == UnitsanityItems.option_unit_line:
            item = unit.line.item
            return (item.id,) if item is not None else ()
        if self._items_mode == UnitsanityItems.option_upgrades:
            return tuple(token.id for token in unit.upgrade_tokens or ())
        return tuple(BUILDING_TO_UNITS_ITEM[building].id for building in unit.buildings or ()
                     if building in BUILDING_TO_UNITS_ITEM and self.civs_build(building))

    def unit_row(self, unit: Age2UnitData, location_id: int) -> Row:
        items = self.items_for(unit)
        if len(items) > self.MAX_ITEMS:
            raise ValueError(
                f"{unit.unit_name} needs {len(items)} items; raise MAX_ITEMS here and "
                "UNIT_ITEM_CAPACITY in AP_Constants.xs to match")
        return Row(unit, location_id, unit.line.id, unit.age.value, unit.tier,
                   self.upgrade_item_for(unit), self.is_caveman_exempt(unit), items,
                   tuple(unit.variant_game_ids or ()))

    def owned_type_row(self, place: UnitLocation) -> Row:
        if isinstance(place, Age2VillagerJobData):
            return Row(place, place.id, place.line.id, Age2AgeData.DARK.value, 1,
                       self.NO_UPGRADE_ITEM, True, (place.item.id,), ())

        return Row(place, place.id, self.NO_LINE, Age2AgeData.DARK.value, 0,
                   self.NO_UPGRADE_ITEM, True, (), ())

    def rows_for(self, place: UnitLocation) -> list[Row]:
        if isinstance(place, Age2UnitLineData):
            return [self.unit_row(unit, place.id) for unit in place.units
                    if unit in self._trainable]
        if isinstance(place, Age2UnitData):
            return [self.unit_row(place, place.id)]
        return [self.owned_type_row(place)]

    def rows(self) -> list[Row]:
        out: dict[UnitLocation, Row] = {}
        for place in self.places():
            for row in self.rows_for(place):
                out.setdefault(row.unit, row)
        if len(out) > self.UNIT_CAPACITY:
            raise ValueError(
                f"{len(out)} units is past the XS capacity of {self.UNIT_CAPACITY}; raise "
                "UNIT_CAPACITY in AP_Constants.xs to match")
        return list(out.values())

    def render(self) -> str:
        high, low = ((SlotData.UNSET, SlotData.UNSET) if self._tag is None
                     else SlotData.seed_halves(self._tag))
        lines = [f"extern const int {self.SEED_HIGH} = {high};",
                 f"extern const int {self.SEED_LOW} = {low};",
                 "",
                 "void LoadUnitTable() {"]
        body = len(lines)
        for row in self.rows():
            lines.append(
                f"    addUnit({row.location_id}, {row.unit.game_id}, {row.line_id}, "
                f"{row.age}, {row.tier}, {row.upgrade_item_id}, "
                f"{int(row.caveman_exempt)});")
            for item_id in row.items:
                lines.append(f"    addUnitItem({row.unit.game_id}, {item_id});")
            for variant in row.variants:
                lines.append(f"    addUnitVariant({row.unit.game_id}, {variant});")
        if len(lines) == body:
            lines.append("    return;")
        lines.append("}")
        return "\n".join(lines) + "\n"
