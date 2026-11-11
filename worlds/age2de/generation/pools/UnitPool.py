from typing import Iterable

from ...Options import (Age2Options, IncludeUniqueUnits, ShuffleVillager, Unitsanity,
                        UnitsanityItems, upgrade_techs_shuffled)
from ...items.Items import Age2ItemData
from ...locations.Buildings import Age2BuildingData
from ...locations.Civilizations import Age2CivData
from ...locations.EscortUnits import Age2EscortUnitData
from ...locations.Heroes import Age2HeroData
from ...locations.Scenarios import Age2ScenarioData
from ...locations.UnitLines import Age2UnitLineData
from ...locations.UnitLocations import UnitLocation, VILLAGER_LINES
from ...locations.Units import Age2UnitData, UnitType
from ...locations.VillagerJobs import Age2VillagerJobData
from ...locations.connections.CivilizationUnits import CIV_TO_UNITS, UNTRAINABLE
from ...locations.connections.UnitBuildings import BUILDING_TO_UNITS_ITEM
from ...locations.connections.VillagerJobResources import JOB_TO_SCENARIOS
from .CivilizationPool import CivilizationPool

UNIT_TYPE_TO_OPTIONS: dict[str, tuple[int, ...]] = {
    UnitType.unique_unit: (IncludeUniqueUnits.option_unique, IncludeUniqueUnits.option_both),
    UnitType.regional_unit: (IncludeUniqueUnits.option_regional, IncludeUniqueUnits.option_both),
}

