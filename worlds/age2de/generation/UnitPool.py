from typing import Iterable

from ..Options import (Age2Options, IncludeUniqueUnits, ShuffleVillager, Unitsanity,
                       UnitsanityItems)
from ..items.Items import Age2ItemData
from ..locations.Buildings import Age2BuildingData
from ..locations.Civilizations import Age2CivData
from ..locations.Heroes import Age2HeroData
from ..locations.Scenarios import Age2ScenarioData
from ..locations.UnitLines import Age2UnitLineData
from ..locations.Units import Age2UnitData, UnitType
from ..locations.VillagerJobs import Age2VillagerJobData
from ..locations.connections.CivilizationUnits import CIV_TO_UNITS, UNTRAINABLE
from ..locations.connections.UnitBuildings import BUILDING_TO_UNITS_ITEM

type UnitLocation = Age2UnitData | Age2UnitLineData | Age2VillagerJobData | Age2HeroData

UNIT_TYPE_TO_OPTIONS: dict[str, tuple[int, ...]] = {
    UnitType.unique_unit: (IncludeUniqueUnits.option_unique, IncludeUniqueUnits.option_both),
    UnitType.regional_unit: (IncludeUniqueUnits.option_regional, IncludeUniqueUnits.option_both),
}

class UnitPool:

    def __init__(self, options: Age2Options, civs: Iterable[Age2CivData],
                 scenarios: Iterable[Age2ScenarioData]) -> None:
        self._unitsanity = options.unitsanity
        self._unitsanity_items = options.unitsanity_items
        self._include_unique_units = options.include_unique_units
        self._shuffle_villager = options.shuffle_villager
        self._scenarios = list(scenarios)
        self._trainable = {unit for civ in civs for unit in CIV_TO_UNITS[civ]}
        self._granted = {grant
                         for scenario in self._scenarios
                         for grant in scenario.startup_units + scenario.trigger_units}


    def is_villager(self, unit: Age2UnitData) -> bool:
        """Shuffle Villager owns the villager outright, so unitsanity never touches it."""
        return unit.line is Age2UnitLineData.VILLAGER_LINE


    def is_unit_type_included(self, unit: Age2UnitData) -> bool:
        """Include Unique Units. A unit every civilization has is never held back by it."""
        wanted = UNIT_TYPE_TO_OPTIONS.get(unit.unit_type)
        return wanted is None or self._include_unique_units in wanted


    def includes(self, unit: Age2UnitData) -> bool:
        """Whether this unit is one of the seed's units, in any unitsanity mode."""
        if self._unitsanity == Unitsanity.option_none:
            return False
        if self.is_villager(unit) or unit in UNTRAINABLE:
            return False
        if unit not in self._trainable:
            if self._unitsanity != Unitsanity.option_all or unit not in self._granted:
                return False
        return self.is_unit_type_included(unit)


    def includes_line(self, line: Age2UnitLineData) -> bool:
        """A line is in play when any of its tiers is. A civilization that reaches only the
        base tier still gets the line, which is what makes the line the unit of unlocking."""
        return any(self.includes(unit) for unit in line.units)


    def is_trainable(self, line: Age2UnitLineData) -> bool:
        return any(unit in self._trainable for unit in line.units)


    @property
    def lines(self) -> list[Age2UnitLineData]:
        """Every line in play. These are what unitsanity items unlock, in both modes - under
        `all` the locations become per-unit but the lines are still the thing you unlock."""
        return [line for line in Age2UnitLineData if self.includes_line(line)]


    @property
    def units(self) -> list[Age2UnitData]:
        """Every unit in play, whether or not each is separately a location."""
        return [unit for unit in Age2UnitData if self.includes(unit)]


    @property
    def heroes(self) -> list[Age2HeroData]:
        if self._unitsanity != Unitsanity.option_all:
            return []
        return [hero for hero in Age2HeroData if hero in self._granted]


    @property
    def villager_locations(self) -> list[UnitLocation]:
        if self._shuffle_villager == ShuffleVillager.option_no:
            return []
        if self._shuffle_villager != ShuffleVillager.option_include_professions:
            return [Age2UnitLineData.VILLAGER_LINE]
        return [Age2UnitData.VILLAGER_MALE, Age2UnitData.VILLAGER_FEMALE] \
            + list(Age2VillagerJobData)

    @property
    def line_locations(self) -> dict[Age2UnitLineData, list[UnitLocation]]:
        grouped: dict[Age2UnitLineData, list[UnitLocation]] = {}
        if self._unitsanity == Unitsanity.option_all:
            for unit in self.units:
                grouped.setdefault(unit.line, []).append(unit)
        else:
            for line in self.lines:
                grouped[line] = [line]
        villager = self.villager_locations
        if villager:
            grouped[Age2UnitLineData.VILLAGER_LINE] = villager
        return grouped


    def owner_of(self, location: UnitLocation) -> Age2UnitData:
        """The unit whose producing buildings decide where a location is placed. A villager
        job is done by a villager, so it sits wherever villagers are trained."""
        if isinstance(location, Age2VillagerJobData) or self.is_villager_location(location):
            return Age2UnitData.VILLAGER_MALE
        if isinstance(location, Age2UnitLineData):
            return location.head
        return location


    def is_villager_location(self, location: UnitLocation) -> bool:
        """Anything Shuffle Villager owns, whichever granularity produced it."""
        if isinstance(location, Age2VillagerJobData):
            return True
        if isinstance(location, Age2HeroData):
            return False
        if isinstance(location, Age2UnitLineData):
            return location is Age2UnitLineData.VILLAGER_LINE
        return self.is_villager(location)


    def scenario_grants_line(self, scenario: Age2ScenarioData, line: Age2UnitLineData,
               at_start: bool) -> bool:
        granted = scenario.startup_units if at_start else scenario.trigger_units
        return any(isinstance(grant, Age2UnitData) and grant.line is line
                   for grant in granted)


    def scenario_grants_hero(self, scenario: Age2ScenarioData, hero: Age2HeroData,
                    at_start: bool) -> bool:
        granted = scenario.startup_units if at_start else scenario.trigger_units
        return hero in granted


    def items(self, lines: Iterable[Age2UnitLineData], units: Iterable[Age2UnitData],
              buildings: Iterable[Age2BuildingData], villager: bool) -> list[Age2ItemData]:
        chosen: list[Age2ItemData]
        if self._unitsanity_items == UnitsanityItems.option_unit_line:
            chosen = [line.item for line in lines if self.is_trainable(line)]
        elif self._unitsanity_items == UnitsanityItems.option_upgrades:
            wanted = {token for unit in units for token in unit.upgrade_tokens}
            chosen = [token for token in Age2ItemData if token in wanted]
        else:
            producers = set(buildings)
            chosen = [BUILDING_TO_UNITS_ITEM[building] for building in Age2BuildingData
                      if building in producers]
        if villager:
            chosen.append(Age2UnitLineData.VILLAGER_LINE.item)
        return chosen