class UnitPool:

    def __init__(self, options: Age2Options, civs: CivilizationPool,
                 scenarios: Iterable[Age2ScenarioData]) -> None:
        self._unitsanity = options.unitsanity
        self._unitsanity_items = options.unitsanity_items
        self._techsanity = options.techsanity
        self._include_unique_units = options.include_unique_units
        self._shuffle_villager = options.shuffle_villager
        self._caveman = options.caveman
        self._civs = civs
        self._scenarios = list(scenarios)
        self._trainable = {unit for civ in civs.included for unit in CIV_TO_UNITS[civ]}
        if Age2UnitData.VILLAGER_MALE in self._trainable:
            self._trainable.add(Age2UnitData.VILLAGER_FEMALE)
        self._granted = {grant
                         for scenario in self._scenarios
                         for grant in scenario.startup_units + scenario.trigger_units}


    def is_villager(self, unit: Age2UnitData) -> bool:
        return unit.line in VILLAGER_LINES


    def is_unit_type_included(self, unit: Age2UnitData) -> bool:
        wanted = UNIT_TYPE_TO_OPTIONS.get(unit.unit_type)
        return wanted is None or self._include_unique_units in wanted


    def is_trainable_unit(self, unit: Age2UnitData) -> bool:
        return unit in self._trainable

    def civ_trains(self, civ: Age2CivData, unit: Age2UnitData) -> bool:
        return unit in CIV_TO_UNITS[civ]

    def includes(self, unit: Age2UnitData) -> bool:
        if self._unitsanity == Unitsanity.option_none:
            return False
        if self.is_villager(unit) or unit in UNTRAINABLE:
            return False
        if unit not in self._trainable:
            if self._unitsanity != Unitsanity.option_all or unit not in self._granted:
                return False
        return self.is_unit_type_included(unit)


    def includes_line(self, line: Age2UnitLineData) -> bool:
        return any(self.includes(unit) for unit in line.units)


    def is_trainable(self, line: Age2UnitLineData) -> bool:
        return any(unit in self._trainable for unit in line.units)


    @property
    def lines(self) -> list[Age2UnitLineData]:
        return [line for line in Age2UnitLineData if self.includes_line(line)]


    @property
    def units(self) -> list[Age2UnitData]:
        return [unit for unit in Age2UnitData if self.includes(unit)]


    @property
    def heroes(self) -> list[Age2HeroData]:
        if self._unitsanity != Unitsanity.option_all:
            return []
        return [hero for hero in Age2HeroData if hero in self._granted]


    @property
    def escorts(self) -> list[Age2EscortUnitData]:
        if self._unitsanity != Unitsanity.option_all:
            return []
        return [escort for escort in Age2EscortUnitData if escort in self._granted]

    @property
    def special_units(self) -> list[Age2HeroData | Age2EscortUnitData]:
        return self.heroes + self.escorts


    @property
    def villager_locations(self) -> list[UnitLocation]:
        if self._shuffle_villager == ShuffleVillager.option_no:
            return []
        if self._shuffle_villager != ShuffleVillager.option_include_professions:
            return list(VILLAGER_LINES)
        return [Age2UnitData.VILLAGER_MALE, Age2UnitData.VILLAGER_FEMALE] + [job for job in Age2VillagerJobData if self.job_possible(job)]

    def job_possible(self, job: Age2VillagerJobData) -> bool:
        if job.building is not None and not self._civs.builds(job.building):
            return False
        scenarios = JOB_TO_SCENARIOS.get(job.job_name)
        if scenarios is None:
            return True
        return any(scenario in scenarios for scenario in self._scenarios)

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
            for line in VILLAGER_LINES:
                mine = [place for place in villager if self.villager_line_of(place) is line]
                if mine:
                    grouped[line] = mine
        return grouped


    def mercenary_exclusive_location(self, unit: Age2UnitData) -> bool:
        for line, locations in self.line_locations.items():
            if unit in locations or (unit.line is line and line in locations):
                return True
        return False

    def root_unit_data(self, location: UnitLocation) -> Age2UnitData:
        if isinstance(location, Age2VillagerJobData) or self.is_villager_location(location):
            return Age2UnitData.VILLAGER_MALE
        if isinstance(location, Age2UnitLineData):
            return location.head
        return location


    def villager_line_of(self, place: UnitLocation) -> Age2UnitLineData:
        if isinstance(place, Age2UnitLineData):
            return place
        if isinstance(place, Age2VillagerJobData):
            return place.line
        if place is Age2UnitData.VILLAGER_FEMALE:
            return Age2UnitLineData.VILLAGER_FEMALE_LINE
        return Age2UnitLineData.VILLAGER_MALE_LINE

    def is_villager_location(self, location: UnitLocation) -> bool:
        """Anything Shuffle Villager owns, whichever granularity produced it."""
        if isinstance(location, Age2VillagerJobData):
            return True
        if isinstance(location, Age2HeroData):
            return False
        if isinstance(location, Age2UnitLineData):
            return location in VILLAGER_LINES
        return self.is_villager(location)


    def startup_grants(self, scenario: Age2ScenarioData, target: UnitLocation) -> bool:
        if isinstance(target, Age2UnitLineData):
            return any(isinstance(grant, Age2UnitData) and grant.line is target
                       for grant in scenario.startup_units)
        return target in scenario.startup_units


    def trigger_grants(self, scenario: Age2ScenarioData, target: UnitLocation) -> bool:
        if isinstance(target, Age2UnitLineData):
            return any(isinstance(grant, Age2UnitData) and grant.line is target
                       for grant in scenario.trigger_units)
        return target in scenario.trigger_units


    def items(self, lines: Iterable[Age2UnitLineData], units: Iterable[Age2UnitData],
              buildings: Iterable[Age2BuildingData], villager: bool) -> list[Age2ItemData]:
        chosen: list[Age2ItemData]
        if self._unitsanity_items == UnitsanityItems.option_unit_line:
            chosen = [line.item for line in lines
                      if self.is_trainable(line) or self._caveman]
        elif self._unitsanity_items == UnitsanityItems.option_upgrades:
            heads_only = not upgrade_techs_shuffled(self._techsanity)
            wanted = {token for unit in units if unit.tier == 0 or not heads_only
                      for token in unit.upgrade_tokens}
            chosen = [token for token in Age2ItemData if token in wanted]
        else:
            producers = set(buildings)
            chosen = [BUILDING_TO_UNITS_ITEM[building] for building in Age2BuildingData
                      if building in producers]
        if villager:
            chosen.append(Age2UnitLineData.VILLAGER_MALE_LINE.item)
        if self._shuffle_villager == ShuffleVillager.option_include_professions:
            for job in Age2VillagerJobData:
                if self.job_possible(job) and job.item not in chosen:
                    chosen.append(job.item)
        return chosen
